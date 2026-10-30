#!/usr/bin/env python3
"""Read-only deployment HA evidence collector for *real* Kubernetes clusters.

Checks the live API, NOT whether a namespace merely contains generated YAML.
No secret contents, credentials, pod logs, or object dumps are printed or saved.
It cannot certify CSI data durability, actual network failover or RTO/RPO.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import ssl
import urllib.error
import urllib.request
from pathlib import Path

DNS = re.compile(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$')
HOST = re.compile(r'^[a-z0-9]([-a-z0-9.]*[a-z0-9])?$')


class EvidenceFailure(RuntimeError):
    pass


def kubectl(*args: str, timeout: int = 30) -> dict:
    try:
        cp = subprocess.run(['kubectl', *args], capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EvidenceFailure('Kubernetes API unavailable or query timed out') from exc
    if cp.returncode:
        # Kubernetes diagnostics may contain infrastructure paths/tokens: redact.
        raise EvidenceFailure('Kubernetes API query failed; diagnostics redacted')
    try:
        doc = json.loads(cp.stdout)
    except ValueError as exc:
        raise EvidenceFailure('Kubernetes returned invalid JSON') from exc
    if not isinstance(doc, dict):
        raise EvidenceFailure('Kubernetes did not return an object')
    return doc


def demand(value: bool, message: str) -> None:
    if not value:
        raise EvidenceFailure(message)


def check(data: dict[str, dict], *, app: str, service: str, ingress: str,
          host: str, ingress_class: str, replicas: int, require_tls: bool,
          pdb: str) -> dict:
    """Validate *provided* API responses (deterministic and unit-testable)."""
    deploy, pods, pvc, pv, pd, ing, svc, endpoints = (
        data[k] for k in ('deployment', 'pods', 'pvc', 'pv', 'pdb', 'ingress', 'service', 'endpoints'))
    spec = deploy.get('spec', {})
    status = deploy.get('status', {})
    demand(spec.get('replicas') is not None and spec.get('replicas') >= replicas,
           'Deployment desired replicas below required minimum')
    demand(status.get('observedGeneration', 0) >= deploy.get('metadata', {}).get('generation', 1),
           'Deployment controller has not observed latest generation')
    demand(status.get('readyReplicas', 0) >= replicas and status.get('availableReplicas', 0) >= replicas,
           'Deployment replicas are not Ready and Available')
    strategy = spec.get('strategy', {})
    rolling = strategy.get('rollingUpdate', {})
    demand(strategy.get('type') == 'RollingUpdate' and str(rolling.get('maxUnavailable')) in ('0', '0%'),
           'Rolling update does not preserve currently available replicas')
    tpl = spec.get('template', {}).get('spec', {})
    spread = tpl.get('topologySpreadConstraints', [])
    demand(any(x.get('topologyKey') == 'kubernetes.io/hostname'
               and x.get('whenUnsatisfiable') == 'DoNotSchedule'
               and x.get('minDomains', 0) >= 2 for x in spread),
           'Strict cross-node scheduling not configured')
    demand(tpl.get('terminationGracePeriodSeconds', 0) >= 30,
           'Termination grace period below HA minimum')

    pod_items = pods.get('items', [])
    ready = [p for p in pod_items
             if not p.get('metadata', {}).get('deletionTimestamp')
             and any(c.get('type') == 'Ready' and c.get('status') == 'True'
                     for c in p.get('status', {}).get('conditions', []))]
    nodes = [p.get('spec', {}).get('nodeName') for p in ready]
    demand(len(ready) >= replicas and all(nodes) and len(set(nodes)) >= 2,
           'Ready API replicas not spread across two distinct nodes')

    volumes = tpl.get('volumes', [])
    claims = [v['persistentVolumeClaim'].get('claimName') for v in volumes
              if 'persistentVolumeClaim' in v]
    claim = pvc.get('metadata', {}).get('name')
    demand(claim in claims and pvc.get('status', {}).get('phase') == 'Bound'
           and 'ReadWriteMany' in pvc.get('spec', {}).get('accessModes', []),
           'Application assets do not use a Bound RWX claim')
    demand(pvc.get('spec', {}).get('volumeName') == pv.get('metadata', {}).get('name'),
           'PVC/PV binding inconsistent')
    pv_spec = pv.get('spec', {})
    demand('ReadWriteMany' in pv_spec.get('accessModes', []), 'PV lacks RWX access')
    # hostPath/local are not networked storage even when declared RWX.
    demand(not any(k in pv_spec for k in ('hostPath', 'local')),
           'HostPath/local volume is not independent networked shared storage')
    driver = 'csi' if pv_spec.get('csi', {}).get('driver') else ('nfs' if pv_spec.get('nfs') else ('cephfs' if pv_spec.get('cephfs') else ''))
    demand(bool(driver), 'Unknown storage backend: independent RWX proof required')

    pdb_spec = pd.get('spec', {})
    pdb_status = pd.get('status', {})
    labels = spec.get('selector', {}).get('matchLabels', {})
    demand(labels and all(pdb_spec.get('selector', {}).get('matchLabels', {}).get(k) == v
                          for k, v in labels.items()), 'PDB does not select application pods')
    demand(pdb_status.get('currentHealthy', 0) >= replicas and pdb_status.get('disruptionsAllowed', 0) >= 1,
           'PDB cannot currently tolerate a voluntary eviction')
    demand(pd.get('metadata', {}).get('name') == pdb, 'Unexpected PDB object')

    svc_spec = svc.get('spec', {})
    demand(all(svc_spec.get('selector', {}).get(k) == v for k, v in labels.items()),
           'Service does not select application pods')
    endpoint_nodes = set()
    for item in endpoints.get('items', []):
        if item.get('metadata', {}).get('labels', {}).get('kubernetes.io/service-name') != service:
            continue
        for ep in item.get('endpoints', []):
            if ep.get('conditions', {}).get('ready') is True:
                if ep.get('nodeName'):
                    endpoint_nodes.add(ep['nodeName'])
    demand(len(endpoint_nodes) >= 2, 'Service lacks live Ready endpoints on two nodes')

    ing_spec = ing.get('spec', {})
    demand(ing_spec.get('ingressClassName') == ingress_class, 'Unexpected ingress class')
    paths = [p for rule in ing_spec.get('rules', []) if rule.get('host') == host
             for p in rule.get('http', {}).get('paths', [])]
    demand(any(p.get('path') == '/' and p.get('pathType') == 'Prefix'
               and p.get('backend', {}).get('service', {}).get('name') == service
               for p in paths), 'Ingress Host/path not routed to expected Service')
    if require_tls:
        demand(any(host in t.get('hosts', []) for t in ing_spec.get('tls', [])),
               'Ingress TLS host configuration missing')
    # This receipt has intentionally no external URL or mutable API data.
    return {'status': 'API_CONTRACT_PASS', 'replicas_ready': len(ready),
            'distinct_ready_nodes': len(set(nodes)), 'endpoint_nodes': len(endpoint_nodes),
            'rwx_backend_type': driver, 'pdb_disruption_allowed': True,
            'tls_configured': bool(ing_spec.get('tls')),
            'limitations': ['No actual ingress HTTP/TLS probe',
                            'No CSI data durability/failure injection',
                            'No database HA/ClamAV load verification',
                            'No RTO/RPO or security/operator certification']}


def collect(*, namespace: str, app: str, service: str, ingress: str,
            host: str, ingress_class: str, replicas: int, require_tls: bool,
            pdb: str, context: str) -> dict:
    demand(all(DNS.fullmatch(x) for x in (namespace, app, service, ingress, pdb, ingress_class)),
           'Kubernetes resource name invalid')
    demand(bool(HOST.fullmatch(host)) and '.' in host, 'Host invalid')
    demand(2 <= replicas <= 20, 'Require 2 to 20 replicas')
    config = kubectl('config', 'view', '--minify', '-o', 'json')
    active = config.get('contexts', [{}])[0].get('name') if config.get('contexts') else None
    demand(context and context == active, 'Refusing unexpected Kubernetes context')
    def get(kind: str, name: str) -> dict:
        return kubectl('-n', namespace, 'get', kind, name, '-o', 'json')
    deploy = get('deployment', app)
    pod_selector = ','.join(f'{k}={v}' for k, v in sorted(deploy.get('spec', {}).get('selector', {}).get('matchLabels', {}).items()))
    demand(bool(pod_selector), 'Deployment selector missing')
    pods = kubectl('-n', namespace, 'get', 'pods', '-l', pod_selector, '-o', 'json')
    pvc_name = next((v['persistentVolumeClaim'].get('claimName') for v in
                     deploy.get('spec', {}).get('template', {}).get('spec', {}).get('volumes', [])
                     if 'persistentVolumeClaim' in v), None)
    demand(bool(pvc_name) and bool(DNS.fullmatch(pvc_name)), 'Application PVC absent')
    pvc = get('pvc', pvc_name)
    pv_name = pvc.get('spec', {}).get('volumeName', '')
    demand(bool(pv_name) and bool(DNS.fullmatch(pv_name)), 'Application PVC is unbound')
    pv = kubectl('get', 'pv', pv_name, '-o', 'json')
    data = dict(deployment=deploy, pods=pods, pvc=pvc, pv=pv,
                pdb=get('pdb', pdb), ingress=get('ingress', ingress),
                service=get('service', service),
                endpoints=kubectl('-n', namespace, 'get', 'endpointslices',
                                  '-l', f'kubernetes.io/service-name={service}', '-o', 'json'))
    return check(data, app=app, service=service, ingress=ingress, host=host,
                 ingress_class=ingress_class, replicas=replicas, require_tls=require_tls, pdb=pdb)



def probe_public_ingress(host: str, *, require_tls: bool) -> dict:
    """Optional external probe; HTTPS uses normal certificate/hostname validation.

    Do not trust redirects to a login page or downgrade to insecure HTTP.
    This is not multi-node fault injection or a real load test.
    """
    demand(bool(HOST.fullmatch(host)) and '.' in host, 'Public ingress host invalid')
    scheme = 'https' if require_tls else 'http'
    url = f'{scheme}://{host}/api/health/ready'

    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, request, fp, code, message, headers, newurl):
            return None

    try:
        opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        request = urllib.request.Request(url, headers={'Accept': 'application/json'}, method='GET')
        with opener.open(request, timeout=8) as response:
            demand(response.status == 200, 'Public ingress readiness returned non-200 status')
            payload = response.read(4096)
            demand(bool(payload.strip()), 'Public ingress readiness returned an empty response')
    except (OSError, ValueError, urllib.error.HTTPError) as exc:
        # Never propagate URL, proxy env settings, certificate details, body or headers.
        raise EvidenceFailure('Public ingress probe failed; network details redacted') from exc
    return {'public_ingress_readiness': 'HTTP_200', 'transport': scheme,
            'certificate_hostname_validation': bool(require_tls)}

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('namespace', 'app', 'service', 'ingress', 'host', 'ingress-class', 'pdb', 'context'):
        parser.add_argument('--' + field, required=True)
    parser.add_argument('--replicas', type=int, default=2)
    parser.add_argument('--require-tls', action='store_true')
    parser.add_argument('--probe-external', action='store_true',
                        help='Also connect to the public readiness URL with normal TLS verification')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        report = collect(namespace=args.namespace, app=args.app, service=args.service,
                         ingress=args.ingress, host=args.host, ingress_class=args.ingress_class,
                         replicas=args.replicas, require_tls=args.require_tls,
                         pdb=args.pdb, context=args.context)
        if args.probe_external:
            report.update(probe_public_ingress(args.host, require_tls=args.require_tls))
    except (EvidenceFailure, KeyError, TypeError, IndexError) as exc:
        print('NOT ACCEPTED: ' + (str(exc) if isinstance(exc, EvidenceFailure) else 'Malformed Kubernetes API response'),
              file=sys.stderr)
        return 1
    output = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.output:
        if args.output.exists() or args.output.is_symlink():
            print('NOT ACCEPTED: refusing to overwrite existing evidence', file=sys.stderr)
            return 1
        try:
            with args.output.open('x', encoding='utf-8') as f:
                f.write(output)
        except OSError:
            print('NOT ACCEPTED: evidence file could not be created', file=sys.stderr)
            return 1
    print(output, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
