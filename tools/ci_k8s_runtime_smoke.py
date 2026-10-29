#!/usr/bin/env python3
"""Opt-in real single-node KIND rollout with PostgreSQL 18 and two live API pods.

This intentionally proves ONLY a disposable, single-node Kubernetes runtime:
no ingress controller, independent worker nodes, external RWX driver, service
SLO, real offsite DR, ClamAV or rootless Podman certification. The hostPath
RWX backing is CI-ONLY and MUST NEVER be used as production storage.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from k8s_wizard import DEFAULTS, generate, validate

NAMESPACE = 'quorivio-runtime'
APP = 'quorivio-runtime'
CLUSTER = 'quorivio-runtime'
IMAGE = 'quorivio:kind-runtime'
PVC_CLASS = 'quorivio-ci-hostpath'  # Single-node disposable CI ONLY
PV_NAME = 'quorivio-ci-rwx-volume'


def cmd(*argv: str, timeout: int = 120, include_output: bool = False) -> str:
    """Never display Kubernetes or secret manifests on errors."""
    result = subprocess.run(list(argv), text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'CI Kubernetes runtime command failed: {argv[0]} (exit {result.returncode}; output redacted)')
    return result.stdout if include_output else ''


def pod_names() -> list[str]:
    raw = cmd('kubectl', '-n', NAMESPACE, 'get', 'pods', '-l', f'app={APP}',
              '-o', 'json', include_output=True)
    payload = json.loads(raw)
    return sorted(item['metadata']['name'] for item in payload['items']
                  if item.get('metadata', {}).get('deletionTimestamp') is None)


def service_probe(source_pod: str, path: str) -> None:
    """Probe the REAL ClusterIP service from a running non-root API container."""
    if path not in ('/api/health/ready', '/api/health/live', '/'):
        raise ValueError('Unexpected CI probe path')
    url = f'http://{APP}.{NAMESPACE}.svc.cluster.local{path}'
    script = ("fetch(process.argv[1],{signal:AbortSignal.timeout(8000)})"
              ".then(async r=>{if(!r.ok)throw Error('HTTP status '+r.status);"
              "const s=await r.text();if(!s.trim())throw Error('empty body')})"
              ".catch(()=>process.exit(17))")
    cmd('kubectl','-n',NAMESPACE,'exec',source_pod,'--','node','-e',script,url,timeout=25)


def shared_volume_probe(writer_pod: str, reader_pod: str) -> None:
    """Prove both API pods actually see the same disposable asset mount."""
    path='/app/assets/.quorivio-ci-rwx-probe'
    writer=("const f=require('node:fs');"
            "f.writeFileSync(process.argv[1],'ci-shared-asset', {flag:'wx', mode:0o600})")
    reader=("const f=require('node:fs');"
            "if(f.readFileSync(process.argv[1],'utf8')!=='ci-shared-asset')process.exit(19)")
    cleanup="require('node:fs').unlinkSync(process.argv[1])"
    cmd('kubectl','-n',NAMESPACE,'exec',writer_pod,'--','node','-e',writer,path,timeout=25)
    try:
        cmd('kubectl','-n',NAMESPACE,'exec',reader_pod,'--','node','-e',reader,path,timeout=25)
    finally:
        cmd('kubectl','-n',NAMESPACE,'exec',writer_pod,'--','node','-e',cleanup,path,timeout=25)


def ensure_clean_cluster() -> None:
    # A unique ephemeral namespace and PV avoid altering any pre-existing app.
    # Never attempt this outside the disposable cluster identified by name.
    current = cmd('kubectl','config','current-context',include_output=True).strip()
    if current != f'kind-{CLUSTER}':
        raise RuntimeError('Refusing runtime test outside disposable KIND cluster')
    cmd('kubectl', 'create', 'namespace', NAMESPACE)
    cmd('docker', 'exec', f'{CLUSTER}-control-plane', 'sh', '-c',
        'mkdir -p /var/local/quorivio-ci-rwx && chmod 0777 /var/local/quorivio-ci-rwx')


def write_private_pv(directory: Path) -> Path:
    # Single-node hostPath RWX only. This does not represent a real multi-node
    # CSI driver or satisfy the production RWX acceptance gate.
    path=directory/'ci-hostpath-pv.json'
    manifest={
        'apiVersion':'v1','kind':'PersistentVolume',
        'metadata':{'name':PV_NAME},
        'spec':{'capacity':{'storage':'10Gi'},'accessModes':['ReadWriteMany'],
                'persistentVolumeReclaimPolicy':'Retain',
                'storageClassName':PVC_CLASS,
                'hostPath':{'path':'/var/local/quorivio-ci-rwx','type':'Directory'}},
    }
    path.write_text(json.dumps(manifest,sort_keys=True)+'\n')
    return path


def main() -> None:
    ensure_clean_cluster()
    with tempfile.TemporaryDirectory(prefix='quorivio-kind-runtime-') as d:
        directory=Path(d)
        class_path=directory/'ci-storage-class.json'
        class_path.write_text(json.dumps({
            'apiVersion':'storage.k8s.io/v1','kind':'StorageClass',
            'metadata':{'name':PVC_CLASS},
            'provisioner':'kubernetes.io/no-provisioner',
            'volumeBindingMode':'Immediate',
            'reclaimPolicy':'Retain'},sort_keys=True)+'\n')
        cmd('kubectl','apply','-f',str(class_path))
        path=write_private_pv(directory)
        cmd('kubectl','apply','-f',str(path))
        output=directory/'manifest'
        cfg=validate({**DEFAULTS,'namespace':NAMESPACE,'name':APP,
                      'image':IMAGE,'postgres_image':'postgres:18-alpine',
                      'host':'quorivio.example.invalid','replicas':2,
                      'asset_access_mode':'ReadWriteMany',
                      'asset_storage_class':PVC_CLASS,
                      'postgres_sslmode':'require',
                      'tls_termination':False})
        generate(cfg,output)
        # Never print generated Kubernetes Secret or overrides file contents.
        cmd('kubectl','apply','-k',str(output),timeout=90)
        cmd('kubectl','-n',NAMESPACE,'rollout','status',f'statefulset/{APP}-postgres',
            '--timeout=280s',timeout=300)
        cmd('kubectl','-n',NAMESPACE,'rollout','status',f'deployment/{APP}',
            '--timeout=280s',timeout=300)
        pods=pod_names()
        if len(pods)!=2:
            raise RuntimeError('Expected exactly two available API pods')
        # A real service read from within a pod, not only YAML/schema checks.
        service_probe(pods[0],'/api/health/ready')
        service_probe(pods[0],'/api/health/live')
        service_probe(pods[1],'/')
        shared_volume_probe(pods[0],pods[1])
        print('PASS single-node KIND: 2 API pods, PostgreSQL 18, shared hostPath CI PVC and real ClusterIP HTTP probes')
        # Replacement should preserve healthy survivor and restore 2 replicas;
        # intentionally not a network partition or a multi-node HA assertion.
        survivor, victim = pods
        cmd('kubectl','-n',NAMESPACE,'delete','pod',victim,
            '--wait=false','--grace-period=25',timeout=60)
        # Endpoints removal is asynchronous after SIGTERM. A brief 503 during
        # voluntary drain is normal; use bounded retries, never skip the check.
        for attempt in range(24):
            try:
                service_probe(survivor,'/api/health/ready')
                break
            except RuntimeError:
                if attempt == 23:
                    raise RuntimeError('Surviving pod could not reach a ready service during replacement')
                time.sleep(1)
        cmd('kubectl','-n',NAMESPACE,'rollout','status',f'deployment/{APP}',
            '--timeout=220s',timeout=240)
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            replacement=pod_names()
            if len(replacement)==2 and victim not in replacement:
                break
            time.sleep(2)
        else:
            raise RuntimeError('Deployment did not return to two fresh pods')
        service_probe(replacement[0],'/api/health/ready')
        service_probe(replacement[1],'/api/health/ready')
        print('PASS single-node KIND: one pod replaced, peer remained ready, service recovered both endpoints')
    print('LIMIT: not production ingress, RWX CSI, multi-node quorum, storage fault, RTO/RPO or Podman acceptance')


if __name__=='__main__':
    try:
        main()
    except (RuntimeError, subprocess.TimeoutExpired, ValueError, KeyError) as exc:
        print('FAIL disposable Kubernetes runtime acceptance: '+str(exc),file=sys.stderr)
        sys.exit(1)
