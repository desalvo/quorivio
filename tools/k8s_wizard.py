#!/usr/bin/env python3
"""Standalone, deterministic, idempotent Quorivio Kubernetes Kustomize generator (stdlib)."""
import argparse, json, re, sys, os, secrets, base64, urllib.parse, tempfile, types, hashlib, importlib
from pathlib import Path
import stat
import urllib.request
import urllib.error

# This single-file wizard is the release unit.  Its upstream is intentionally
# fixed to the official public repository: never accept a URL from CLI input.
WIZARD_VERSION = '0.1.0-dev-rc259'
WIZARD_UPSTREAM_URL = 'https://raw.githubusercontent.com/desalvo/quorivio/main/tools/k8s_wizard.py'
WIZARD_MAX_DOWNLOAD_BYTES = 2 * 1024 * 1024
_WIZARD_RESTART_GUARD = 'QUORIVIO_WIZARD_RESTARTED_AFTER_UPDATE'

class WizardUpdateError(RuntimeError):
    """No cluster operation may follow an unsuccessful required update check."""


def _wizard_version_from_source(source: str):
    """Extract only the literal release marker, never execute remote code to inspect it."""
    match = re.search(r"(?m)^WIZARD_VERSION\s*=\s*['\"](0\.1\.0-dev-rc([0-9]+))['\"]\s*$", source)
    return (match.group(1), int(match.group(2))) if match else None


def _download_official_wizard():
    """Retrieve a bounded Python source over verified HTTPS from official main."""
    request = urllib.request.Request(WIZARD_UPSTREAM_URL, headers={
        'User-Agent': 'Quorivio-Kubernetes-Wizard/' + WIZARD_VERSION,
        'Cache-Control': 'no-cache',
    })
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            resolved = urllib.parse.urlsplit(response.geturl())
            if resolved.scheme != 'https' or resolved.hostname != 'raw.githubusercontent.com' or response.geturl() != WIZARD_UPSTREAM_URL:
                raise WizardUpdateError('GitHub wizard source redirected outside trusted HTTPS origin')
            body = response.read(WIZARD_MAX_DOWNLOAD_BYTES + 1)
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        raise WizardUpdateError('Cannot securely check official GitHub for the latest wizard') from exc
    if not body or len(body) > WIZARD_MAX_DOWNLOAD_BYTES:
        raise WizardUpdateError('GitHub wizard is empty or exceeds safe source size')
    return body


def _maybe_install_official_update(script_path: Path) -> bool:
    """Atomically install a newer official standalone wizard; never downgrade.

    Only a complete, syntactically valid, explicitly versioned release is
    eligible.  No Kubernetes call occurs until this finishes.  A concurrent
    update or a symlinked executable is rejected rather than overwritten.
    """
    script_path = Path(script_path).absolute()
    if script_path.is_symlink() or not script_path.is_file():
        raise WizardUpdateError('Refusing to replace a symlinked or missing wizard')
    original = script_path.read_bytes()
    remote = _download_official_wizard()
    try:
        text = remote.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise WizardUpdateError('GitHub wizard is not UTF-8 Python source') from exc
    release = _wizard_version_from_source(text)
    if release is None:
        # RC258 and earlier had no version marker.  Refuse to replace a newer,
        # standalone wizard with an unverifiable, potentially older script.
        print('Wizard: upstream has no comparable release marker; keeping installed '+WIZARD_VERSION, file=sys.stderr)
        return False
    local = _wizard_version_from_source(original.decode('utf-8'))
    if local is None:
        raise WizardUpdateError('Installed wizard has no valid release marker')
    if release[1] < local[1]:
        print('Wizard: GitHub main is older than installed '+WIZARD_VERSION+'; refusing downgrade', file=sys.stderr)
        return False
    if remote == original:
        return False
    if '_STANDALONE_COMPONENT_SOURCES' not in text or "if __name__=='__main__'" not in text:
        raise WizardUpdateError('Upstream update is not a complete standalone wizard')
    try:
        compile(text, str(script_path), 'exec')
    except SyntaxError as exc:
        raise WizardUpdateError('Upstream wizard failed Python syntax validation') from exc
    if script_path.read_bytes() != original:
        raise WizardUpdateError('Wizard file changed during update; refusing concurrent overwrite')
    current_mode = stat.S_IMODE(script_path.stat().st_mode)
    handle, temporary = tempfile.mkstemp(prefix='.quorivio-wizard-update-', dir=str(script_path.parent))
    try:
        os.fchmod(handle, current_mode)
        with os.fdopen(handle, 'wb') as output:
            output.write(remote)
            output.flush()
            os.fsync(output.fileno())
        if script_path.is_symlink() or script_path.read_bytes() != original:
            raise WizardUpdateError('Wizard path changed during update')
        os.replace(temporary, script_path)
    except OSError as exc:
        raise WizardUpdateError('Cannot atomically replace wizard; check directory permissions') from exc
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)
    print('Wizard updated from official GitHub main: '+local[0]+' -> '+release[0]+' (SHA-256 '+hashlib.sha256(remote).hexdigest()[:16]+')', file=sys.stderr)
    return True


