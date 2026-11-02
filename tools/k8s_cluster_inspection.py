"""Read-only discovery for importing an existing Quorivio Kubernetes installation.

Never reads Secret values, touches persistent volumes, or performs kubectl apply.
The resulting overrides are safe to review, not an immediately applicable
replacement: the wizard cannot reconstruct original database/auth credentials.
"""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path


def inspect_resources(namespace: str, name: str, kubectl: str = 'kubectl') -> dict:
    if not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?', namespace) or not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?', name):
        raise ValueError('Invalid Kubernetes namespace/name')
    def read(kind: str, resource_name: str):
        args = [kubectl, '-n', namespace, 'get', kind, resource_name, '-o', 'json', '--ignore-not-found=true', '--request-timeout=10s']
        try:
            result = subprocess.run(args, capture_output=True, text=True, timeout=15, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RuntimeError('Kubernetes read-only discovery failed; check kubectl context and access') from exc
        if result.returncode:
            # Do not echo cluster responses: they may include sensitive metadata.
            raise RuntimeError(f'Cannot inspect {kind}/{resource_name}; check read permissions and kubectl context')
        if not result.stdout.strip(): return None
        data = json.loads(result.stdout)
        return data if isinstance(data, dict) and data.get('kind') else None
    manifest={
        'deployment':read('deployment',name),
        'configmap':read('configmap',name+'-config'),
        'assets_pvc':read('pvc',name+'-assets'),
        'ingress':read('ingress',name),
        'clamav_deployment':read('deployment',name+'-clamav'),
        'clamav_service':read('service',name+'-clamav'),
        'postgres_statefulset':read('statefulset',name+'-postgres'),
        'postgres_service':read('service',name+'-postgres'),
    }
    return manifest


def derive_nonsecret_config(resources: dict, namespace: str, name: str) -> dict:
    overrides = {'namespace':namespace,'name':name}
    warnings=[]
    deployment = resources.get('deployment') or {}
    pod = deployment.get('spec',{}).get('template',{}).get('spec',{})
    containers=pod.get('containers') or []
    app=next((c for c in containers if c.get('name')==name),containers[0] if containers else {})
    if not deployment: warnings.append('Application Deployment not found')
    if app.get('image'):overrides['image']=app['image']
    if isinstance(deployment.get('spec',{}).get('replicas'),int):overrides['replicas']=deployment['spec']['replicas']
    selectors=pod.get('nodeSelector') or {}
    if selectors:overrides['app_node_selector']=','.join(f'{key}={value}' for key,value in sorted(selectors.items()))
    security=pod.get('securityContext') or {}
    if security.get('fsGroup') != 1000:warnings.append('Application Pod fsGroup is not 1000; verify CephFS/NFS write permissions')
    config=(resources.get('configmap') or {}).get('data') or {}
    if 'MAX_UPLOAD_MB' in config:
        try: overrides['max_upload_mb']=int(config['MAX_UPLOAD_MB'])
        except ValueError:warnings.append('MAX_UPLOAD_MB in ConfigMap is not numeric')
    if 'PORT' in config:
        try:overrides['container_port']=int(config['PORT'])
        except ValueError:warnings.append('PORT in ConfigMap is not numeric')
    if 'PUBLIC_BASE_URL' in config:
        from urllib.parse import urlsplit
        url=urlsplit(config['PUBLIC_BASE_URL']);
        if url.hostname:overrides['host']=url.hostname
        if url.scheme in ('http','https'):overrides['tls_termination']=url.scheme=='https'
    pvc=resources.get('assets_pvc') or {}
    spec=pvc.get('spec') or {}
    if spec.get('storageClassName'):overrides['asset_storage_class']=spec['storageClassName']
    modes=spec.get('accessModes') or []
    if modes and modes[0] in ('ReadWriteMany','ReadWriteOnce'):overrides['asset_access_mode']=modes[0]
    quantity=(spec.get('resources') or {}).get('requests',{}).get('storage')
    if quantity:overrides['asset_storage_size']=quantity
    if overrides.get('replicas',1)>1 and overrides.get('asset_access_mode','ReadWriteOnce')!='ReadWriteMany':
        warnings.append('Multiple app replicas with RWO storage: verify single-node scheduling and mount constraints')
    ingress=resources.get('ingress') or {}
    i_spec=ingress.get('spec') or {}
    if i_spec.get('ingressClassName'):overrides['ingress_class']=i_spec['ingressClassName']
    rules=i_spec.get('rules') or []
    if rules and rules[0].get('host'):overrides['host']=rules[0]['host']
    if i_spec.get('tls'):overrides['tls_termination']=True
    tls=i_spec.get('tls') or []
    if tls and tls[0].get('secretName'):overrides['tls_secret']=tls[0]['secretName']
    if 'haproxy' in overrides.get('ingress_class','').lower():overrides['ingress_controller']='haproxy'
    if 'nginx' in overrides.get('ingress_class','').lower():overrides['ingress_controller']='nginx'
    antivirus = resources.get('clamav_deployment') and resources.get('clamav_service')
    overrides['antivirus_mode']='managed' if antivirus else 'external'
    if not antivirus:
        host = config.get('CLAMAV_HOST','')
        if host and host!=name+'-clamav':overrides['antivirus_host']=host
        warnings.append('Managed ClamAV Deployment/Service pair not detected; do not assume uploads are protected')
    postgres=resources.get('postgres_statefulset')
    overrides['postgres_mode']='internal' if postgres else 'external'
    if not postgres:
        if config.get('PGHOST'):overrides['postgres_host']=config['PGHOST']
        warnings.append('PostgreSQL StatefulSet not found under wizard name; check the existing DB independently')
    else:
        c=postgres.get('spec',{}).get('template',{}).get('spec',{}).get('containers',[])
        if c and c[0].get('image'):overrides['postgres_image']=c[0]['image']
    warnings.append('Secrets are intentionally NOT imported: preserve existing Kubernetes Secret and original credentials')
    warnings.append('Read-only discovery never updates existing PVC, database, Deployment or Ingress')
    return {'overrides':overrides,'warnings':warnings,
            'resource_presence':{key:bool(value) for key,value in resources.items()}}


def save_report(output:Path,report:dict):
    from k8s_wizard import guarded_output_directory,secure_write
    out=guarded_output_directory(output)
    secure_write(out/'quorivio-cluster-discovery.json',json.dumps(report,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
