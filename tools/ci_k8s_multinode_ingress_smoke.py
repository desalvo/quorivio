#!/usr/bin/env python3
"""Opt-in *live* Kubernetes multi-worker and NGINX ingress smoke.

The two KIND worker nodes bind the SAME disposable runner host directory. This
proves pod scheduling, HTTP ingress, rolling replacement, and file visibility
across KIND workers. It does NOT prove NFS, a production CSI RWX driver,
independent physical machines, HAProxy, HA at the control plane, or SLA/SLO.
No production credentials, image push, host listener, or namespace is used.
"""
from __future__ import annotations

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
INGRESS = 'ingress-nginx-controller.ingress-nginx.svc.cluster.local'
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


def ingress_probe(source: str, path: str = '/api/health/ready', bad_host: bool = False) -> None:
    if path not in ('/', '/api/health/live', '/api/health/ready'):
        raise ValueError('Unexpected HTTP probe path')
    # Reach the real ingress-nginx Service using the HTTP core client and an
    # explicit Host header; avoid fetch(), which rewrites it to Service DNS.
    target = f'http://{INGRESS}{path}'
    node_script(source, ingress_http_source(), target,
                'unknown.example.invalid' if bad_host else HOST,
                '404' if bad_host else '200')


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


def main() -> None:
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
                           'host': HOST, 'tls_termination': False,
                           'antivirus_mode': 'external', 'antivirus_host': 'clamav-ci-unavailable.invalid'})
        manifest_path = home/'kustomize'
        generate(config, manifest_path)
        # The generated Ingress is HTTP-only by design; no TLS secret or
        # certificates are ever generated for this ephemeral ingress scenario.
        configmap = (manifest_path/'10-configmap.yaml').read_text()
        if f'PUBLIC_BASE_URL: "http://{HOST}"' not in configmap:
            raise RuntimeError('The generated public origin is not HTTP for a non-TLS ingress')
        run('kubectl', 'apply', '-k', str(manifest_path), timeout=120)
        run('kubectl', '-n', NS, 'rollout', 'status', f'statefulset/{APP}-postgres',
            '--timeout=280s', timeout=310)
        run('kubectl', '-n', NS, 'rollout', 'status', f'deployment/{APP}',
            '--timeout=280s', timeout=310)
        locations = assert_distribution(ws)
        first, second = sorted(locations)
        shared_mount_check(first, second)
        print('PASS KIND multiworker: PostgreSQL 18, strict separate-node scheduling and cross-node asset visibility (runner shared bind, not CSI)', flush=True)

        # Opt-in actual NGINX ingress controller (upstream version pinned).
        run('kubectl', 'apply', '-f', NGINX_MANIFEST, timeout=120)
        run('kubectl', '-n', 'ingress-nginx', 'rollout', 'status',
            'deployment/ingress-nginx-controller', '--timeout=300s', timeout=330)
        # Admission webhook reconciles separately from controller readiness.
        # Retry actual edge requests rather than trusting a deployment's ready count.
        for attempt in range(30):
            try:
                ingress_probe(first)
                ingress_probe(second, '/')
                ingress_probe(first, bad_host=True)
                break
            except RuntimeError:
                if attempt == 29:
                    raise RuntimeError('Real ingress controller did not route the configured host')
                time.sleep(2)
        print('PASS KIND NGINX: real HTTP ingress host routing, nonmatching host rejection and both API origins', flush=True)

        # Delete one API pod while a separate node still serves through ingress.
        run('kubectl', '-n', NS, 'delete', 'pod', second, '--wait=false',
            '--grace-period=25', timeout=50)
        for attempt in range(30):
            try:
                ingress_probe(first, '/api/health/ready')
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
                ingress_probe(first, '/api/health/live')
                shared_mount_check(*sorted(refreshed))
                break
            time.sleep(2)
        else:
            raise RuntimeError('No safe cross-worker replacement was observed')
        print('PASS KIND multiworker: ingress available through pod replacement, two independent worker placements restored', flush=True)
    print('LIMIT: test uses one Docker host and shared bind; not multi-machine NFS/CSI, HAProxy, native ARM64, TLS certificate, production SLA or operator sign-off')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired) as exc:
        print(f'FAIL disposable multiworker/ingress acceptance: {exc}', file=sys.stderr)
        sys.exit(1)