def _run_standalone_cli():
    args = sys.argv[1:]
    # Pure local metadata and help must also work offline; all operational
    # commands check upstream unless explicitly overridden by the operator.
    bypass = any(flag in args for flag in ('--version', '--help', '-h', '--no-self-update'))
    if not bypass and os.environ.get(_WIZARD_RESTART_GUARD) != '1':
        try:
            if _maybe_install_official_update(Path(__file__)):
                # Preserve all arguments, the kubeconfig environment and the
                # interpreter.  A one-shot guard prevents re-exec loops.
                os.environ[_WIZARD_RESTART_GUARD] = '1'
                os.execv(sys.executable, [sys.executable, str(Path(__file__).absolute()), *args])
        except WizardUpdateError as exc:
            print('Wizard self-update blocked: '+str(exc), file=sys.stderr)
            print('If explicitly working offline, rerun with --no-self-update.', file=sys.stderr)
            return 3
    return main(args)

DEFAULTS = {'namespace':'quorivio','name':'quorivio','image':'desalvo/quorivio:latest','host':'quorivio.example.org','replicas':1,'enforce_node_diversity':False,'max_upload_mb':100,'antivirus_mode':'managed','antivirus_image':'clamav/clamav:stable','antivirus_host':'','container_port':8080,'postgres_mode':'internal','postgres_image':'postgres:18.6-alpine','postgres_host':'postgresql','postgres_port':5432,'postgres_sslmode':'require','ingress_controller':'nginx','haproxy_variant':'community','ingress_class':'','postgres_host':'postgresql','postgres_database':'quorivio','postgres_user':'quorivio','secret_name':'quorivio-app-secrets','tls_secret':'','tls_termination':True,'app_node_selector':'','postgres_node_selector':'','admin_email':'admin@example.org','admin_password':'','auth_secret':'','postgres_password':'','storage_class':'','asset_storage_class':'','asset_storage_size':'10Gi','asset_access_mode':'ReadWriteOnce','cpu_request':'100m','memory_request':'256Mi','cpu_limit':'1000m','memory_limit':'1Gi'}
FIELDS = tuple(DEFAULTS)
def quote(s): return json.dumps(str(s), ensure_ascii=False)
def validate(cfg):
    for k in cfg:
        if k not in DEFAULTS: raise ValueError(f'Unknown key: {k}')
    if not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?', cfg['name']) or len(cfg['name'])>63: raise ValueError('Invalid Kubernetes name')
    if not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?',cfg['namespace']):raise ValueError('Invalid namespace')
    if not re.fullmatch(r'[a-zA-Z0-9.-]+',cfg['host']) or '.' not in cfg['host']:raise ValueError('Invalid DNS host')
    if not re.fullmatch(r'[A-Za-z0-9._:/@+-]+',cfg['image']):raise ValueError('Invalid image reference')
    if cfg['antivirus_mode'] not in ('managed','external'):raise ValueError('Invalid antivirus mode')
    if not re.fullmatch(r'[A-Za-z0-9._:/@+-]+',cfg['antivirus_image']):raise ValueError('Invalid antivirus image')
    if cfg['antivirus_mode']=='external':
        if (not cfg['antivirus_host'] or len(cfg['antivirus_host'])>253 or any(
            not re.fullmatch(r'[a-z0-9]([-a-z0-9]*[a-z0-9])?', part) or len(part)>63
            for part in cfg['antivirus_host'].split('.'))):raise ValueError('External antivirus host is required')
    elif cfg['antivirus_host']:raise ValueError('Managed antivirus host is derived automatically')
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
    if type(cfg['enforce_node_diversity']) is not bool: raise ValueError('enforce_node_diversity must be true or false')
    if cfg['enforce_node_diversity'] and cfg['replicas'] < 2: raise ValueError('Node diversity requires at least two replicas')
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
    public_scheme='https' if cfg['tls_termination'] else 'http'
    dbhost=(name+'-postgres') if cfg['postgres_mode']=='internal' else cfg['postgres_host']
    clamavhost=name+'-clamav' if cfg['antivirus_mode']=='managed' else cfg['antivirus_host']
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
  QUORIVIO_AV_REQUIRED: "true"
  CLAMAV_HOST: {quote(clamavhost)}
  CLAMAV_PORT: "3310"
  MAX_UPLOAD_MB: {quote(cfg['max_upload_mb'])}
  QUORIVIO_ASSET_DIR: /app/assets
  PORT: {quote(port)}
  PUBLIC_BASE_URL: {quote(public_scheme+'://'+cfg['host'])}
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
{selector_yaml(cfg['app_node_selector'])}{('      topologySpreadConstraints:' + chr(10) + '        - maxSkew: 1' + chr(10) + '          topologyKey: kubernetes.io/hostname' + chr(10) + '          whenUnsatisfiable: ' + ('DoNotSchedule' if cfg['enforce_node_diversity'] else 'ScheduleAnyway') + chr(10) + ('          minDomains: 2' + chr(10) if cfg['enforce_node_diversity'] else '') + '          labelSelector:' + chr(10) + '            matchLabels:' + chr(10) + '              app: ' + name + chr(10)) if cfg['replicas'] > 1 else ''}      terminationGracePeriodSeconds: 45
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
    if cfg['antivirus_mode']=='managed':
        files.update(antivirus_resources(cfg,name,ns))
        files['kustomization.yaml']=files['kustomization.yaml'].replace(
            '  - 15-assets-pvc.yaml\n',
            '  - 13-clamav-deployment.yaml\n  - 14-clamav-service.yaml\n  - 15-assets-pvc.yaml\n  - 16-clamav-networkpolicy.yaml\n')
    else:
        for old in ('13-clamav-deployment.yaml','14-clamav-service.yaml','16-clamav-networkpolicy.yaml'):
            (out/old).unlink(missing_ok=True)
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

