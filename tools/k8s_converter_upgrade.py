#!/usr/bin/env python3
"""Safe, narrowly scoped conversion sidecar upgrade for wizard-created Deployments.

Read live Kubernetes objects; never regenerate or replace the original Kustomize
base, Secrets, PostgreSQL, PVCs, Ingress, or Service. Plans contain only a JSON
Patch on the Deployment pod template with resourceVersion/UID compare-and-swap.
Applying a plan is a separate explicit operation.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import math
import os
import re
import secrets
import stat
import subprocess
import tempfile
import time
from pathlib import Path

NAME = re.compile(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?\Z')
IMAGE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:/@+\-]*\Z')
PLAN_SCHEMA = 'quorivio-k8s-converter-upgrade-v1'
CONVERTER_OVERLAY = '95-converter-sidecar-patch.json'
CONVERTER_NAME = 'converter'
ENV = {
    'QUORIVIO_ENABLE_CONVERTER': 'true',
    'QUORIVIO_CONVERTER_WORKER_URL': 'http://127.0.0.1:8099',
    'QUORIVIO_CONVERSION_DIR': '/conversions',
}


class UpgradeError(ValueError):
    pass


def valid_name(value: str, kind: str = 'resource') -> str:
    if not isinstance(value, str) or len(value) > 253 or any(len(x)>63 or not NAME.fullmatch(x) for x in value.split('.')):
        raise UpgradeError(f'invalid {kind} name')
    return value


def run_kubectl(args: list[str], *, kubectl: str = 'kubectl', input_data: str | None = None, timeout: int = 25) -> str:
    try:
        cmd=[kubectl, *args]
        p=subprocess.run(cmd,input=input_data,capture_output=True,text=True,timeout=timeout,check=False)
    except (OSError, subprocess.TimeoutExpired) as ex:
        raise UpgradeError('kubectl operation unavailable or timed out; verify kubeconfig/context') from ex
    if p.returncode:
        # Never print kubectl stderr: it can contain admission webhook payloads
        # or credentials from a malformed existing Deployment.
        raise UpgradeError('Kubernetes request failed: ' + ' '.join(args[:min(3,len(args))]) + '; check RBAC, context and cluster status')
    return p.stdout


def get_object(namespace: str, kind: str, name: str, kubectl: str = 'kubectl') -> dict:
    raw=run_kubectl(['-n',namespace,'get',kind,name,'-o','json','--request-timeout=10s'],kubectl=kubectl)
    try: value=json.loads(raw)
    except json.JSONDecodeError as ex: raise UpgradeError('invalid Kubernetes JSON response') from ex
    if not isinstance(value,dict) or value.get('metadata',{}).get('name') != name or value.get('metadata',{}).get('namespace',namespace) != namespace:
        raise UpgradeError('Kubernetes resource identity mismatch')
    return value


def kube_context(kubectl: str = 'kubectl') -> str:
    value=run_kubectl(['config','current-context'],kubectl=kubectl).strip()
    if not value: raise UpgradeError('kubectl current context is missing')
    return value


def find_api_container(deployment: dict, requested: str | None) -> tuple[int,dict]:
    containers=deployment.get('spec',{}).get('template',{}).get('spec',{}).get('containers',[])
    if not isinstance(containers,list) or not containers:raise UpgradeError('Deployment has no app containers')
    if any(not isinstance(c,dict) or not isinstance(c.get('name'),str) for c in containers):
        raise UpgradeError('invalid container inventory')
    if requested:
        hits=[(i,c) for i,c in enumerate(containers) if c['name']==requested]
    else:
        hits=[(i,c) for i,c in enumerate(containers) if c['name'] in ('quorivio',deployment.get('metadata',{}).get('name'))]
        if len(hits)!=1 and len(containers)==1:hits=[(0,containers[0])]
    if len(hits)!=1:raise UpgradeError('ambiguous app container: specify --app-container')
    if hits[0][1]['name']==CONVERTER_NAME:raise UpgradeError('cannot use converter as the app container')
    return hits[0]


def discover_secret(app: dict, explicit: str | None) -> str:
    if explicit:return valid_name(explicit,'Secret')
    env=app.get('env',[]) or []
    if not isinstance(env,list):raise UpgradeError('invalid app env')
    preferred={v.get('valueFrom',{}).get('secretKeyRef',{}).get('name') for v in env if v.get('name') in ('DATABASE_URL','AUTH_SECRET')}
    preferred.discard(None)
    if len(preferred)==1:return valid_name(preferred.pop(),'Secret')
    if len(preferred)>1:raise UpgradeError('multiple app Secrets: specify --converter-secret')
    refs=[v.get('secretRef',{}).get('name') for v in app.get('envFrom',[]) or [] if 'secretRef' in v]
    refs=[v for v in refs if v]
    if len(set(refs))==1:return valid_name(refs[0],'Secret')
    raise UpgradeError('cannot identify existing app Secret: specify --converter-secret')


def check_token(secret: dict) -> bool:
    encoded=(secret.get('data') or {}).get('QUORIVIO_WORKER_TOKEN')
    if encoded is None:return False
    try: token=base64.b64decode(encoded,validate=True)
    except (ValueError, TypeError) as ex:raise UpgradeError('worker token Secret value is not valid base64') from ex
    if len(token)<32 or b'\n' in token or b'\r' in token:
        raise UpgradeError('existing worker token is invalid or shorter than 32 bytes; do not overwrite automatically')
    return True


def plan_token_provision(namespace: str, deployment_name: str, app_container: str | None, explicit_secret: str | None, kubectl: str='kubectl') -> tuple[str,bool]:
    deployment=get_object(namespace,'deployment',deployment_name,kubectl)
    _,app=find_api_container(deployment,app_container)
    name=discover_secret(app,explicit_secret)
    secret=get_object(namespace,'secret',name,kubectl)
    if check_token(secret):return name,False
    if secret.get('immutable') is True:raise UpgradeError('existing Secret is immutable; cannot provision token')
    version=secret.get('metadata',{}).get('resourceVersion')
    if not isinstance(version,str) or not version:raise UpgradeError('missing Secret resourceVersion')
    patch=[{'op':'test','path':'/metadata/resourceVersion','value':version}]
    if secret.get('data') is None:
        patch.append({'op':'add','path':'/data','value':{}})
    # The token exists only in memory and is sent via stdin; not in shell args,
    # generated manifests, logs, the source tree, or a temporary file.
    token=secrets.token_hex(32)
    patch.append({'op':'add','path':'/data/QUORIVIO_WORKER_TOKEN','value':base64.b64encode(token.encode('ascii')).decode('ascii')})
    payload=json.dumps(patch,separators=(',',':'))
    for dry in (True,False):
        args=['-n',namespace,'patch','secret',name,'--type=json','--patch-file=/dev/stdin','-o','name']
        if dry:args.insert(-2,'--dry-run=server')
        run_kubectl(args,kubectl=kubectl,input_data=payload)
    return name,True


def _append_list(ops: list[dict], obj: dict, key: str, prefix: str, entries: list[dict]) -> None:
    if not entries:return
    existing=obj.get(key)
    if existing is None:ops.append({'op':'add','path':prefix+'/'+key,'value':entries})
    elif isinstance(existing,list):
        for entry in entries:ops.append({'op':'add','path':prefix+'/'+key+'/-','value':entry})
    else:raise UpgradeError('malformed Kubernetes array '+key)


def _rollout_int_or_percent(value: object, replicas: int, *, round_up: bool, label: str) -> int:
    """Resolve an IntOrString using Kubernetes RollingUpdate rounding rules.

    maxUnavailable percentages round DOWN; maxSurge percentages round UP.
    Python booleans are not valid Kubernetes integer quantities.
    """
    if type(value) is int and value >= 0:
        return value
    if isinstance(value, str) and re.fullmatch(r'[0-9]+%', value):
        pct = int(value[:-1])
        if pct > 100:
            raise UpgradeError(f'invalid {label} percentage')
        count = replicas * pct
        return (count + 99) // 100 if round_up else count // 100
    # Kubernetes emits JSON numbers for integer IntOrString and strings for
    # percentages. Conservatively reject malformed/missing representations.
    raise UpgradeError(f'invalid {label}; expected nonnegative integer or 0..100%')


def effective_rollout_unavailability(deployment: dict) -> int:
    """Evaluate live API Deployment rollout constraints without altering them."""
    spec = deployment.get('spec') or {}
    replicas = spec.get('replicas', 1)
    if type(replicas) is not int or replicas < 1:
        raise UpgradeError('Deployment requires at least one replica for availability-safe converter upgrade')
    strategy = spec.get('strategy') or {}
    kind = strategy.get('type', 'RollingUpdate')
    if kind == 'Recreate':
        raise UpgradeError('Recreate strategy; refuse potential availability disruption')
    if kind != 'RollingUpdate':
        raise UpgradeError('unsupported Deployment rollout strategy')
    rolling = strategy.get('rollingUpdate') or {}
    unavailable = _rollout_int_or_percent(
        rolling.get('maxUnavailable', '25%'), replicas, round_up=False,
        label='maxUnavailable')
    surge = _rollout_int_or_percent(
        rolling.get('maxSurge', '25%'), replicas, round_up=True,
        label='maxSurge')
    if surge == 0 and unavailable == 0:
        raise UpgradeError('maxUnavailable and maxSurge are both effectively zero; rollout would stall')
    return unavailable


def build_patch(deployment: dict, app_container: str | None, secret_name: str, image: str) -> tuple[list[dict],dict]:
    if not IMAGE.fullmatch(image) or '://' in image or '/' not in image:
        raise UpgradeError('converter image must be a valid repository with explicit tag or digest')
    if '@' in image:
        digest=image.split('@',1)[1]
        if not re.fullmatch(r'sha256:[0-9a-f]{64}',digest):
            raise UpgradeError('converter image digest must be a full sha256 reference')
    elif ':' not in image.rsplit('/',1)[-1]:
        raise UpgradeError('converter image requires latest, a release tag or sha256 digest')
    spec=deployment.get('spec',{}).get('template',{}).get('spec',{})
    pod_sec=spec.get('securityContext') or {}
    group=pod_sec.get('fsGroup')
    if type(group) is not int or group<1:
        raise UpgradeError('existing pod needs an fsGroup for shared writable emptyDir; refuse to alter PVC ownership')
    # Kubernetes defaults RollingUpdate to 25% maxUnavailable and rounds
    # percentage values DOWN. For 1..3 replicas, the effective unavailability
    # is zero. Reject only plans that could actually remove a ready replica.
    if effective_rollout_unavailability(deployment) != 0:
        raise UpgradeError('effective maxUnavailable is non-zero; refuse potential availability disruption')
    if deployment.get('metadata',{}).get('labels',{}).get('app.kubernetes.io/managed-by')=='Helm':
        raise UpgradeError('Helm-managed Deployment: use helm upgrade instead of patching')
    version=deployment.get('metadata',{}).get('resourceVersion')
    uid=deployment.get('metadata',{}).get('uid')
    if not isinstance(version,str) or not version or not isinstance(uid,str) or not uid:
        raise UpgradeError('Deployment UID/resourceVersion unavailable; cannot safely guard changes')
    i,app=find_api_container(deployment,app_container)
    containers=spec['containers']
    if any(port.get('containerPort') == 8099 or port.get('name') == CONVERTER_NAME
           for container in containers for port in container.get('ports',[]) or []):
        raise UpgradeError('pod port 8099 or converter port name is already claimed')
    if any(c.get('name')==CONVERTER_NAME for c in containers):
        raise UpgradeError('converter sidecar already exists: inspect or reconcile it manually; no overwrite')
    existing_env={v['name']:v for v in app.get('env',[]) or [] if isinstance(v,dict) and 'name' in v}
    desired_env=[{'name':key,'value':value} for key,value in ENV.items()]
    desired_env.append({'name':'QUORIVIO_WORKER_TOKEN','valueFrom':{'secretKeyRef':{'name':secret_name,'key':'QUORIVIO_WORKER_TOKEN'}}})
    missing_env=[]
    for item in desired_env:
        prior=existing_env.get(item['name'])
        if prior is None:missing_env.append(item)
        elif prior != item:raise UpgradeError(f'conflicting existing app variable {item["name"]}; refuse to override')
    volumes=spec.get('volumes',[]) or []
    for v in volumes:
        if v.get('name') in ('conversions','converter-tmp'):
            raise UpgradeError('converter volume name already in use; refuse to take over existing volume')
    mounts=app.get('volumeMounts',[]) or []
    for m in mounts:
        if m.get('name')=='conversions' or m.get('mountPath')=='/conversions':
            raise UpgradeError('existing conversion mount present: refuse to replace or shadow it')
    sidecar={
      'name':CONVERTER_NAME,'image':image,'imagePullPolicy':'IfNotPresent',
      'ports':[{'name':'converter','containerPort':8099,'protocol':'TCP'}],
      'env':[{'name':'QUORIVIO_WORKER_TOKEN','valueFrom':{'secretKeyRef':{'name':secret_name,'key':'QUORIVIO_WORKER_TOKEN'}}},
             {'name':'QUORIVIO_CONVERSION_DIR','value':'/conversions'},
             {'name':'HOME','value':'/tmp'}, {'name':'XDG_CACHE_HOME','value':'/tmp/.cache'}],
      'volumeMounts':[{'name':'conversions','mountPath':'/conversions'}, {'name':'converter-tmp','mountPath':'/tmp'}],
      'readinessProbe':{'httpGet':{'path':'/health','port':8099},'initialDelaySeconds':3,'periodSeconds':10,'timeoutSeconds':3,'failureThreshold':6},
      'livenessProbe':{'httpGet':{'path':'/health','port':8099},'initialDelaySeconds':20,'periodSeconds':30,'timeoutSeconds':3,'failureThreshold':3},
      'securityContext':{'runAsNonRoot':True,'runAsUser':1000,'runAsGroup':group,'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']},'seccompProfile':{'type':'RuntimeDefault'}},
      'resources':{'requests':{'cpu':'100m','memory':'256Mi'},'limits':{'cpu':'2','memory':'2Gi'}},
    }
    patch=[{'op':'test','path':'/metadata/uid','value':uid},
           {'op':'test','path':'/metadata/resourceVersion','value':version},
           {'op':'test','path':f'/spec/template/spec/containers/{i}/name','value':app['name']}]
    _append_list(patch,app,'env',f'/spec/template/spec/containers/{i}',missing_env)
    _append_list(patch,app,'volumeMounts',f'/spec/template/spec/containers/{i}',[{'name':'conversions','mountPath':'/conversions'}])
    _append_list(patch,spec,'volumes','/spec/template/spec',[
         {'name':'conversions','emptyDir':{'sizeLimit':'2Gi'}},
         {'name':'converter-tmp','emptyDir':{'sizeLimit':'1Gi'}}])
    patch.append({'op':'add','path':'/spec/template/spec/containers/-','value':sidecar})
    return patch, {'deployment_uid':uid,'deployment_resource_version':version,'app_container':app['name'],'secret_name':secret_name}


def _generated_input(directory: Path, namespace: str, deployment_name: str,
                     secret_name: str) -> tuple[Path, dict[str, bytes]]:
    """Fail closed unless this is the original, owned wizard Kustomize directory.

    Inspect exact metadata and files without evaluating YAML tags, following
    symlinks or reading any credentials into logs. All unrelated resources,
    operator customizations and overrides are preserved byte-for-byte.
    """
    directory=Path(directory).absolute()
    if any(part.is_symlink() for part in (directory,*directory.parents)):
        raise UpgradeError('generated manifest path or parent is a symlink')
    if not directory.is_dir():
        raise UpgradeError('generated manifest directory does not exist')
    names=('kustomization.yaml','20-deployment.yaml','05-app-secret.yaml','quorivio-overrides.json')
    data={}
    for name in names:
        file=directory/name
        if file.is_symlink() or not file.is_file() or not stat.S_ISREG(file.stat().st_mode):
            raise UpgradeError('generated directory must contain a regular wizard file: '+name)
        data[name]=file.read_bytes()
    k=data['kustomization.yaml'].decode('utf-8')
    d=data['20-deployment.yaml'].decode('utf-8')
    secret=data['05-app-secret.yaml'].decode('utf-8')
    if not all(re.search(r'^  - '+re.escape(entry)+r'$',k,re.M) for entry in ('20-deployment.yaml','05-app-secret.yaml')):
        raise UpgradeError('generated Kustomization does not include Deployment and Secret')
    for value,kind,name in ((d,'Deployment',deployment_name),(secret,'Secret',secret_name)):
        # The original generator emits apiVersion/kind/metadata in this order.
        if not re.search(r'(?m)^kind: '+kind+r'\nmetadata:\n  name: '+re.escape(name)+r'\n  namespace: '+re.escape(namespace)+r'\s*$',value):
            raise UpgradeError('generated '+kind+' identity differs from live Kubernetes')
    try: overrides=json.loads(data['quorivio-overrides.json'])
    except ValueError as exc:raise UpgradeError('generated wizard override record is not valid JSON') from exc
    if not isinstance(overrides,dict) or any(k in overrides and overrides[k]!=v for k,v in (('namespace',namespace),('name',deployment_name))):
        raise UpgradeError('generated override name/namespace differs from live Deployment')
    return directory,data


def _secret_data_yaml(source: str) -> dict[str,str]:
    """Read only the simple base64 data block emitted by the wizard."""
    if not re.search(r'(?m)^type: Opaque\n^data:\n',source):
        raise UpgradeError('generated Secret does not use the expected Opaque/data format')
    tail=source.split('\ndata:\n',1)[1]
    result={}
    for line in tail.splitlines():
        if not line.strip():continue
        match=re.fullmatch(r'  ([A-Z][A-Z0-9_]*): ([A-Za-z0-9+/=]+)',line)
        if not match:
            raise UpgradeError('generated Secret contains unsupported data encoding or annotations')
        key,value=match.groups()
        if key in result:raise UpgradeError('duplicate Secret key in generated manifest')
        try: base64.b64decode(value,validate=True)
        except ValueError as exc:raise UpgradeError('invalid base64 value in generated Secret') from exc
        result[key]=value
    if not result:raise UpgradeError('generated Secret has no data entries')
    return result


def _generated_secret_with_token(source: str, live_secret: dict) -> str:
    check_token(live_secret)
    live=live_secret.get('data') or {}
    recorded=_secret_data_yaml(source)
    for key,value in recorded.items():
        if key in live and live[key]!=value:
            raise UpgradeError('generated Secret differs from live for '+key+'; refuse overwriting credentials')
    token=live['QUORIVIO_WORKER_TOKEN']
    if 'QUORIVIO_WORKER_TOKEN' in recorded:
        return source
    return source.rstrip('\n')+'\n  QUORIVIO_WORKER_TOKEN: '+token+'\n'


def _manifest_overlay(deployment: dict, secret_name: str) -> str:
    """Strategic merge patch: do not replace the original Deployment template.

    Kubernetes Kustomize merges containers by name, env by name and mounts by
    mountPath.  This is declarative and reusable; live JSON Patch preconditions
    such as UID and resourceVersion must never appear in generated manifests.
    """
    spec=deployment['spec']['template']['spec']
    _,app=find_api_container(deployment,None)
    hits=[c for c in spec['containers'] if c['name']==CONVERTER_NAME]
    if len(hits)!=1:raise UpgradeError('live converter sidecar is absent or ambiguous')
    sidecar=hits[0]
    if not IMAGE.fullmatch(sidecar.get('image','')) or not '/' in sidecar['image']:
        raise UpgradeError('invalid live converter image')
    expected_env=[{'name':key,'value':value} for key,value in ENV.items()]
    expected_env.append({'name':'QUORIVIO_WORKER_TOKEN','valueFrom':{'secretKeyRef':{'name':secret_name,'key':'QUORIVIO_WORKER_TOKEN'}}})
    app_env={x.get('name'):x for x in app.get('env',[]) or []}
    for item in expected_env:
        if app_env.get(item['name'])!=item:
            raise UpgradeError('live converter app environment has drifted: '+item['name'])
    if {'name':'conversions','mountPath':'/conversions'} not in (app.get('volumeMounts') or []):
        raise UpgradeError('live converter app mount is absent')
    required_volumes=[{'name':'conversions','emptyDir':{'sizeLimit':'2Gi'}},{'name':'converter-tmp','emptyDir':{'sizeLimit':'1Gi'}}]
    for volume in required_volumes:
        if volume not in (spec.get('volumes') or []):
            raise UpgradeError('live converter volume has unexpected specification')
    if sidecar.get('env') is None or not any(x.get('name')=='QUORIVIO_WORKER_TOKEN' and x.get('valueFrom',{}).get('secretKeyRef',{})=={'name':secret_name,'key':'QUORIVIO_WORKER_TOKEN'} for x in sidecar.get('env',[])):
        raise UpgradeError('live converter Secret reference differs')
    if any(c.get('name')==CONVERTER_NAME for c in spec['containers'] if c is not sidecar):
        raise UpgradeError('duplicate converter container')
    overlay={'apiVersion':'apps/v1','kind':'Deployment',
      'metadata':{'name':deployment['metadata']['name'],'namespace':deployment['metadata']['namespace']},
      'spec':{'template':{'spec':{'containers':[
         {'name':app['name'],'env':expected_env,'volumeMounts':[{'name':'conversions','mountPath':'/conversions'}]},
         sidecar], 'volumes':required_volumes}}}}
    return json.dumps(overlay,indent=2,ensure_ascii=False,sort_keys=True)+'\n'


def _generated_reconciliation_changes(directory: Path, namespace: str, deployment_name: str,
                                       secret_name: str, deployment: dict, live_secret: dict,
                                       expected_hashes: dict | None=None) -> tuple[dict[str,bytes],dict[str,bytes]]:
    directory,original=_generated_input(directory,namespace,deployment_name,secret_name)
    if expected_hashes is not None:
        for name,digest in expected_hashes.items():
            if name==CONVERTER_OVERLAY:
                file=directory/name
                if file.is_symlink() or (hashlib.sha256(file.read_bytes()).hexdigest() if file.is_file() else None)!=digest:
                    raise UpgradeError('generated converter overlay changed since planning; regenerate plan')
            elif name not in original or hashlib.sha256(original[name]).hexdigest()!=digest:
                raise UpgradeError('generated manifest changed since planning: '+name+'; regenerate plan')
    k=original['kustomization.yaml'].decode('utf8')
    if CONVERTER_OVERLAY not in k:
        if re.search(r'(?m)^patches:\s*$',k):
            # Preserve unrelated operator-authored Kustomize patches. Insert
            # before the next root-level key rather than clobbering the list.
            lines=k.splitlines(keepends=True)
            matches=[i for i,line in enumerate(lines) if line.strip()=='patches:' and line.startswith('patches:')]
            if len(matches)!=1:raise UpgradeError('ambiguous generated Kustomize patches')
            insert=matches[0]+1
            while insert<len(lines) and (lines[insert].startswith(' ') or not lines[insert].strip()):insert+=1
            lines.insert(insert,'  - path: '+CONVERTER_OVERLAY+'\n')
            k=''.join(lines)
        else:
            if not k.endswith('\n'):k+='\n'
            k+='patches:\n  - path: '+CONVERTER_OVERLAY+'\n'
    elif not re.search(r'(?m)^  - path: '+re.escape(CONVERTER_OVERLAY)+r'$',k):
        raise UpgradeError('generated converter overlay reference is malformed')
    patch=_manifest_overlay(deployment,secret_name)
    existing_patch=directory/CONVERTER_OVERLAY
    if existing_patch.is_symlink() or (existing_patch.exists() and not existing_patch.is_file()):
        raise UpgradeError('unsafe generated converter overlay file')
    if existing_patch.is_file():
        # Do not silently replace operator-customized overlays.
        try:old=json.loads(existing_patch.read_text(encoding='utf8'))
        except ValueError as exc:raise UpgradeError('existing converter overlay is not valid JSON') from exc
        if old!=json.loads(patch):
            raise UpgradeError('generated converter overlay differs from live; manual reconciliation required')
    secret=_generated_secret_with_token(original['05-app-secret.yaml'].decode('utf8'),live_secret)
    edits={ '05-app-secret.yaml':secret.encode('utf8'),
            CONVERTER_OVERLAY:patch.encode('utf8'),
            'kustomization.yaml':k.encode('utf8') }
    return original,edits


def _atomic_generated_write(path:Path, data:bytes, mode:int)->None:
    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise UpgradeError('unsafe generated manifest destination')
    fd,temp=tempfile.mkstemp(prefix='.quorivio-sync-',dir=str(path.parent))
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as f:
            f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


def _commit_generated_edits(directory: Path, original: dict[str,bytes], edits:dict[str,bytes]) -> str:
    """Backup first; publish Kustomization last to activate complete overlay."""
    directory=Path(directory).absolute()
    backup_root=directory/'.quorivio-manifest-backups'
    if backup_root.is_symlink():raise UpgradeError('unsafe generated backup directory')
    backup_root.mkdir(mode=0o700,exist_ok=True)
    if not backup_root.is_dir():raise UpgradeError('invalid generated backup directory')
    backup=Path(tempfile.mkdtemp(prefix='converter-',dir=str(backup_root)))
    backup.chmod(0o700)
    for name in ('05-app-secret.yaml','kustomization.yaml'):
        (backup/name).write_bytes(original[name]);(backup/name).chmod(0o600)
    current_patch=directory/CONVERTER_OVERLAY
    if current_patch.exists():
        (backup/CONVERTER_OVERLAY).write_bytes(current_patch.read_bytes())
        (backup/CONVERTER_OVERLAY).chmod(0o600)
    # Check for concurrent/manual edits immediately before replacement.
    for name,content in original.items():
        if (directory/name).read_bytes()!=content:
            raise UpgradeError('generated files modified concurrently; backup kept at '+str(backup))
    written=[]
    try:
        for name in ('05-app-secret.yaml',CONVERTER_OVERLAY,'kustomization.yaml'):
            if name not in edits or (name in original and edits[name]==original[name]):continue
            if name==CONVERTER_OVERLAY and edits[name]==b'':continue
            path=directory/name
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise UpgradeError('unsafe generated file during synchronization')
            _atomic_generated_write(path,edits[name],0o600 if name=='05-app-secret.yaml' else 0o644)
            written.append(name)
    except (OSError,UpgradeError) as exc:
        for name in reversed(written):
            path=directory/name
            if name in original:
                _atomic_generated_write(path,original[name],0o600 if name=='05-app-secret.yaml' else 0o644)
            elif (backup/name).exists():
                _atomic_generated_write(path,(backup/name).read_bytes(),0o644)
            else:path.unlink(missing_ok=True)
        raise UpgradeError('generated synchronization failed; original files restored; backup at '+str(backup)) from exc
    return str(backup)


def reconcile_generated(directory: Path, namespace: str, deployment_name: str,
                        *, kubectl: str='kubectl', expected_hashes: dict | None=None) -> str:
    """Read validated live converter state; update only Kustomize overlay and token."""
    deployment=get_object(namespace,'deployment',deployment_name,kubectl)
    _,app=find_api_container(deployment,None)
    secret_name=discover_secret(app,None)
    secret=get_object(namespace,'secret',secret_name,kubectl)
    check_token(secret)
    original,edits=_generated_reconciliation_changes(directory,namespace,deployment_name,
      secret_name,deployment,secret,expected_hashes)
    return _commit_generated_edits(directory,original,edits)


def reconcile_generated_token(directory:Path,namespace:str,deployment_name:str,*,kubectl:str='kubectl') -> str:
    """After --ensure-converter-token, keep the original Kustomize Secret safe."""
    deployment=get_object(namespace,'deployment',deployment_name,kubectl)
    _,app=find_api_container(deployment,None)
    secret_name=discover_secret(app,None)
    secret=get_object(namespace,'secret',secret_name,kubectl)
    _,original=_generated_input(directory,namespace,deployment_name,secret_name)
    updated=_generated_secret_with_token(original['05-app-secret.yaml'].decode('utf8'),secret).encode('utf8')
    if updated==original['05-app-secret.yaml']:
        return 'already synchronized'
    return _commit_generated_edits(Path(directory),original,{
       '05-app-secret.yaml':updated,
       CONVERTER_OVERLAY:(Path(directory)/CONVERTER_OVERLAY).read_bytes() if (Path(directory)/CONVERTER_OVERLAY).is_file() else b'',
       'kustomization.yaml':original['kustomization.yaml'],
    })

def _fresh_directory(output: Path) -> Path:
    # Do not overlay the original wizard-generated manifests: that could
    # accidentally remove PostgreSQL/ingress or regenerate admin credentials.
    if any(part.is_symlink() for part in (output.absolute(), *output.absolute().parents)):
        raise UpgradeError('refusing symlinked upgrade output or parent')
    if output.exists():
        if not output.is_dir() or any(output.iterdir()):
            raise UpgradeError('upgrade output must be a fresh, empty directory; never reuse the original wizard output')
    else: output.mkdir(parents=True,mode=0o700)
    output.chmod(0o700)
    return output


def _write_private(p: Path, value: str) -> None:
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf8') as out:out.write(value)


def prepare_upgrade(namespace: str, deployment_name: str, output: Path,
                    image: str, *, app_container: str | None=None,
                    secret_name: str | None=None, kubectl: str='kubectl',
                    generated_dir: Path | None=None) -> dict:
    valid_name(namespace,'Namespace');valid_name(deployment_name,'Deployment')
    current_context=kube_context(kubectl)
    deployment=get_object(namespace,'deployment',deployment_name,kubectl)
    _,app=find_api_container(deployment,app_container)
    secret_name=discover_secret(app,secret_name)
    secret=get_object(namespace,'secret',secret_name,kubectl)
    if not check_token(secret):
        raise UpgradeError('existing app Secret lacks QUORIVIO_WORKER_TOKEN; run --ensure-converter-token first')
    patch,identity=build_patch(deployment,app_container,secret_name,image)
    generated_hashes=None
    if generated_dir is not None:
        original=_generated_input(generated_dir,namespace,deployment_name,secret_name)[1]
        # Planning is read only. No missing token or converter patch is written yet.
        _generated_secret_with_token(original['05-app-secret.yaml'].decode('utf8'),secret)
        generated_hashes={key:hashlib.sha256(value).hexdigest() for key,value in original.items()}
        overlay_file=Path(generated_dir)/CONVERTER_OVERLAY
        if overlay_file.is_symlink():raise UpgradeError('unsafe generated converter overlay')
        generated_hashes[CONVERTER_OVERLAY]=hashlib.sha256(overlay_file.read_bytes()).hexdigest() if overlay_file.is_file() else None
    output=_fresh_directory(output)
    encoded=json.dumps(patch,indent=2,ensure_ascii=False)+'\n'
    plan={'schema':PLAN_SCHEMA,'context':current_context,'namespace':namespace,'deployment':deployment_name,
          'converter_image':image,**identity,'patch_sha256':hashlib.sha256(encoded.encode('utf8')).hexdigest(),
          'generated_dir':str(Path(generated_dir).absolute()) if generated_dir is not None else None,
          'generated_sha256':generated_hashes}
    _write_private(output/'converter-patch.json',encoded)
    _write_private(output/'converter-plan.json',json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
    _write_private(output/'LEGGIMI.txt',
        'Quorivio upgrade PDF/PPTX: SOLO Deployment; no Secret, DB, PVC, Service or Ingress changes.\n'
        'Inspect converter-plan.json and converter-patch.json. The JSON Patch contains\n'
        'atomic UID/resourceVersion preconditions: stale deployments must be replanned.\n'
        'Check the converter image is available and accessible to cluster nodes.\n'
        'Dry-run: kubectl -n '+namespace+' patch deployment '+deployment_name+
        ' --type=json --patch-file='+str((output/'converter-patch.json').resolve())+' --dry-run=server -o name\n'
        'Apply explicitly using: python3 tools/k8s_wizard.py --apply-converter --output '+str(output.resolve())+'\n'
        'After successful rollout the wizard reconciles the original generated Kustomize base, if configured.\n')
    return plan


def apply_upgrade(output: Path, *, kubectl: str='kubectl') -> dict:
    if any(part.is_symlink() for part in (output.absolute(), *output.absolute().parents)) or not output.is_dir():
        raise UpgradeError('invalid or symlinked converter upgrade directory')
    for name in ('converter-patch.json','converter-plan.json'):
        p=output/name
        if p.is_symlink() or not p.is_file() or not stat.S_ISREG(p.stat().st_mode):
            raise UpgradeError('missing or unsafe upgrade file '+name)
    try:
        plan=json.loads((output/'converter-plan.json').read_text(encoding='utf8'))
        raw=(output/'converter-patch.json').read_bytes()
        patch=json.loads(raw)
    except (ValueError,OSError) as ex:raise UpgradeError('invalid converter upgrade plan') from ex
    if plan.get('schema')!=PLAN_SCHEMA or hashlib.sha256(raw).hexdigest()!=plan.get('patch_sha256'):
        raise UpgradeError('upgrade plan changed after generation; regenerate safely')
    ns=valid_name(plan['namespace'],'Namespace');name=valid_name(plan['deployment'],'Deployment')
    if plan.get('context')!=kube_context(kubectl):
        raise UpgradeError('kubectl context changed: upgrade aborted')
    deployment=get_object(ns,'deployment',name,kubectl)
    meta=deployment.get('metadata',{})
    if meta.get('uid')!=plan.get('deployment_uid') or meta.get('resourceVersion')!=plan.get('deployment_resource_version'):
        raise UpgradeError('Deployment changed since planning: regenerate patch; nothing applied')
    index,app=find_api_container(deployment,plan['app_container'])
    if app['name']!=plan['app_container'] or discover_secret(app,plan['secret_name'])!=plan['secret_name']:
        raise UpgradeError('app container or Secret changed since planning')
    if not check_token(get_object(ns,'secret',plan['secret_name'],kubectl)):
        raise UpgradeError('worker token disappeared from Secret')
    expected,_=build_patch(deployment,plan['app_container'],plan['secret_name'],plan['converter_image'])
    if patch!=expected:raise UpgradeError('upgrade JSON Patch does not match allowlisted Deployment modifications')
    generated_dir=plan.get('generated_dir')
    if generated_dir:
        original=_generated_input(Path(generated_dir),ns,name,plan['secret_name'])[1]
        for filename,checksum in (plan.get('generated_sha256') or {}).items():
            if filename==CONVERTER_OVERLAY:
                p=Path(generated_dir)/filename
                if p.is_symlink() or (hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)!=checksum:
                    raise UpgradeError('generated overlay changed since planning; refuse to patch live cluster')
            elif filename not in original or hashlib.sha256(original[filename]).hexdigest()!=checksum:
                raise UpgradeError('generated files changed since planning; refuse to patch live cluster')
        _generated_secret_with_token(original['05-app-secret.yaml'].decode('utf8'),get_object(ns,'secret',plan['secret_name'],kubectl))
    # Server validation before the single atomic patch, then verify the
    # rollout; no secret, PostgreSQL, PVC, Service or Ingress operations.
    cmd=['-n',ns,'patch','deployment',name,'--type=json','--patch-file='+str((output/'converter-patch.json').resolve()),'-o','name']
    run_kubectl(cmd+['--dry-run=server'],kubectl=kubectl)
    run_kubectl(cmd,kubectl=kubectl)
    run_kubectl(['-n',ns,'rollout','status','deployment/'+name,'--timeout=180s'],kubectl=kubectl,timeout=190)
    if generated_dir:
        try:
            plan['generated_backup']=reconcile_generated(Path(generated_dir),ns,name,kubectl=kubectl,
                expected_hashes=plan.get('generated_sha256'))
        except (UpgradeError,OSError) as exc:
            raise UpgradeError('Live converter deployed, but generated manifest sync failed; run --sync-generated with --generated-dir after resolving: '+str(exc)) from exc
    return plan
