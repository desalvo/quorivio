#!/usr/bin/env python3
"""Standalone-compatible PostgreSQL disk-PVC probe upgrade.

A DB filesystem is observable only inside its pod/PVC. An existing wizard-
managed PostgreSQL StatefulSet can receive a read-only filesystem probe,
which writes real df capacity to a small, database-backed telemetry row.
A planned/apply split and explicit DB restart acknowledgement guard against
unintentional disruption of single-node PostgreSQL installations.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path

NAME=re.compile(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?\Z')
OVERLAY='97-postgres-disk-probe-patch.json'
PLAN='disk-monitor-plan.json'
PATCH='disk-monitor-json-patch.json'
PROBE_NAME='db-disk-probe'
PROBE_SCRIPT='''
while true; do
  measure="$(df -Pk /var/lib/postgresql | awk 'END {print $2 " " $4}')"
  set -- $measure
  if [ "$#" -eq 2 ]; then
    case "$1:$2" in
      *[!0-9:]*|:*) echo 'database disk probe: invalid df sample' >&2 ;;
      *)
        total="$(( $1 * 1024 ))"
        available="$(( $2 * 1024 ))"
        if [ "$total" -gt 0 ] && [ "$available" -ge 0 ] && [ "$available" -le "$total" ]; then
          PGPASSWORD="$POSTGRES_PASSWORD" PGSSLMODE=disable psql -w -X -q -v ON_ERROR_STOP=1 -h 127.0.0.1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c \
            "INSERT INTO disk_monitor_samples(source,total_bytes,available_bytes,observed_at) VALUES ('database',$total,$available,now()) ON CONFLICT(source) DO UPDATE SET total_bytes=excluded.total_bytes,available_bytes=excluded.available_bytes,observed_at=excluded.observed_at" >/dev/null 2>&1 || echo 'database disk probe: DB not ready; will retry' >&2
        fi ;;
    esac
  fi
  sleep 300
done
'''.strip()

class DiskMonitorUpgradeError(ValueError):pass

def valid_name(value:str)->str:
 if not isinstance(value,str) or len(value)>253 or any(len(part)>63 or not NAME.fullmatch(part) for part in value.split('.')):raise DiskMonitorUpgradeError('invalid Kubernetes resource name')
 return value

def _run(args:list[str],kubectl='kubectl',stdin=None,timeout=30)->str:
 try:p=subprocess.run([kubectl,*args],input=stdin,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout,check=False)
 except (OSError,subprocess.TimeoutExpired) as ex:raise DiskMonitorUpgradeError('kubectl unavailable, verify kubeconfig and RBAC') from ex
 if p.returncode:raise DiskMonitorUpgradeError('kubectl operation failed: '+str(args[:3])+'; verify context, RBAC and rollout')
 return p.stdout

def _context(kubectl='kubectl')->str:
 value=_run(['config','current-context'],kubectl).strip()
 if not value:raise DiskMonitorUpgradeError('missing Kubernetes context')
 return value

def _statefulset(namespace:str,name:str,kubectl='kubectl')->dict:
 s=json.loads(_run(['-n',namespace,'get','statefulset',name,'-o','json'],kubectl))
 if s.get('kind')!='StatefulSet' or s.get('metadata',{}).get('name')!=name or s.get('metadata',{}).get('namespace',namespace)!=namespace:raise DiskMonitorUpgradeError('StatefulSet mismatch')
 return s

def disk_probe_sidecar(postgres:dict)->dict:
 containers=postgres.get('spec',{}).get('template',{}).get('spec',{}).get('containers',[])
 original=[c for c in containers if c.get('name')=='postgres']
 if len(original)!=1:raise DiskMonitorUpgradeError('expected one postgres container')
 pg=original[0]
 mounts=pg.get('volumeMounts') or []
 if not any(m.get('mountPath')=='/var/lib/postgresql' and m.get('name') for m in mounts):raise DiskMonitorUpgradeError('PostgreSQL PVC mount not found at /var/lib/postgresql')
 env=pg.get('env') or []
 selected=[]
 for key in ('POSTGRES_DB','POSTGRES_USER','POSTGRES_PASSWORD'):
  matches=[e for e in env if e.get('name')==key]
  if len(matches)!=1 or not isinstance(matches[0],dict) or ('value' not in matches[0] and 'valueFrom' not in matches[0]):raise DiskMonitorUpgradeError('PostgreSQL '+key+' is not explicitly configured')
  selected.append(matches[0])
 if 'valueFrom' not in selected[-1] or not selected[-1]['valueFrom'].get('secretKeyRef'):
  raise DiskMonitorUpgradeError('PostgreSQL password must come from a Kubernetes Secret')
 image=pg.get('image')
 if not isinstance(image,str) or not image.startswith('postgres:'):raise DiskMonitorUpgradeError('probe requires official PostgreSQL image with psql and df')
 mount=next(m for m in mounts if m.get('mountPath')=='/var/lib/postgresql')
 return {'name':PROBE_NAME,'image':image,'imagePullPolicy':pg.get('imagePullPolicy','IfNotPresent'),
  'command':['/bin/sh','-ec',PROBE_SCRIPT], 'env':selected,
  'volumeMounts':[{'name':mount['name'],'mountPath':'/var/lib/postgresql','readOnly':True}],
  'securityContext':{'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'runAsNonRoot':True,'runAsUser':999,'capabilities':{'drop':['ALL']}},
  'resources':{'requests':{'cpu':'10m','memory':'32Mi'},'limits':{'cpu':'150m','memory':'128Mi'}}}

def _safe_write(path:Path,data:bytes)->None:
 if path.is_symlink() or (path.exists() and not path.is_file()):raise DiskMonitorUpgradeError('unsafe output file')
 fd,tmp=tempfile.mkstemp(prefix='.db-disk-monitor-',dir=str(path.parent));os.fchmod(fd,0o600)
 try:
  with os.fdopen(fd,'wb') as dest:dest.write(data);dest.flush();os.fsync(dest.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def _generated(generated:Path,namespace:str,name:str,sidecar:dict)->None:
 generated=Path(generated).absolute()
 base=generated/'12-postgres-statefulset.yaml';kfile=generated/'kustomization.yaml';patchfile=generated/OVERLAY
 if generated.is_symlink() or not base.is_file() or base.is_symlink() or not kfile.is_file() or kfile.is_symlink():raise DiskMonitorUpgradeError('wizard-generated internal PostgreSQL manifests not found')
 k=kfile.read_text()
 if name+'-postgres' not in base.read_text() or namespace not in base.read_text():raise DiskMonitorUpgradeError('generated StatefulSet identity mismatch')
 if '  - path: '+OVERLAY not in k:
  if re.search(r'(?m)^patches:\s*$',k):
   lines=k.splitlines(keepends=True);matches=[i for i,l in enumerate(lines) if l.strip()=='patches:' and l.startswith('patches:')]
   if len(matches)!=1:raise DiskMonitorUpgradeError('ambiguous Kustomize patches')
   idx=matches[0]+1
   while idx<len(lines) and (lines[idx].startswith(' ') or not lines[idx].strip()):idx+=1
   lines.insert(idx,'  - path: '+OVERLAY+'\n');k=''.join(lines)
  else:k=k.rstrip()+'\npatches:\n  - path: '+OVERLAY+'\n'
 patch={'apiVersion':'apps/v1','kind':'StatefulSet','metadata':{'name':name+'-postgres','namespace':namespace},'spec':{'template':{'spec':{'containers':[sidecar]}}}}
 if patchfile.is_symlink():raise DiskMonitorUpgradeError('refusing symlinked Kustomize patch')
 # Backups private; do not back up credentials here.
 backup=generated/'.quorivio-manifest-backups';backup.mkdir(exist_ok=True,mode=0o700)
 if backup.is_symlink():raise DiskMonitorUpgradeError('unsafe backup location')
 for file in (kfile,patchfile):
  if file.is_file():
   dest=backup/(file.name+'.before-disk-monitor')
   if not dest.exists():_safe_write(dest,file.read_bytes())
 _safe_write(patchfile,(json.dumps(patch,indent=2,sort_keys=True)+'\n').encode())
 _safe_write(kfile,k.encode())

def plan_disk_monitor(namespace:str,app_name:str,output:Path,generated:Path,kubectl='kubectl')->dict:
 namespace=valid_name(namespace);app_name=valid_name(app_name)
 output=Path(output).absolute();generated=Path(generated).absolute()
 if output.exists() and any(output.iterdir()):raise DiskMonitorUpgradeError('plan output must be empty')
 state=_statefulset(namespace,app_name+'-postgres',kubectl)
 containers=state['spec']['template']['spec']['containers']
 if any(c.get('name')==PROBE_NAME for c in containers):raise DiskMonitorUpgradeError('disk probe already installed; use --sync-disk-monitor instead')
 sidecar=disk_probe_sidecar(state)
 meta=state['metadata'];uid=meta.get('uid');rv=meta.get('resourceVersion')
 if not uid or not rv:raise DiskMonitorUpgradeError('missing UID/resourceVersion')
 if not (generated/'12-postgres-statefulset.yaml').is_file():raise DiskMonitorUpgradeError('generated PostgreSQL manifest absent')
 manifest_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (generated/'kustomization.yaml',generated/'12-postgres-statefulset.yaml')}
 patch=[{'op':'test','path':'/metadata/uid','value':uid},{'op':'test','path':'/metadata/resourceVersion','value':rv},{'op':'add','path':'/spec/template/spec/containers/-','value':sidecar}]
 data={'schema':'quorivio-db-disk-monitor-v1','namespace':namespace,'statefulset':app_name+'-postgres','context':_context(kubectl),'uid':uid,'resourceVersion':rv,'generatedDir':str(generated),'generatedHashes':manifest_hashes,'patchSha256':hashlib.sha256(json.dumps(patch,sort_keys=True).encode()).hexdigest()}
 output.mkdir(parents=True,exist_ok=True,mode=0o700)
 _safe_write(output/PLAN,(json.dumps(data,indent=2,sort_keys=True)+'\n').encode());_safe_write(output/PATCH,(json.dumps(patch,indent=2,sort_keys=True)+'\n').encode())
 return data

def apply_disk_monitor(output:Path,ack_restart:bool,kubectl='kubectl')->dict:
 if not ack_restart:raise DiskMonitorUpgradeError('explicit --acknowledge-db-restart is required: a StatefulSet rollout restarts PostgreSQL')
 output=Path(output).absolute();plan=json.loads((output/PLAN).read_text());patch=json.loads((output/PATCH).read_text())
 if plan.get('schema')!='quorivio-db-disk-monitor-v1' or plan.get('patchSha256')!=hashlib.sha256(json.dumps(patch,sort_keys=True).encode()).hexdigest():raise DiskMonitorUpgradeError('invalid or modified disk-monitor plan')
 if _context(kubectl)!=plan['context']:raise DiskMonitorUpgradeError('Kubernetes context changed')
 state=_statefulset(plan['namespace'],plan['statefulset'],kubectl)
 if state['metadata'].get('uid')!=plan['uid'] or state['metadata'].get('resourceVersion')!=plan['resourceVersion']:raise DiskMonitorUpgradeError('PostgreSQL StatefulSet changed since planning')
 directory=Path(plan['generatedDir'])
 for name,digest in plan['generatedHashes'].items():
  source=directory/name
  if source.is_symlink() or not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise DiskMonitorUpgradeError('generated manifests changed since planning')
 _run(['-n',plan['namespace'],'patch','statefulset',plan['statefulset'],'--type=json','--patch-file='+str(output/PATCH),'--dry-run=server','-o','name'],kubectl)
 _run(['-n',plan['namespace'],'patch','statefulset',plan['statefulset'],'--type=json','--patch-file='+str(output/PATCH)],kubectl)
 _run(['-n',plan['namespace'],'rollout','status','statefulset/'+plan['statefulset'],'--timeout=300s'],kubectl,timeout=330)
 return sync_disk_monitor(plan['namespace'],plan['statefulset'].removesuffix('-postgres'),directory,kubectl)

# The Kubernetes API server defaults these two harmless Container fields when
# it persists a StatefulSet. They are absent from the JSON Patch submitted by
# the wizard. Compare security-sensitive properties EXACTLY after removing ONLY
# these precisely valued API defaults, never by partial dict/subset matching.
_API_CONTAINER_DEFAULTS={
 'terminationMessagePath':'/dev/termination-log',
 'terminationMessagePolicy':'File',
}

def _verified_live_probe(live_probe:dict,expected:dict)->None:
 if not isinstance(live_probe,dict):
  raise DiskMonitorUpgradeError('invalid live disk probe structure')
 actual=dict(live_probe)
 for key,allowed in _API_CONTAINER_DEFAULTS.items():
  if key in actual:
   if actual[key]!=allowed:
    raise DiskMonitorUpgradeError('live disk probe '+key+' drift; refusing manifest overwrite')
   del actual[key]
 if actual!=expected:
  # Do not print the live value: some future admission controllers may inject
  # sensitive data into an env entry. Only expose non-secret property names.
  differences=sorted(k for k in set(actual)|set(expected) if actual.get(k)!=expected.get(k))
  raise DiskMonitorUpgradeError('live disk probe security/image/volumes drift; refusing manifest overwrite (fields: '+','.join(differences)+')')

def sync_disk_monitor(namespace:str,app_name:str,generated:Path,kubectl='kubectl')->dict:
 namespace=valid_name(namespace);app_name=valid_name(app_name)
 live=_statefulset(namespace,app_name+'-postgres',kubectl)
 probes=[c for c in live['spec']['template']['spec']['containers'] if c.get('name')==PROBE_NAME]
 if len(probes)!=1:raise DiskMonitorUpgradeError('no unique live PostgreSQL disk probe')
 expected=disk_probe_sidecar(live)
 _verified_live_probe(probes[0],expected)
 _generated(Path(generated),namespace,app_name,expected)
 return {'namespace':namespace,'statefulset':app_name+'-postgres','generatedDir':str(Path(generated).absolute())}