def antivirus_resources(cfg,name,ns):
    """Private managed ClamAV endpoint, never exposed by an Ingress/NodePort.

    The official clamd image owns its own startup/privilege lifecycle; unlike
    the Quorivio API it does not inherit runAsUser=1000. The namespace's Pod
    Security Admission and real image behavior must be accepted by operators.
    """
    deployment=f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}-clamav
  namespace: {ns}
spec:
  replicas: 1
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: {name}-clamav
  template:
    metadata:
      labels:
        app: {name}-clamav
    spec:
      automountServiceAccountToken: false
      containers:
        - name: clamav
          image: {cfg['antivirus_image']}
          imagePullPolicy: IfNotPresent
          ports:
            - name: clamd
              containerPort: 3310
          readinessProbe:
            tcpSocket:
              port: clamd
            initialDelaySeconds: 60
            periodSeconds: 15
            failureThreshold: 20
          livenessProbe:
            tcpSocket:
              port: clamd
            initialDelaySeconds: 180
            periodSeconds: 30
            failureThreshold: 5
          securityContext:
            allowPrivilegeEscalation: false
          resources:
            requests:
              cpu: 100m
              memory: 2Gi
            limits:
              cpu: 2000m
              memory: 4Gi
"""
    service=f"""apiVersion: v1
kind: Service
metadata:
  name: {name}-clamav
  namespace: {ns}
spec:
  type: ClusterIP
  selector:
    app: {name}-clamav
  ports:
    - name: clamd
      port: 3310
      targetPort: clamd
"""
    policy=f"""apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {name}-clamav-private
  namespace: {ns}
spec:
  podSelector:
    matchLabels:
      app: {name}-clamav
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: {name}
      ports:
        - protocol: TCP
          port: 3310
