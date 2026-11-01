#!/usr/bin/env python3
"""Explicit opt-in real Kubernetes RWX data-path evidence (not an HA/SLA certificate).

Read-only by default. Never fetches Secret values, prints pod responses, or changes
workloads; --confirm-write creates and deletes two unique, small files under the
application's mounted asset directory. The caller must select the exact context.
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
from pathlib import PurePosixPath

DNS = re.compile(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$')
LABEL_KEY = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._/-]{0,251}[A-Za-z0-9]$|^[A-Za-z0-9]$')
LABEL_VALUE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,61}[A-Za-z0-9]$|^[A-Za-z0-9]$')


class ProbeError(Exception):
    pass


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ProbeError(reason)


def run(command: list[str], *, stdin: str | None = None, timeout: int = 30) -> str:
    try:
        completed = subprocess.run(command, input=stdin, capture_output=True, text=True,
                                   check=False, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProbeError('Kubernetes command unavailable or timed out; details redacted') from exc
    if completed.returncode:
        raise ProbeError('Kubernetes command failed; details redacted')
    return completed.stdout


def read_json(command: list[str], *, runner=run) -> dict:
    try:
        doc = json.loads(runner(command))
    except (ValueError, TypeError) as exc:
        raise ProbeError('Invalid Kubernetes API JSON') from exc
    require(isinstance(doc, dict), 'Kubernetes API did not return a JSON object')
    return doc


def validate_mount(path: str) -> str:
    require(isinstance(path, str) and path.startswith('/') and '\x00' not in path,
            'Absolute asset mount path required')
    parts = PurePosixPath(path).parts
    require('..' not in path.split('/') and len(parts) > 2 and path not in ('/', '/app'),
            'Asset mount path must be a non-root directory without traversal')
    require(path == str(PurePosixPath(path)) and len(path) <= 250,
            'Asset mount path is not normalized')
    return path


def assess(deployment: dict, pods: dict, pvc: dict, pv: dict, *, mount: str) -> dict:
    """Classify objects without false claims about durability or independent hardware."""
    mount = validate_mount(mount)
    spec = deployment.get('spec', {})
    desired = spec.get('replicas', 0)
    require(isinstance(desired, int) and desired >= 2, 'Deployment must request at least two replicas')
    status = deployment.get('status', {})
    require(status.get('observedGeneration', 0) >= deployment.get('metadata', {}).get('generation', 1)
            and status.get('readyReplicas', 0) >= 2, 'Deployment has not converged to two ready replicas')
    selector = spec.get('selector', {}).get('matchLabels', {})
    require(isinstance(selector, dict) and selector and all(
        isinstance(k, str) and isinstance(v, str) and k and v for k, v in selector.items()),
        'Deployment has no stable pod label selector')
    claim = pvc.get('metadata', {}).get('name')
    require(isinstance(claim, str) and DNS.fullmatch(claim) is not None,
            'PVC name is invalid')
    require(pvc.get('status', {}).get('phase') == 'Bound'
            and 'ReadWriteMany' in pvc.get('spec', {}).get('accessModes', []),
            'PVC must be Bound and declare ReadWriteMany')
    require(pvc.get('spec', {}).get('volumeName') == pv.get('metadata', {}).get('name'),
            'PVC/PV binding mismatch')
    pv_spec = pv.get('spec', {})
    require('ReadWriteMany' in pv_spec.get('accessModes', []), 'PV does not declare RWX')
    require('hostPath' not in pv_spec and 'local' not in pv_spec,
            'hostPath/local are not independently shared network storage')
    backend = 'csi' if pv_spec.get('csi', {}).get('driver') else 'nfs' if pv_spec.get('nfs') else 'cephfs' if pv_spec.get('cephfs') else None
    require(backend is not None, 'Unsupported or unverified persistent storage driver')
    tpl = spec.get('template', {}).get('spec', {})
    volumes = [v.get('name') for v in tpl.get('volumes', [])
               if v.get('persistentVolumeClaim', {}).get('claimName') == claim]
    require(len(volumes) == 1 and isinstance(volumes[0], str),
            'Exactly one mounted volume must reference the RWX claim')
    containers = [c.get('name') for c in tpl.get('containers', [])
                  if any(m.get('name') == volumes[0] and m.get('mountPath') == mount
                         and not m.get('readOnly', False) and not m.get('subPath')
                         and not m.get('subPathExpr') for m in c.get('volumeMounts', []))]
    require(len(containers) == 1 and isinstance(containers[0], str),
            'Exactly one application container must mount RWX path read-write without subPath')
    candidates = []
    for pod in pods.get('items', []):
        meta, pspec, pstatus = (pod.get('metadata', {}), pod.get('spec', {}), pod.get('status', {}))
        if meta.get('deletionTimestamp') or not all(meta.get('labels', {}).get(k) == v for k, v in selector.items()):
            continue
        if not any(c.get('type') == 'Ready' and c.get('status') == 'True' for c in pstatus.get('conditions', [])):
            continue
        node, name = pspec.get('nodeName'), meta.get('name')
        if not isinstance(name, str) or not DNS.fullmatch(name) or not node or not DNS.fullmatch(node):
            continue
        if not any(v.get('persistentVolumeClaim', {}).get('claimName') == claim
                   and v.get('name') == volumes[0] for v in pspec.get('volumes', [])):
            continue
        container = next((c for c in pspec.get('containers', []) if c.get('name') == containers[0]), None)
        if container is None or not any(m.get('name') == volumes[0] and m.get('mountPath') == mount
                                        and not m.get('readOnly', False) and not m.get('subPath')
                                        and not m.get('subPathExpr') for m in container.get('volumeMounts', [])):
            continue
        if not any(c.get('name') == containers[0] and c.get('ready') is True
                   for c in pstatus.get('containerStatuses', [])):
            continue
        candidates.append((node, name, containers[0]))
    candidates.sort()
    pair = next(((a, b) for a in candidates for b in candidates
                 if a[0] != b[0]), None)
    require(pair is not None, 'No two ready application pods with RWX mount on distinct Kubernetes nodes')
    return {'status': 'API_CONTRACT_PASS', 'backend': backend,
            'distinct_nodes': len({a[0] for a in candidates}), 'pod_pair': [pair[0][1], pair[1][1]],
            'container': containers[0], 'mount_path': mount,
            'limitations': ['Kubernetes nodes may be virtual machines on a single physical host',
                            'PVC/PV API declarations do not establish actual cross-node data transfer',
                            'No durability, network-partition, disk-failure or RTO/RPO certification']}


# Node is present in Quorivio's application image. Never use a shell, redirect,
# or operate outside the private UUID-scoped .quorivio-rwx-probe-* directory.
NODE_PROBE = r'''
const fs=require('node:fs'),path=require('node:path');
const [root,id,action]=process.argv.slice(1);
if(!/^\w[\w-]*$/.test(id)||id.length>60||!['write-a','read-a','write-b','read-b','clean'].includes(action))process.exit(7);
const base=fs.realpathSync(root),dir=path.join(base,'.quorivio-rwx-probe-'+id);
if(!dir.startsWith(base+path.sep))process.exit(7);
if(action==='clean'){fs.rmSync(dir,{recursive:true,force:true});process.stdout.write('RWX_OK');process.exit(0);}
if(action.startsWith('write'))fs.mkdirSync(dir,{recursive:true,mode:0o700});
const file=path.join(dir,action.endsWith('-a')?'a':'b');
const nonce=fs.readFileSync(0,'utf8');
if(!/^[a-f0-9]{48}$/.test(nonce))process.exit(7);
if(action.startsWith('write')){
 const fd=fs.openSync(file,fs.constants.O_WRONLY|fs.constants.O_CREAT|fs.constants.O_EXCL|fs.constants.O_NOFOLLOW,0o600);
 try{fs.writeFileSync(fd,nonce,'utf8');fs.fsyncSync(fd)}finally{fs.closeSync(fd)}
}else{
 const fd=fs.openSync(file,fs.constants.O_RDONLY|fs.constants.O_NOFOLLOW);
 try{if(fs.readFileSync(fd,'utf8')!==nonce)process.exit(8)}finally{fs.closeSync(fd)}
}
process.stdout.write('RWX_OK');
'''.strip()


def exchange(*, context: str, namespace: str, evidence: dict,
             runner=run) -> dict:
    """A -> B and B -> A. Cleanup is attempted on either pod even after errors."""
    pod_a, pod_b = evidence['pod_pair']
    nonce = secrets.token_hex(24)
    identity = secrets.token_hex(16)
    container, mount = evidence['container'], evidence['mount_path']

    def exec_in(pod: str, action: str, value: str = '') -> None:
        command = ['kubectl', '--context', context, '-n', namespace, 'exec', '-i', pod,
                   '-c', container, '--', 'node', '-e', NODE_PROBE, mount, identity, action]
        result = runner(command, stdin=value, timeout=25)
        require(result.strip() == 'RWX_OK', 'Cross-node RWX probe returned invalid acknowledgement')

    try:
        exec_in(pod_a, 'write-a', nonce)
        exec_in(pod_b, 'read-a', nonce)
        exec_in(pod_b, 'write-b', nonce)
        exec_in(pod_a, 'read-b', nonce)
    finally:
        # Try both: one replica may be unavailable after an interrupted operation.
        # The directory name is random, and no production asset path is removed.
        for pod in (pod_a, pod_b):
            try:
                exec_in(pod, 'clean')
            except ProbeError:
                pass
    return {'status': 'CROSS_NODE_RW_EXCHANGE_PASS', 'directions': 2,
            'bytes_per_direction': len(nonce), 'cleanup_attempted_on_both_pods': True,
            'limitations': evidence['limitations'] + [
                'Two ready pods on Kubernetes nodes do not prove physically independent hosts',
                'This opt-in non-destructive probe is not sustained I/O or network fault injection']}


def collect(*, context: str, namespace: str, deployment: str, mount: str,
            confirm_write: bool, runner=run) -> dict:
    require(all(DNS.fullmatch(v) for v in (namespace, deployment)),
            'Namespace or deployment name invalid')
    validate_mount(mount)
    require(isinstance(context, str) and context and len(context) <= 253 and '\x00' not in context,
            'Explicit expected Kubernetes context is required')
    current = runner(['kubectl', 'config', 'current-context'], timeout=12).strip()
    require(current == context, 'Refusing a Kubernetes context different from the expected context')

    def get(*parts: str) -> dict:
        return read_json(['kubectl', '--context', context, *parts, '-o', 'json'], runner=runner)

    dep = get('-n', namespace, 'get', 'deployment', deployment)
    labels = dep.get('spec', {}).get('selector', {}).get('matchLabels', {})
    require(labels and all(LABEL_KEY.fullmatch(k) and LABEL_VALUE.fullmatch(v) for k, v in labels.items()),
            'Deployment selector unsuitable for scoped pod queries')
    selector = ','.join(f'{k}={v}' for k,v in sorted(labels.items()))
    pods = get('-n', namespace, 'get', 'pods', '-l', selector)
    volume_names = [v.get('persistentVolumeClaim', {}).get('claimName') for v in
                    dep.get('spec', {}).get('template', {}).get('spec', {}).get('volumes', [])
                    if 'persistentVolumeClaim' in v]
    require(len(volume_names) == 1 and isinstance(volume_names[0], str) and DNS.fullmatch(volume_names[0]),
            'Exactly one named RWX claim is required')
    pvc = get('-n', namespace, 'get', 'pvc', volume_names[0])
    pv_name = pvc.get('spec', {}).get('volumeName', '')
    require(bool(pv_name) and DNS.fullmatch(pv_name), 'PVC must reference a valid bound PV')
    pv = get('get', 'pv', pv_name)
    result = assess(dep, pods, pvc, pv, mount=mount)
    if confirm_write:
        result = {**result, **exchange(context=context, namespace=namespace,
                                      evidence=result, runner=runner)}
    else:
        result['status'] = 'API_CONTRACT_ONLY_NO_IO'
    return result


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--context', required=True)
    p.add_argument('--namespace', required=True)
    p.add_argument('--deployment', required=True)
    p.add_argument('--mount-path', default='/app/assets')
    p.add_argument('--confirm-write', action='store_true', help='opt in to temporary two-way cross-pod file I/O')
    args = p.parse_args(argv)
    try:
        outcome = collect(context=args.context, namespace=args.namespace, deployment=args.deployment,
                          mount=args.mount_path, confirm_write=args.confirm_write)
    except ProbeError as exc:
        print(json.dumps({'status':'FAIL', 'reason':str(exc)}, ensure_ascii=False))
        return 2
    # No arbitrary kubectl, asset contents, file UUID, or sensitive paths in output.
    outcome.pop('pod_pair', None)
    print(json.dumps(outcome, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
