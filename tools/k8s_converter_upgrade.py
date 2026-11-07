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
import os
import re
import secrets
import stat
import subprocess
from pathlib import Path

NAME = re.compile(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?\Z')
IMAGE = re.compile(r'[A-Za-z0-9][A-Za-z0-9._:/@+\-]*\Z')
PLAN_SCHEMA = 'quorivio-k8s-converter-upgrade-v1'
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
    strategy=deployment.get('spec',{}).get('strategy') or {}
    unavailable=(strategy.get('rollingUpdate') or {}).get('maxUnavailable',0)
    if strategy.get('type') == 'Recreate' or unavailable not in (0,'0','0%'):
        raise UpgradeError('non-zero maxUnavailable or Recreate strategy; refuse potential availability disruption')
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
                    secret_name: str | None=None, kubectl: str='kubectl') -> dict:
    valid_name(namespace,'Namespace');valid_name(deployment_name,'Deployment')
    current_context=kube_context(kubectl)
    deployment=get_object(namespace,'deployment',deployment_name,kubectl)
    _,app=find_api_container(deployment,app_container)
    secret_name=discover_secret(app,secret_name)
    secret=get_object(namespace,'secret',secret_name,kubectl)
    if not check_token(secret):
        raise UpgradeError('existing app Secret lacks QUORIVIO_WORKER_TOKEN; run --ensure-converter-token first')
    patch,identity=build_patch(deployment,app_container,secret_name,image)
    output=_fresh_directory(output)
    encoded=json.dumps(patch,indent=2,ensure_ascii=False)+'\n'
    plan={'schema':PLAN_SCHEMA,'context':current_context,'namespace':namespace,'deployment':deployment_name,
          'converter_image':image,**identity,'patch_sha256':hashlib.sha256(encoded.encode('utf8')).hexdigest()}
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
        'The wizard never edits the initial Kustomize base or its Secrets.\n')
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
    # Server validation before the single atomic patch, then verify the
    # rollout; no secret, PostgreSQL, PVC, Service or Ingress operations.
    cmd=['-n',ns,'patch','deployment',name,'--type=json','--patch-file='+str((output/'converter-patch.json').resolve()),'-o','name']
    run_kubectl(cmd+['--dry-run=server'],kubectl=kubectl)
    run_kubectl(cmd,kubectl=kubectl)
    run_kubectl(['-n',ns,'rollout','status','deployment/'+name,'--timeout=180s'],kubectl=kubectl,timeout=190)
    return plan
