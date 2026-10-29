#!/usr/bin/env python3
"""Standalone, deterministic, idempotent Quorivio Kubernetes Kustomize generator (stdlib)."""
import argparse, json, re, sys, os, secrets, base64, urllib.parse, tempfile
from pathlib import Path

DEFAULTS = {'namespace':'quorivio','name':'quorivio','image':'desalvo/quorivio:latest','host':'quorivio.example.org','replicas':1,'max_upload_mb':100,'container_port':8080,'postgres_mode':'internal','postgres_image':'postgres:18.6-alpine','postgres_host':'postgresql','postgres_port':5432,'postgres_sslmode':'require','ingress_controller':'nginx','haproxy_variant':'community','ingress_class':'','postgres_host':'postgresql','postgres_database':'quorivio','postgres_user':'quorivio','secret_name':'quorivio-app-secrets','tls_secret':'','tls_termination':True,'app_node_selector':'','postgres_node_selector':'','admin_email':'admin@example.org','admin_password':'','auth_secret':'','postgres_password':'','storage_class':'','asset_storage_class':'','asset_storage_size':'10Gi','asset_access_mode':'ReadWriteOnce','cpu_request':'100m','memory_request':'256Mi','cpu_limit':'1000m','memory_limit':'1Gi'}
FIELDS = tuple(DEFAULTS)
def quote(s): return json.dumps(str(s), ensure_ascii=False)
def validate(cfg):
    for k in cfg:
        if k not in DEFAULTS: raise ValueError(f'Unknown key: {k}')
    if not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?', cfg['name']) or len(cfg['name'])>63: raise ValueError('Invalid Kubernetes name')
    if not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?',cfg['namespace']):raise ValueError('Invalid namespace')
    if not re.fullmatch(r'[a-zA-Z0-9.-]+',cfg['host']) or '.' not in cfg['host']:raise ValueError('Invalid DNS host')
    if not re.fullmatch(r'[A-Za-z0-9._:/@+-]+',cfg['image']):raise ValueError('Invalid image reference')
    if not re.fullmatch(r'[A-Za-z0-9._:/@+-]+',cfg['postgres_image']):raise ValueError('Invalid PostgreSQL image')
    if cfg['ingress_class'] and not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?',cfg['ingress_class']):raise ValueError('Invalid ingress class')
    if cfg['storage_class'] and not re.fullmatch(r'[a-z0-9]([-a-z0-9.]*[a-z0-9])?',cfg['storage_class']):raise ValueError('Invalid storage class')
    if cfg['asset_storage_class'] and not re.fullmatch(r'[a-z0-9]([-a-z0-9.]*[a-z0-9])?',cfg['asset_storage_class']):raise ValueError('Invalid asset storage class')
    if not re.fullmatch(r'[1-9][0-9]*(Mi|Gi|Ti)',cfg['asset_storage_size']):raise ValueError('Invalid asset storage size')
    if cfg['asset_access_mode'] not in ('ReadWriteOnce','ReadWriteMany'):raise ValueError('Invalid asset access mode')
    if cfg['postgres_mode'] not in ('internal','external'):raise ValueError('Invalid postgres_mode')
    if cfg['ingress_controller'] not in ('nginx','haproxy'):raise ValueError('Invalid ingress_controller')
    if cfg['haproxy_variant'] not in ('community','haproxytech'):raise ValueError('Invalid haproxy_variant')
    if cfg['postgres_sslmode'] not in ('require','verify-full','verify-ca','disable'):raise ValueError('Invalid sslmode')
    if cfg['postgres_mode']=='external' and (cfg['postgres_host']=='postgresql' or cfg['postgres_sslmode']=='disable'):raise ValueError('External PostgreSQL requires dedicated host and TLS')
    if type(cfg['postgres_port']) is not int or not 1<=cfg['postgres_port']<=65535:raise ValueError('Invalid postgres_port')
    if type(cfg['max_upload_mb']) is not int or not 1<=cfg['max_upload_mb']<=1024:raise ValueError('max_upload_mb must be 1..1024')
    if type(cfg['replicas']) is not int or not 1 <= cfg['replicas'] <= 20: raise ValueError('replicas must be 1-20')
    if type(cfg['container_port']) is not int or not 1 <= cfg['container_port'] <= 65535: raise ValueError('Invalid port')
    if type(cfg['postgres_port']) is not int or not 1 <= cfg['postgres_port'] <= 65535: raise ValueError('Invalid postgres_port')
    if cfg['replicas'] > 1 and cfg['asset_access_mode'] != 'ReadWriteMany':raise ValueError('Multiple API replicas require ReadWriteMany asset storage')


    if not isinstance(cfg['tls_termination'],bool): raise ValueError('tls_termination must be true or false')
    for key in ('app_node_selector','postgres_node_selector'):
        parse_node_selector(cfg[key])
    if cfg['tls_secret'] and not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?',cfg['tls_secret']): raise ValueError('Invalid TLS secret')
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+',cfg['admin_email']): raise ValueError('Invalid admin_email')
    for k in ('admin_password','auth_secret','postgres_password'):
        if cfg[k] and (len(cfg[k]) < (32 if k=='auth_secret' else 12) or any(x in cfg[k] for x in '\r\n')): raise ValueError(f'Invalid or short {k}')
    for k in ('postgres_host','postgres_database','postgres_user','secret_name','cpu_request','memory_request','cpu_limit','memory_limit'):
        if not re.fullmatch('[A-Za-z0-9._/-]+',str(cfg[k])):raise ValueError(f'Invalid value for {k}')
    return cfg

