#!/usr/bin/env python3
"""Opt-in *live* Kubernetes multi-worker NGINX or HAProxy ingress smoke.

The two KIND worker nodes bind the SAME disposable runner host directory. This
proves pod scheduling, HTTP ingress, rolling replacement, and file visibility
across KIND workers. It does NOT prove NFS, a production CSI RWX driver,
independent physical machines, HA at the control plane, or SLA/SLO.
No production credentials, image push, host listener, or namespace is used.
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from k8s_wizard import DEFAULTS, generate, validate

CLUSTER = 'quorivio-multinode'
NS = CLUSTER
APP = 'quorivio-multi'
IMAGE = 'quorivio:kind-multinode'
PV = 'quorivio-multinode-ci-host-pv'
CLASS = 'quorivio-multinode-ci-host'
HOST = 'quorivio-multi.example.invalid'
NGINX_INGRESS = 'ingress-nginx-controller.ingress-nginx.svc.cluster.local'
HAPROXY_NAMESPACE = 'quorivio-ci-haproxy'
HAPROXY_RELEASE = 'quorivio-ci-haproxy'
TLS_SECRET = 'quorivio-ci-ingress-tls'
# Fixed upstream chart release; avoid following floating chart versions in CI.
HAPROXY_CHART_VERSION = '1.54.3'
# Version-pinned upstream KIND manifest, deployed only in a disposable cluster.
NGINX_MANIFEST = ('https://raw.githubusercontent.com/kubernetes/ingress-nginx/'
                  'controller-v1.12.1/deploy/static/provider/kind/deploy.yaml')


def run(*args: str, timeout: int = 120) -> str:
    """No output on error: kubectl may expose credentials in diagnostics."""
    process = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    if process.returncode:
        raise RuntimeError(f'Disposable Kubernetes check failed: {args[0]} (exit {process.returncode}; output redacted)')
    return process.stdout


def checked_context() -> None:
    if run('kubectl', 'config', 'current-context').strip() != f'kind-{CLUSTER}':
        raise RuntimeError('Refusing to operate outside the dedicated disposable KIND cluster')


def workers() -> list[str]:
    data = json.loads(run('kubectl', 'get', 'nodes', '-o', 'json'))
    names = sorted(x['metadata']['name'] for x in data['items']
                   if 'node-role.kubernetes.io/control-plane' not in x['metadata'].get('labels', {})
                   and 'node-role.kubernetes.io/master' not in x['metadata'].get('labels', {}))
    if len(names) != 2 or len(data['items']) != 3:
        raise RuntimeError('Expected precisely two independent KIND worker nodes and one control plane')
    return names


def pods() -> dict[str, str]:
    data = json.loads(run('kubectl', '-n', NS, 'get', 'pods', '-l', f'app={APP}', '-o', 'json'))
    return {item['metadata']['name']: item['spec'].get('nodeName', '')
            for item in data['items'] if not item['metadata'].get('deletionTimestamp')}


def assert_distribution(known_workers: list[str]) -> dict[str, str]:
    locations = pods()
    if len(locations) != 2 or set(locations.values()) != set(known_workers):
        raise RuntimeError('Two API replicas must remain on separate worker hosts')
    return locations


def node_script(source: str, script: str, *arguments: str) -> None:
    run('kubectl', '-n', NS, 'exec', source, '--', 'node', '-e', script, *arguments, timeout=35)


def ingress_http_source() -> str:
    """Node core HTTP request preserves the virtual-host Host header.

    Node's global fetch()/undici silently replaces the provided Host header
    with the upstream Service DNS name, causing genuine NGINX name-based
    routing checks to fail although the controller and backends are healthy.
    No response bodies or headers are written into CI logs.
    """
    return ("const http=require('node:http');"
            "const target=new URL(process.argv[1]);"
            "if(target.protocol!=='http:')process.exit(31);"
            "const expected=Number(process.argv[3]);"
            "const req=http.request(target,{method:'GET',headers:{Host:process.argv[2]},timeout:8000},res=>{"
            "if(res.statusCode!==expected){res.resume();process.exitCode=21;return}"
            "let bytes=0;res.on('data',part=>{bytes+=part.length;"
            "if(bytes>65536){req.destroy();process.exitCode=22}});"
            "res.on('end',()=>{if(expected===200&&bytes===0)process.exitCode=23});"
            "});"
            "req.on('timeout',()=>req.destroy());"
            "req.on('error',()=>{process.exitCode=24});req.end();")


def ingress_probe(source: str, path: str = '/api/health/ready', bad_host: bool = False, ingress: str = NGINX_INGRESS) -> None:
    if path not in ('/', '/api/health/live', '/api/health/ready'):
        raise ValueError('Unexpected HTTP probe path')
    # Reach the real ingress-nginx Service using the HTTP core client and an
    # explicit Host header; avoid fetch(), which rewrites it to Service DNS.
    target = f'http://{ingress}{path}'
    node_script(source, ingress_http_source(), target,
                'unknown.example.invalid' if bad_host else HOST,
                '404' if bad_host else '200')


def https_probe_source() -> str:
    """Trusted HTTPS/SNI and Host routing, with certificate verification ENABLED.

    The CA argument is a self-signed CI test certificate, never an auth token.
    A deliberately untrusted call must fail only with a trust-chain
    error; hostname mismatch, certificate expiry, timeouts and connection
    failures cannot produce a false PASS.
    """
    return ("const https=require('node:https');"
            "const target=new URL(process.argv[1]);"
            "if(target.protocol!=='https:'||target.pathname!=='/api/health/ready'&&target.pathname!=='/'&&target.pathname!=='/api/health/live')process.exit(31);"
            "const host=process.argv[2],expected=Number(process.argv[3]);"
            "const ca=Buffer.from(process.argv[4],'base64');"
            "const mode=process.argv[5];"
            "if(!['trusted','untrusted'].includes(mode)||!ca.length)process.exit(31);"
            "const req=https.request(target,{method:'GET',servername:process.argv[6],"
            "headers:{Host:host},ca:mode==='trusted'?ca:undefined,"
            "rejectUnauthorized:true,timeout:8000},res=>{"
            "if(mode==='untrusted'){res.resume();process.exitCode=43;return}"
            "if(res.statusCode!==expected){res.resume();process.exitCode=41;return}"
            "let bytes=0;res.on('data',part=>{bytes+=part.length;"
            "if(bytes>65536){req.destroy();process.exitCode=42}});"
            "res.on('end',()=>{if(expected===200&&bytes===0)process.exitCode=44});"
            "});"
            "req.on('timeout',()=>req.destroy(new Error('connection timeout')));"
            "req.on('error',err=>{"
            "if(mode==='untrusted'&&['DEPTH_ZERO_SELF_SIGNED_CERT','SELF_SIGNED_CERT_IN_CHAIN',"
            "'UNABLE_TO_VERIFY_LEAF_SIGNATURE','UNABLE_TO_GET_ISSUER_CERT_LOCALLY'].includes(err.code)){return}"
            "process.exitCode=45});req.end();")


def issue_ephemeral_https_cert(directory: Path) -> str:
    """Create a 1-day self-signed TLS identity inside a disposable test folder."""
    cert, key = directory/'quorivio-ci.crt', directory/'quorivio-ci.key'
    run('openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-sha256',
        '-nodes', '-days', '1', '-subj', f'/CN={HOST}',
        '-addext', f'subjectAltName=DNS:{HOST}',
        '-keyout', str(key), '-out', str(cert), timeout=25)
    key.chmod(0o600)
    # kubectl output remains captured/redacted. Never print key, Secret or PEM.
    run('kubectl', '-n', NS, 'create', 'secret', 'tls', TLS_SECRET,
        f'--cert={cert}', f'--key={key}', timeout=30)
    return base64.b64encode(cert.read_bytes()).decode('ascii')


def https_ingress_probe(source: str, *, ingress: str, certificate_b64: str,
                        path: str = '/api/health/ready', bad_host: bool = False,
                        untrusted: bool = False) -> None:
    if path not in ('/', '/api/health/ready', '/api/health/live'):
        raise ValueError('Unexpected HTTPS test path')
    if not certificate_b64 or not isinstance(certificate_b64, str):
        raise ValueError('A pinned disposable test CA is required')
    if not ingress.endswith(':443'):
        raise ValueError('An explicit HTTPS ingress Service port is required')
    node_script(source, https_probe_source(), f'https://{ingress}{path}',
                'unknown.example.invalid' if bad_host else HOST,
                '404' if bad_host else '200', certificate_b64,
                'untrusted' if untrusted else 'trusted', HOST)


def shared_mount_check(source: str, destination: str) -> None:
    if source == destination:
        raise ValueError('Two distinct API replicas required')
    pathname = '/app/assets/.ci-multinode-shared'
    write = ("const fs=require('node:fs');"
             "fs.writeFileSync(process.argv[1],'kind-multi-worker-shared',"
             "{flag:'wx',mode:0o600})")
    read = ("const fs=require('node:fs');"
            "if(fs.readFileSync(process.argv[1],'utf8')!=='kind-multi-worker-shared')process.exit(24)")
    remove = "require('node:fs').unlinkSync(process.argv[1])"
    node_script(source, write, pathname)
    try:
        node_script(destination, read, pathname)
    finally:
        node_script(source, remove, pathname)


def write_pv(path: Path) -> Path:
    resource = {'apiVersion': 'v1', 'kind': 'PersistentVolume',
                'metadata': {'name': PV},
                'spec': {'capacity': {'storage': '10Gi'},
                         'accessModes': ['ReadWriteMany'],
                         'persistentVolumeReclaimPolicy': 'Retain',
                         'storageClassName': CLASS,
                         'hostPath': {'path': '/var/local/quorivio-ci-rwx',
                                      'type': 'Directory'}}}
    path.write_text(json.dumps(resource, sort_keys=True) + '\n', encoding='utf-8')
    return path


def haproxy_ingress_service(port_number: int = 80) -> str:
    """Find the actual chart-created private HTTP Service by label and port.

    Neither a guessed Helm resource name nor the runner's host networking is
    an acceptable ingress proof; the probe runs inside an application pod.
    """
    data = json.loads(run('kubectl', '-n', HAPROXY_NAMESPACE, 'get', 'services',
                          '-l', f'app.kubernetes.io/instance={HAPROXY_RELEASE}', '-o', 'json'))
    matches = []
    for item in data['items']:
        if item['spec'].get('type') == 'ExternalName':
            continue
        if item['spec'].get('clusterIP') in (None, 'None'):
            continue
        for port in item['spec'].get('ports', []):
            if port.get('port') == port_number and port.get('protocol', 'TCP') == 'TCP':
                matches.append((item['metadata']['name'], port['port']))
    if len(matches) != 1:
        raise RuntimeError('Expected exactly one private HAProxy HTTP ingress Service')
    return f'{matches[0][0]}.{HAPROXY_NAMESPACE}.svc.cluster.local:{matches[0][1]}'


def install_ingress(controller: str) -> str:
    if controller == 'nginx':
        run('kubectl', 'apply', '-f', NGINX_MANIFEST, timeout=120)
        run('kubectl', '-n', 'ingress-nginx', 'rollout', 'status',
            'deployment/ingress-nginx-controller', '--timeout=300s', timeout=330)
        return NGINX_INGRESS
    if controller != 'haproxytech':
        raise ValueError('Unsupported disposable ingress controller')
    # Chart is pinned, the service is ClusterIP, no external listener or secret.
    run('helm', 'upgrade', '--install', HAPROXY_RELEASE,
        'oci://ghcr.io/haproxytech/helm-charts/kubernetes-ingress',
        '--version', HAPROXY_CHART_VERSION, '--namespace', HAPROXY_NAMESPACE,
        '--create-namespace', '--set', 'controller.replicaCount=1',
        '--set', 'controller.service.type=ClusterIP',
        '--set', 'controller.ingressClass=haproxy',
        '--wait', '--timeout', '300s', timeout=360)
    cls = json.loads(run('kubectl', 'get', 'ingressclass', 'haproxy', '-o', 'json'))
    if cls['metadata']['name'] != 'haproxy':
        raise RuntimeError('Official HAProxy ingress class missing')
    return haproxy_ingress_service()


def main(controller: str = 'nginx', *, https: bool = False) -> None:
    if controller not in ('nginx', 'haproxytech'):
        raise ValueError('Unknown ingress controller')
    checked_context()
    ws = workers()
    for node in ws:
        run('kubectl', 'label', 'node', node, 'quorivio-ci-worker=yes', '--overwrite')
    # The runner creates the bind-mounted directory before KIND node creation.
    # Never use this class outside ephemeral KIND: hostPath is NOT network RWX.
    with tempfile.TemporaryDirectory(prefix='quorivio-multinode-') as td:
        home = Path(td)
        sc = home/'storage-class.json'
        sc.write_text(json.dumps({'apiVersion': 'storage.k8s.io/v1', 'kind': 'StorageClass',
                                  'metadata': {'name': CLASS},
                                  'provisioner': 'kubernetes.io/no-provisioner',
                                  'volumeBindingMode': 'Immediate'}, sort_keys=True) + '\n')
        run('kubectl', 'apply', '-f', str(sc))
        run('kubectl', 'apply', '-f', str(write_pv(home/'pv.json')))
        config = validate({**DEFAULTS,
                           'name': APP, 'namespace': NS, 'image': IMAGE,
                           'postgres_image': 'postgres:18-alpine',
                           'replicas': 2, 'enforce_node_diversity': True,
                           'asset_access_mode': 'ReadWriteMany',
                           'asset_storage_class': CLASS,
                           'app_node_selector': 'quorivio-ci-worker=yes',
                           'host': HOST, 'tls_termination': https,
                           'tls_secret': TLS_SECRET if https else '',
                           'ingress_controller': 'haproxy' if controller == 'haproxytech' else 'nginx',
                           'haproxy_variant': 'haproxytech' if controller == 'haproxytech' else 'community',
                           'antivirus_mode': 'external', 'antivirus_host': 'clamav-ci-unavailable.invalid'})
        manifest_path = home/'kustomize'
        generate(config, manifest_path)
        # The generated app Public URL must agree with actual edge TLS mode.
        configmap = (manifest_path/'10-configmap.yaml').read_text()
        scheme = 'https' if https else 'http'
        if f'PUBLIC_BASE_URL: "{scheme}://{HOST}"' not in configmap:
            raise RuntimeError('Generated public origin and ingress TLS disagree')
        if https:
            ingress_spec = (manifest_path/'40-ingress.yaml').read_text()
            if f'secretName: {TLS_SECRET}' not in ingress_spec:
                raise RuntimeError('Generated TLS ingress secret reference missing')
            # Namespace must exist before creating the disposable TLS Secret.
            run('kubectl', 'create', 'namespace', NS, timeout=30)
            certificate_b64 = issue_ephemeral_https_cert(home)
        else:
            certificate_b64 = ''
        run('kubectl', 'apply', '-k', str(manifest_path), timeout=120)
        run('kubectl', '-n', NS, 'rollout', 'status', f'statefulset/{APP}-postgres',
            '--timeout=280s', timeout=310)
        run('kubectl', '-n', NS, 'rollout', 'status', f'deployment/{APP}',
            '--timeout=280s', timeout=310)
        locations = assert_distribution(ws)
        first, second = sorted(locations)
        shared_mount_check(first, second)
        print('PASS KIND multiworker: PostgreSQL 18, strict separate-node scheduling and cross-node asset visibility (runner shared bind, not CSI)', flush=True)

        # Use the real isolated controller, not a hand-written mock endpoint.
        ingress = install_ingress(controller)
        secure_ingress = (haproxy_ingress_service(443) if controller == 'haproxytech'
                          else f'{NGINX_INGRESS}:443') if https else ''
        # Admission webhook reconciles separately from controller readiness.
        # Retry actual requests rather than trusting a controller ready count.
        for attempt in range(30):
            try:
                if https:
                    https_ingress_probe(first, ingress=secure_ingress, certificate_b64=certificate_b64)
                    https_ingress_probe(second, path='/', ingress=secure_ingress, certificate_b64=certificate_b64)
                    https_ingress_probe(first, ingress=secure_ingress, certificate_b64=certificate_b64,
                                        bad_host=True)
                    https_ingress_probe(first, ingress=secure_ingress, certificate_b64=certificate_b64,
                                        untrusted=True)
                else:
                    ingress_probe(first, ingress=ingress)
                    ingress_probe(second, '/', ingress=ingress)
                    ingress_probe(first, bad_host=True, ingress=ingress)
                break
            except RuntimeError:
                if attempt == 29:
                    raise RuntimeError('Real ingress controller did not pass scoped host/TLS routing checks')
                time.sleep(2)
        if https:
            print(f'PASS KIND {controller.upper()}: verified TLS/SNI from both pod clients, pinned certificate, untrusted chain rejected, bad Host rejected', flush=True)
        else:
            print(f'PASS KIND {controller.upper()}: real HTTP ingress host routing, nonmatching host rejection and both API origins', flush=True)

        # Delete one API pod while a separate node still serves through ingress.
        run('kubectl', '-n', NS, 'delete', 'pod', second, '--wait=false',
            '--grace-period=25', timeout=50)
        for attempt in range(30):
            try:
                if https:
                    https_ingress_probe(first, path='/api/health/ready', ingress=secure_ingress,
                                        certificate_b64=certificate_b64)
                else:
                    ingress_probe(first, '/api/health/ready', ingress=ingress)
                break
            except RuntimeError:
                if attempt == 29:
                    raise RuntimeError('Ingress failed to reach the surviving API replica')
                time.sleep(2)
        run('kubectl', '-n', NS, 'rollout', 'status', f'deployment/{APP}',
            '--timeout=240s', timeout=270)
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            refreshed = pods()
            if len(refreshed) == 2 and second not in refreshed:
                assert_distribution(ws)
                # Re-probe ingress and cross-worker mount after replacement.
                if https:
                    https_ingress_probe(first, path='/api/health/live', ingress=secure_ingress,
                                        certificate_b64=certificate_b64)
                else:
                    ingress_probe(first, '/api/health/live', ingress=ingress)
                shared_mount_check(*sorted(refreshed))
                break
            time.sleep(2)
        else:
            raise RuntimeError('No safe cross-worker replacement was observed')
        print('PASS KIND multiworker: ingress available through pod replacement, two independent worker placements restored', flush=True)
    print('LIMIT: test uses one Docker host and shared bind; not multi-machine NFS/CSI, publicly trusted TLS, native ARM64, production SLA or operator sign-off')


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--controller', choices=('nginx', 'haproxytech'), default='nginx')
        parser.add_argument('--tls', action='store_true',
                            help='Use a private, self-signed CI TLS certificate and verify real HTTPS (no public CA)')
        arguments = parser.parse_args()
        main(arguments.controller, https=arguments.tls)
    except (RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL disposable multiworker/ingress acceptance: {exc}', file=sys.stderr)
        sys.exit(1)
