#!/usr/bin/env python3
"""Standalone, deterministic, idempotent Quorivio Kubernetes Kustomize generator (stdlib)."""
import argparse, json, re, sys
from pathlib import Path

DEFAULTS = {'namespace':'quorivio','name':'quorivio','image':'desalvo/quorivio:latest','host':'quorivio.example.org','replicas':1,'container_port':8080,'postgres_mode':'internal','postgres_image':'postgres:18.6-alpine','postgres_host':'postgresql','postgres_port':5432,'postgres_sslmode':'require','ingress_controller':'nginx','haproxy_variant':'community','ingress_class':'','postgres_host':'postgresql','postgres_database':'quorivio','postgres_user':'quorivio','secret_name':'quorivio-app-secrets','tls_secret':'quorivio-tls','storage_class':'','cpu_request':'100m','memory_request':'256Mi','cpu_limit':'1000m','memory_limit':'1Gi'}
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
    if cfg['postgres_mode'] not in ('internal','external'):raise ValueError('Invalid postgres_mode')
    if cfg['ingress_controller'] not in ('nginx','haproxy'):raise ValueError('Invalid ingress_controller')
    if cfg['haproxy_variant'] not in ('community','haproxytech'):raise ValueError('Invalid haproxy_variant')
    if cfg['postgres_sslmode'] not in ('require','verify-full','verify-ca','disable'):raise ValueError('Invalid sslmode')
    if cfg['postgres_mode']=='external' and (cfg['postgres_host']=='postgresql' or cfg['postgres_sslmode']=='disable'):raise ValueError('External PostgreSQL requires dedicated host and TLS')
    if not 1<=int(cfg['postgres_port'])<=65535:raise ValueError('Invalid postgres_port')
    if int(cfg['replicas']) != 1:raise ValueError('Only one API replica supported until a shared WebSocket event bus exists')
    if int(cfg['replicas'])<1 or int(cfg['replicas'])>20:raise ValueError('replicas must be 1-20')
    if not 1<=int(cfg['container_port'])<=65535:raise ValueError('Invalid port')
    for k in ('postgres_host','postgres_database','postgres_user','secret_name','tls_secret','cpu_request','memory_request','cpu_limit','memory_limit'):
        if not re.fullmatch('[A-Za-z0-9._/-]+',str(cfg[k])):raise ValueError(f'Invalid value for {k}')
    return cfg

def generate(cfg,out):
    out.mkdir(parents=True,exist_ok=True)
    name=cfg['name'];ns=cfg['namespace'];port=int(cfg['container_port'])
    klass=cfg['ingress_class'] or cfg['ingress_controller']
    legacy= ('    kubernetes.io/ingress.class: '+quote(klass)+'\n' if cfg['haproxy_variant']=='community' else '    haproxy.org/ingress.class: '+quote(klass)+'\n') if cfg['ingress_controller']=='haproxy' else ''
    dbhost=(name+'-postgres') if cfg['postgres_mode']=='internal' else cfg['postgres_host']
    files={
      '00-namespace.yaml':f'apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {ns}\n',
      '10-configmap.yaml':f'''apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}-config
  namespace: {ns}
data:
  NODE_ENV: production
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
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
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
          resources:
            requests:
              cpu: {quote(cfg['cpu_request'])}
              memory: {quote(cfg['memory_request'])}
            limits:
              cpu: {quote(cfg['cpu_limit'])}
              memory: {quote(cfg['memory_limit'])}
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
{('  annotations:' + chr(10) + legacy) if legacy else ''}spec:
  ingressClassName: {klass}
  tls:
    - hosts: [{cfg['host']}]
      secretName: {cfg['tls_secret']}
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
  - 20-deployment.yaml
  - 30-service.yaml
  - 40-ingress.yaml
'''
    }
    if cfg['postgres_mode']=='internal':
        files.update(postgres_resources(cfg,name,ns))
        files['kustomization.yaml']=files['kustomization.yaml'].replace('  - 10-configmap.yaml\n','  - 10-configmap.yaml\n  - 11-postgres-service.yaml\n  - 12-postgres-statefulset.yaml\n')
    # Remove obsolete generated database resources when switching internal -> external.
    for old in ('11-postgres-service.yaml','12-postgres-statefulset.yaml'):
        if old not in files: (out/old).unlink(missing_ok=True)
    for filename,body in files.items(): (out/filename).write_text(body,encoding='utf-8')
    # Store ONLY changed custom values. No passwords/tokens are collected by the wizard.
    overrides={k:cfg[k] for k in FIELDS if cfg[k]!=DEFAULTS[k]}
    (out/'quorivio-overrides.json').write_text(json.dumps(overrides,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
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
      automountServiceAccountToken: false
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
    saved=out/'quorivio-overrides.json'
    if saved.is_file(): cfg.update(json.loads(saved.read_text()))
    if args.values:cfg.update(json.loads(Path(args.values).read_text()))
    print('Quorivio Kubernetes defaults + existing overrides:')
    for k in FIELDS:print(f'  {k}: {cfg[k]}')
    if not args.unattended:
        if not sys.stdin.isatty():a.error('Interactive mode requires a TTY; use --unattended')
        for k in FIELDS:
            val=input(f'{k} [{cfg[k]}]: ').strip()
            if val:cfg[k]=val
    for entry in args.set:
        if '=' not in entry:a.error('--set requires KEY=VALUE')
        k,v=entry.split('=',1);cfg[k]=v
    try:validate(cfg)
    except ValueError as e:a.error(str(e))
    generate(cfg,out)
    print(f'Generated Kustomize base in {out} (never applied).')
    print('Provide pre-existing Kubernetes Secret and ingress TLS Secret before deployment.')
    return 0
if __name__=='__main__':raise SystemExit(main())