def parse_node_selector(value):
    """Parse comma separated Kubernetes label selectors into a deterministic map."""
    result={}
    if not value: return result
    for item in value.split(','):
        if '=' not in item: raise ValueError('nodeSelector requires key=value entries')
        key,val=(part.strip() for part in item.split('=',1))
        dns=r'[a-z0-9]([-a-z0-9.]*[a-z0-9])?'
        label=r'[A-Za-z0-9]([-A-Za-z0-9_.]*[A-Za-z0-9])?'
        if '/' in key:
            prefix,name=key.split('/',1)
            if len(prefix)>253 or not re.fullmatch(dns,prefix) or any(len(x)>63 for x in prefix.split('.')): raise ValueError('Invalid nodeSelector prefix')
        else: name=key
        if not name or len(name)>63 or not re.fullmatch(label,name) or len(val)>63 or (val and not re.fullmatch(label,val)): raise ValueError('Invalid nodeSelector label')
        if key in result: raise ValueError('Duplicate nodeSelector label')
        result[key]=val
    return dict(sorted(result.items()))

def selector_yaml(value,indent=6):
    labels=parse_node_selector(value)
    if not labels:return ''
    pad=' '*indent
    return pad+'nodeSelector:\n'+''.join(pad+'  '+quote(k)+': '+quote(v)+'\n' for k,v in labels.items())

def checked_file(path):
    """Never read a symlinked credential receipt or a nonregular file."""
    import stat
    if path.is_symlink(): raise ValueError('Refusing symlink in generated output')
    if path.exists() and not stat.S_ISREG(path.lstat().st_mode):
        raise ValueError('Refusing non-file generated output')


def secure_write(path, content, private=True):
    """Atomically replace a manifest without following existing symlinks.

    Never truncate an existing secret: a crash leaves the previous complete
    credentials or the new complete credentials, not a partial YAML/JSON.
    """
    checked_file(path)
    mode = 0o600 if private else 0o644
    descriptor, temporary = tempfile.mkstemp(prefix='.quorivio-atomic-', dir=str(path.parent))
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        checked_file(path)
        os.replace(temporary, path)
    finally:
        if os.path.lexists(temporary): os.unlink(temporary)

def resolve_credentials(cfg,out):
    cfg=dict(cfg)
    saved=out/'quorivio-overrides.json'
    checked_file(saved)
    if saved.exists():
        previous=json.loads(saved.read_text())
        for key in ('admin_password','auth_secret','postgres_password'):
            if not cfg[key] and previous.get(key): cfg[key]=previous[key]
    if not cfg['admin_password']: cfg['admin_password']=secrets.token_urlsafe(24)
    if not cfg['auth_secret']: cfg['auth_secret']=secrets.token_urlsafe(48)
    if cfg['postgres_mode']=='internal' and not cfg['postgres_password']:
        cfg['postgres_password']=secrets.token_urlsafe(32)
    if cfg['postgres_mode']=='external' and not cfg['postgres_password']:
        raise ValueError('External PostgreSQL requires postgres_password (existing database credential)')
    validate(cfg)
    return cfg