"""
    return {'13-clamav-deployment.yaml':deployment,'14-clamav-service.yaml':service,
            '16-clamav-networkpolicy.yaml':policy}

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

# Embedded, reviewable copies of the converter/inspection logic make this
# executable a TRUE single-file wizard. Only Python stdlib is needed; kubectl
# is required for operations against a live Kubernetes cluster.
# Regenerate embedded copies after editing tools/k8s_converter_upgrade.py or
# tools/k8s_cluster_inspection.py and run the standalone contract tests.
_STANDALONE_COMPONENT_SOURCES = {
    'k8s_converter_upgrade': r'''#!/usr/bin/env python3
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
''',
    'k8s_cluster_inspection': r'''"""Read-only discovery for importing an existing Quorivio Kubernetes installation.

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
''',
}
_STANDALONE_COMPONENT_SHA256 = {
    'k8s_converter_upgrade': '0143e83d65c030366bc92da9f3d9d181df90ad31ec01bd6277bf0c8d4d368783',
    'k8s_cluster_inspection': '8af9c08dd1ef6fabc3a6bbfe3730a1cdedf879dc2eda7fdb4364dfd6d42730f7',
}
_COMPONENT_CACHE={}
def _standalone_component(name):
    if name in _COMPONENT_CACHE:
        return _COMPONENT_CACHE[name]
    if name not in _STANDALONE_COMPONENT_SOURCES:
        raise ValueError('Unknown embedded Kubernetes component')
    # In the repository, use the canonical import (and keep existing mocks,
    # security tests, and operator tooling compatible). When only this wizard
    # file is copied to a host, load its verified embedded equivalent.
    local=Path(__file__).with_name(name+'.py')
    if local.is_file() and hashlib.sha256(local.read_bytes()).hexdigest()==_STANDALONE_COMPONENT_SHA256[name]:
        return importlib.import_module(name)
    source=_STANDALONE_COMPONENT_SOURCES[name]
    if hashlib.sha256(source.encode('utf-8')).hexdigest()!=_STANDALONE_COMPONENT_SHA256[name]:
        raise RuntimeError('Embedded Kubernetes module integrity mismatch')
    module=types.ModuleType(name)
    module.__file__=__file__
    module.__package__=''
    # The inspection helper imports k8s_wizard in save_report; the same
    # in-memory instance must be used even when executed as __main__.
    sys.modules.setdefault('k8s_wizard',sys.modules[__name__])
    exec(compile(source, '<standalone-'+name+'>', 'exec'),module.__dict__)
    _COMPONENT_CACHE[name]=module
    return module

def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--version',action='version',version='Quorivio Kubernetes wizard '+WIZARD_VERSION)
    a.add_argument('--no-self-update',action='store_true',help='Explicit offline mode: skip GitHub update check for this invocation')
    a.add_argument('--self-update-only',action='store_true',help='Check for and apply upstream wizard updates, then exit without touching Kubernetes')
    a.add_argument('--unattended',action='store_true',help='Use defaults plus overrides without prompting')
    a.add_argument('--output',default='k8s-generated',help='Target directory for deterministic Kustomize manifests')
    a.add_argument('--values',help='Existing JSON with custom overrides, e.g. saved quorivio-overrides.json')
    modes=a.add_mutually_exclusive_group()
    modes.add_argument('--inspect-cluster',action='store_true',help='Read-only inspection of an existing installation')
    modes.add_argument('--upgrade-converter',action='store_true',help='Plan ONLY a converter sidecar addition to a live Deployment; never apply automatically')
    modes.add_argument('--apply-converter',action='store_true',help='Explicitly apply a previously generated and revalidated converter-only JSON Patch')
    modes.add_argument('--ensure-converter-token',action='store_true',help='Explicitly add a private 32-byte converter token ONLY when the existing app Secret lacks one')
    a.add_argument('--converter-image',help='Published converter-specific image, e.g. your-registry/quorivio-converter:tag; required for --upgrade-converter')
    a.add_argument('--converter-deployment',help='Existing Deployment name (defaults to --set name=...)')
    a.add_argument('--app-container',help='Existing Quorivio API container name, otherwise discover from Deployment')
    a.add_argument('--converter-secret',help='Existing app Secret name, otherwise discover from API container references')
    a.add_argument('--kubectl',default='kubectl',help='kubectl executable; current kubeconfig context is recorded in plans')
    a.add_argument('--set',action='append',default=[],metavar='KEY=VALUE')
    args=a.parse_args(argv)
    if args.self_update_only:
        print('Quorivio Kubernetes wizard '+WIZARD_VERSION+' (update check completed or explicitly skipped)')
        return 0
    cfg=dict(DEFAULTS);out=Path(args.output)
    if args.upgrade_converter or args.apply_converter or args.ensure_converter_token:
        component=_standalone_component('k8s_converter_upgrade')
        UpgradeError=component.UpgradeError
        prepare_upgrade=component.prepare_upgrade
        apply_upgrade=component.apply_upgrade
        plan_token_provision=component.plan_token_provision
        valid_name=component.valid_name
        # Converter modes inspect the LIVE Deployment, never old wizard
        # overrides which could replace credentials or storage configuration.
        if args.values:a.error('--values cannot regenerate or replace existing credentials in converter mode')
        if args.apply_converter:
            if args.set or args.converter_image or args.converter_secret or args.converter_deployment or args.app_container:
                a.error('--apply-converter uses ONLY the already reviewed plan; do not add override options')
            if not any(x == '--output' or x.startswith('--output=') for x in (argv if argv is not None else sys.argv[1:])):
                a.error('--apply-converter requires explicit --output PATH to reviewed converter plan')
            try:report=apply_upgrade(out,kubectl=args.kubectl)
            except (UpgradeError, KeyError, OSError) as exc:a.error(str(exc))
            print('Converter-only Deployment patch applied and rollout verified:',report['namespace'],report['deployment'])
            print('Open platform admin -> Server configuration -> PDF/PowerPoint converter -> Check worker -> Enable.')
            return 0
        overrides={}
        for entry in args.set:
            if '=' not in entry:a.error('--set requires KEY=VALUE')
            key,value=entry.split('=',1)
            if key not in ('namespace','name'):a.error('converter upgrade permits only --set namespace=... and --set name=...')
            overrides[key]=value
        ns=overrides.get('namespace',cfg['namespace'])
        deployment=args.converter_deployment or overrides.get('name',cfg['name'])
        try:
            valid_name(ns,'Namespace');valid_name(deployment,'Deployment')
            if args.ensure_converter_token:
                if args.converter_image:a.error('--ensure-converter-token does not accept --converter-image')
                secret,created=plan_token_provision(ns,deployment,args.app_container,args.converter_secret,kubectl=args.kubectl)
                print('Private worker token', 'provisioned in' if created else 'already valid in', 'existing Secret:',secret)
                print('No other Secret fields or Kubernetes resources changed; token not printed or stored locally.')
            else:
                if not args.converter_image:a.error('--upgrade-converter requires --converter-image with a published and accessible converter-specific image')
                if not any(x == '--output' or x.startswith('--output=') for x in (argv if argv is not None else sys.argv[1:])):
                    a.error('--upgrade-converter requires explicit --output PATH different from original wizard manifests')
                plan=prepare_upgrade(ns,deployment,out,args.converter_image,app_container=args.app_container,secret_name=args.converter_secret,kubectl=args.kubectl)
                print('Converter-only upgrade plan prepared in:',out)
                print('Context:',plan['context'],'Deployment:',plan['namespace']+'/'+plan['deployment'])
                print('Only Deployment pod template will change; no apply, database, PVC, Ingress or Secret modifications.')
                print('Inspect the patch, then use --apply-converter --output',out)
        except (UpgradeError, OSError, KeyError) as exc:a.error(str(exc))
        return 0
    if args.converter_image or args.converter_deployment or args.app_container or args.converter_secret:
        a.error('converter-specific flags require --upgrade-converter or --ensure-converter-token')
    if args.inspect_cluster:
        component=_standalone_component('k8s_cluster_inspection')
        inspect_resources=component.inspect_resources
        derive_nonsecret_config=component.derive_nonsecret_config
        save_report=component.save_report
        # A read-only path is required: never generate new Secret or overwrite
        # any prior Kubernetes YAML during discovery.
        namespace=next((entry.split('=',1)[1] for entry in args.set if entry.startswith('namespace=')),cfg['namespace'])
        name=next((entry.split('=',1)[1] for entry in args.set if entry.startswith('name=')),cfg['name'])
        report=derive_nonsecret_config(inspect_resources(namespace,name,kubectl=args.kubectl),namespace,name)
        save_report(out,report)
        print(f'Read-only inventory saved in {out}/quorivio-cluster-discovery.json')
        print('No Secret values collected, no Kubernetes resources modified, no manifests applied.')
        for note in report['warnings']:print('WARNING:',note)
        return 0
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
        if k in ('tls_termination','enforce_node_diversity'):
            if v.lower() not in ('true','false'):a.error(f'{k} requires true/false')
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
if __name__=='__main__':raise SystemExit(_run_standalone_cli())