def guarded_output_directory(out):
    """Refuse output redirected through any pre-existing directory symlink.

    Manifest generation writes credentials and must never silently follow a
    symlink planted at the output path or in its directory chain. This is not
    a substitute for exclusive ownership of the workspace on a shared host.
    """
    out=Path(out).absolute()
    for part in (out,*out.parents):
        if part.is_symlink():
            raise ValueError('Refusing symlink in Kubernetes output directory')
    if out.exists() and not out.is_dir():
        raise ValueError('Kubernetes output path must be a directory')
    out.mkdir(parents=True,exist_ok=True,mode=0o700)
    if not out.is_dir() or out.is_symlink():
        raise ValueError('Unsafe Kubernetes output directory')
    return out

def generate(cfg,out):
    out=guarded_output_directory(out)
    cfg=resolve_credentials(cfg,out)
    name=cfg['name'];ns=cfg['namespace'];port=int(cfg['container_port'])
    klass=cfg['ingress_class'] or cfg['ingress_controller']
    upload_annotation=('    nginx.ingress.kubernetes.io/proxy-body-size: '+quote(str(cfg['max_upload_mb'])+'m')+'\n') if cfg['ingress_controller']=='nginx' else (('    haproxy.org/max-body-size: '+quote(str(cfg['max_upload_mb']*1024*1024)+'')+'\n') if cfg['haproxy_variant']=='haproxytech' else '')
    legacy= ('    kubernetes.io/ingress.class: '+quote(klass)+'\n' if cfg['haproxy_variant']=='community' else '    haproxy.org/ingress.class: '+quote(klass)+'\n') if cfg['ingress_controller']=='haproxy' else ''
    dbhost=(name+'-postgres') if cfg['postgres_mode']=='internal' else cfg['postgres_host']
    db_url=('postgresql://'+urllib.parse.quote(cfg['postgres_user'],safe='')+':'+urllib.parse.quote(cfg['postgres_password'],safe='')+'@'+dbhost+':'+str(cfg['postgres_port'])+'/'+urllib.parse.quote(cfg['postgres_database'],safe='')+'?sslmode='+('disable' if cfg['postgres_mode']=='internal' else cfg['postgres_sslmode']))
    secret_data={'DATABASE_URL':db_url,'AUTH_SECRET':cfg['auth_secret'],'ADMIN_EMAIL':cfg['admin_email'],'ADMIN_PASSWORD':cfg['admin_password']}
    if cfg['postgres_mode']=='internal':secret_data['POSTGRES_PASSWORD']=cfg['postgres_password']
    files={
      '00-namespace.yaml':f'apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {ns}\n',
      '05-app-secret.yaml':'apiVersion: v1\nkind: Secret\nmetadata:\n  name: '+name.replace('\n','')+'-PLACEHOLDER\n',
      '10-configmap.yaml':f'''apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}-config
  namespace: {ns}
data:
  NODE_ENV: production
  MAX_UPLOAD_MB: {quote(cfg['max_upload_mb'])}
  QUORIVIO_ASSET_DIR: /app/assets
  PORT: {quote(port)}
  PUBLIC_BASE_URL: {quote('https://'+cfg['host'])}
  PGHOST: {quote(dbhost)}
  PGPORT: {quote(cfg['postgres_port'])}
  PGDATABASE: {quote(cfg['postgres_database'])}
  PGUSER: {quote(cfg['postgres_user'])}
  PGSSLMODE: {quote('disable' if cfg['postgres_mode']=='internal' else cfg['postgres_sslmode'])}
''',
      '20-deployment.yaml':f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {ns}
spec:
  replicas: {cfg['replicas']}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
{selector_yaml(cfg['app_node_selector'])}{('      topologySpreadConstraints:' + chr(10) + '        - maxSkew: 1' + chr(10) + '          topologyKey: kubernetes.io/hostname' + chr(10) + '          whenUnsatisfiable: ScheduleAnyway' + chr(10) + '          labelSelector:' + chr(10) + '            matchLabels:' + chr(10) + '              app: ' + name + chr(10)) if cfg['replicas'] > 1 else ''}      terminationGracePeriodSeconds: 45
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        fsGroupChangePolicy: OnRootMismatch
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: {name}
          image: {cfg['image']}
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: {port}
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {cfg['secret_name']}
                  key: DATABASE_URL
          envFrom:
            - configMapRef:
                name: {name}-config
            - secretRef:
                name: {cfg['secret_name']}
          readinessProbe:
            httpGet:
              path: /api/health/ready
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /api/health/live
              port: http
            initialDelaySeconds: 15
            periodSeconds: 20
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop: [ALL]
            readOnlyRootFilesystem: true
          volumeMounts:
            - name: assets
              mountPath: /app/assets
          resources:
            requests:
              cpu: {quote(cfg['cpu_request'])}
              memory: {quote(cfg['memory_request'])}
            limits:
              cpu: {quote(cfg['cpu_limit'])}
              memory: {quote(cfg['memory_limit'])}
      volumes:
        - name: assets
          persistentVolumeClaim:
            claimName: {name}-assets
''',
      '15-assets-pvc.yaml':f'''apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {name}-assets
  namespace: {ns}
spec:
  accessModes: [{cfg['asset_access_mode']}]
{('  storageClassName: '+cfg['asset_storage_class']+chr(10)) if cfg['asset_storage_class'] else ''}  resources:
    requests:
      storage: {cfg['asset_storage_size']}
''',
      '30-service.yaml':f'''apiVersion: v1
kind: Service
metadata:
  name: {name}
  namespace: {ns}
spec:
  type: ClusterIP
  selector:
    app: {name}
  ports:
    - name: http
      port: 80
      targetPort: http
''',
      '40-ingress.yaml':f'''apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {name}
  namespace: {ns}
{('  annotations:' + chr(10) + legacy + upload_annotation) if (legacy or upload_annotation) else ''}spec:
  ingressClassName: {klass}
{('  tls:' + chr(10) + '    - hosts: [' + cfg['host'] + ']' + chr(10) + ('      secretName: ' + cfg['tls_secret'] + chr(10) if cfg['tls_secret'] else '')) if cfg['tls_termination'] else ''}
  rules:
    - host: {cfg['host']}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {name}
                port:
                  name: http
''',
      'kustomization.yaml':f'''apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - 00-namespace.yaml
  - 10-configmap.yaml
  - 15-assets-pvc.yaml
  - 20-deployment.yaml
  - 30-service.yaml
  - 40-ingress.yaml
'''
    }
    if cfg['replicas'] > 1:
        files['25-disruption-budget.yaml']=f"""apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {name}-availability
  namespace: {ns}
spec:
  minAvailable: {cfg['replicas']-1}
  selector:
    matchLabels:
      app: {name}
"""
        files['kustomization.yaml']=files['kustomization.yaml'].replace('  - 30-service.yaml\n','  - 25-disruption-budget.yaml\n  - 30-service.yaml\n')
    else:
        (out/'25-disruption-budget.yaml').unlink(missing_ok=True)
    files['05-app-secret.yaml']='apiVersion: v1\nkind: Secret\nmetadata:\n  name: '+cfg['secret_name']+'\n  namespace: '+ns+'\ntype: Opaque\ndata:\n'+''.join('  '+k+': '+base64.b64encode(v.encode()).decode()+'\n' for k,v in sorted(secret_data.items()))
    files['kustomization.yaml']=files['kustomization.yaml'].replace('  - 10-configmap.yaml\n','  - 05-app-secret.yaml\n  - 10-configmap.yaml\n')
    if cfg['postgres_mode']=='internal':
        files.update(postgres_resources(cfg,name,ns))
        files['kustomization.yaml']=files['kustomization.yaml'].replace('  - 10-configmap.yaml\n','  - 10-configmap.yaml\n  - 11-postgres-service.yaml\n  - 12-postgres-statefulset.yaml\n')
    # Remove obsolete generated database resources when switching internal -> external.
    for old in ('11-postgres-service.yaml','12-postgres-statefulset.yaml'):
        if old not in files: (out/old).unlink(missing_ok=True)
    for filename,body in files.items():
        secure_write(out/filename,body,private=filename=='05-app-secret.yaml')
    # Store ONLY changed custom values. No passwords/tokens are collected by the wizard.
    overrides={k:cfg[k] for k in FIELDS if cfg[k]!=DEFAULTS[k]}
    secure_write(out/'quorivio-overrides.json',json.dumps(overrides,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    return list(files)

def postgres_resources(cfg,name,ns):
    storage=('        storageClassName: '+cfg['storage_class']+'\n') if cfg['storage_class'] else ''
    service=f"""apiVersion: v1
kind: Service
metadata:
  name: {name}-postgres
  namespace: {ns}
spec:
  clusterIP: None
  selector:
    app: {name}-postgres
  ports:
    - name: pg
      port: 5432
      targetPort: pg
"""
    stateful=f"""apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: {name}-postgres
  namespace: {ns}
spec:
  serviceName: {name}-postgres
  replicas: 1
  selector:
    matchLabels:
      app: {name}-postgres
  template:
    metadata:
      labels:
        app: {name}-postgres
    spec:
{selector_yaml(cfg['postgres_node_selector'])}      automountServiceAccountToken: false
      securityContext:
        runAsUser: 999
        runAsGroup: 999
        fsGroup: 999
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: postgres
          image: {cfg['postgres_image']}
          ports:
            - name: pg
              containerPort: 5432
          env:
            - name: POSTGRES_DB
              value: {quote(cfg['postgres_database'])}
            - name: POSTGRES_USER
              value: {quote(cfg['postgres_user'])}
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {cfg['secret_name']}
                  key: POSTGRES_PASSWORD
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql
          readinessProbe:
            exec:
              command: [sh, -c, 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"']
            periodSeconds: 10
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop: [ALL]
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 1000m
              memory: 1Gi
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: [ReadWriteOnce]
{storage}        resources:
          requests:
            storage: 10Gi
"""
    return {'11-postgres-service.yaml':service,'12-postgres-statefulset.yaml':stateful}

def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--unattended',action='store_true',help='Use defaults plus overrides without prompting')
    a.add_argument('--output',default='k8s-generated',help='Target directory for deterministic Kustomize manifests')
    a.add_argument('--values',help='Existing JSON with custom overrides, e.g. saved quorivio-overrides.json')
    a.add_argument('--set',action='append',default=[],metavar='KEY=VALUE')
    args=a.parse_args(argv)
    cfg=dict(DEFAULTS);out=Path(args.output)
    try: guarded_output_directory(out)
    except ValueError as e: a.error(str(e))
    saved=out/'quorivio-overrides.json'
    checked_file(saved)
    if saved.is_file(): cfg.update(json.loads(saved.read_text()))
    if args.values:cfg.update(json.loads(Path(args.values).read_text()))
    print('Quorivio Kubernetes defaults + existing overrides:')
    for k in FIELDS:print(f'  {k}: '+ ('[configured]' if cfg[k] else '[auto-generated]') if k in ('admin_password','auth_secret','postgres_password') else f'  {k}: {cfg[k]}')
    if not args.unattended:
        if not sys.stdin.isatty():a.error('Interactive mode requires a TTY; use --unattended')
        for k in FIELDS:
            val=input(f'{k} [{cfg[k]}]: ').strip()
            if val:cfg[k]=val
    for entry in args.set:
        if '=' not in entry:a.error('--set requires KEY=VALUE')
        k,v=entry.split('=',1)
        if k=='tls_termination':
            if v.lower() not in ('true','false'):a.error('tls_termination requires true/false')
            cfg[k]=v.lower()=='true'
        elif k in ('replicas','max_upload_mb','container_port','postgres_port'):
            try: cfg[k]=int(v)
            except ValueError: a.error(f'{k} must be an integer')
        else: cfg[k]=v
    try:validate(cfg)
    except ValueError as e:a.error(str(e))
    generate(cfg,out)
    print(f'Generated Kustomize base in {out} (never applied).')
    print('Application Secret generated; keep overrides and 05-app-secret.yaml private (0600). Never commit them to Git.')
    print('TLS uses tls_secret when provided, otherwise the ingress controller default certificate.')
    return 0
if __name__=='__main__':raise SystemExit(main())
