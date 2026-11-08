"""RC246: live Kubernetes converter expansion is safe, scoped and explicit."""
from __future__ import annotations
import base64
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import k8s_converter_upgrade as upgrade

TOKEN=base64.b64encode(b'a'*64).decode()
IMAGE='registry.example.org/quorivio-converter:rc245'


def fixture(*, existing_token=True, containers=None, fs_group=1000):
    deploy={'kind':'Deployment','metadata':{'name':'quorivio','namespace':'quorivio','uid':'abc-uuid','resourceVersion':'400','labels':{}},
    'spec':{'replicas':2,'template':{'metadata':{'labels':{'app':'quorivio'}},'spec':{
     'securityContext':{'fsGroup':fs_group},
     'containers':containers or [{'name':'quorivio','image':'desalvo/quorivio:sha-c108694705d2',
     'env':[{'name':'DATABASE_URL','valueFrom':{'secretKeyRef':{'name':'quorivio-app-secrets','key':'DATABASE_URL'}}}],
     'envFrom':[{'configMapRef':{'name':'quorivio-config'}},{'secretRef':{'name':'quorivio-app-secrets'}}],
     'volumeMounts':[{'name':'assets','mountPath':'/app/assets'}]}],
     'volumes':[{'name':'assets','persistentVolumeClaim':{'claimName':'quorivio-assets'}}]
    }}}}
    secret={'kind':'Secret','metadata':{'name':'quorivio-app-secrets','namespace':'quorivio','resourceVersion':'55'},
            'data':{'DATABASE_URL':base64.b64encode(b'secret postgres').decode()}}
    if existing_token:secret['data']['QUORIVIO_WORKER_TOKEN']=TOKEN
    return deploy,secret


def pointer(doc,path):
    def unescape(x):return x.replace('~1','/').replace('~0','~')
    value=doc
    for k in path.strip('/').split('/'):
        k=unescape(k)
        value=value[int(k)] if isinstance(value,list) else value[k]
    return value


def apply_json_patch(obj,patch):
    root=copy.deepcopy(obj)
    for op in patch:
        path=op['path']
        if op['op']=='test':
            if pointer(root,path)!=op['value']:raise AssertionError('test failed')
            continue
        assert op['op']=='add'
        parts=path.strip('/').split('/')
        parent=root
        for key in parts[:-1]:
            parent=parent[int(key)] if isinstance(parent,list) else parent[key]
        if isinstance(parent,list):
            assert parts[-1]=='-'
            parent.append(copy.deepcopy(op['value']))
        else:parent[parts[-1]]=copy.deepcopy(op['value'])
    return root


class PatchDesign(unittest.TestCase):
    def setUp(self):self.deployment,self.secret=fixture()

    def generate(self):return upgrade.build_patch(self.deployment,None,'quorivio-app-secrets',IMAGE)[0]

    def test_only_deployment_pod_spec_changes(self):
        patch=self.generate();changed=apply_json_patch(self.deployment,patch)
        self.assertEqual(self.deployment['spec']['replicas'],changed['spec']['replicas'])
        self.assertEqual(self.deployment['spec']['template']['metadata'],changed['spec']['template']['metadata'])
        self.assertEqual(self.deployment['spec']['template']['spec']['volumes'][0],changed['spec']['template']['spec']['volumes'][0])
        self.assertEqual(self.deployment['spec']['template']['spec']['containers'][0]['image'],changed['spec']['template']['spec']['containers'][0]['image'])
        self.assertEqual(len(changed['spec']['template']['spec']['containers']),2)
        self.assertEqual(changed['spec']['template']['spec']['containers'][1]['image'],IMAGE)
        self.assertEqual(changed['spec']['template']['spec']['containers'][1]['readinessProbe']['httpGet']['path'],'/health')
        self.assertEqual(changed['spec']['template']['spec']['containers'][1]['securityContext']['readOnlyRootFilesystem'],True)
        self.assertEqual(changed['spec']['template']['spec']['containers'][0]['envFrom'],self.deployment['spec']['template']['spec']['containers'][0]['envFrom'])
        self.assertEqual(len(changed['spec']['template']['spec']['volumes']),3)
        self.assertEqual(changed['spec']['template']['spec']['volumes'][1]['emptyDir']['sizeLimit'],'2Gi')

    def test_token_is_secret_ref_and_no_secrets_in_patch(self):
        s=json.dumps(self.generate())
        self.assertIn('secretKeyRef',s);self.assertNotIn(TOKEN,s)
        self.assertNotIn('secret postgres',s)
        self.assertIn('127.0.0.1:8099',s)

    def test_resource_version_and_uid_guard(self):
        ops=self.generate();self.assertEqual(ops[0],{'op':'test','path':'/metadata/uid','value':'abc-uuid'})
        self.assertEqual(ops[1]['path'],'/metadata/resourceVersion')
        new=copy.deepcopy(self.deployment);new['metadata']['resourceVersion']='401'
        with self.assertRaises(AssertionError):apply_json_patch(new,ops)

    def test_no_app_env_and_mounts(self):
        self.deployment['spec']['template']['spec']['containers'][0].pop('env')
        self.deployment['spec']['template']['spec']['containers'][0].pop('volumeMounts')
        out=apply_json_patch(self.deployment,self.generate())
        self.assertEqual(len(out['spec']['template']['spec']['containers'][0]['env']),4)
        self.assertEqual(len(out['spec']['template']['spec']['containers'][0]['volumeMounts']),1)

    def test_existing_env_kept_without_duplicates(self):
        app=self.deployment['spec']['template']['spec']['containers'][0]
        app['env'].append({'name':'QUORIVIO_ENABLE_CONVERTER','value':'true'})
        out=apply_json_patch(self.deployment,self.generate())
        self.assertEqual([x['name'] for x in out['spec']['template']['spec']['containers'][0]['env']].count('QUORIVIO_ENABLE_CONVERTER'),1)

    def test_existing_conflicting_env_refused(self):
        self.deployment['spec']['template']['spec']['containers'][0]['env'].append({'name':'QUORIVIO_ENABLE_CONVERTER','value':'false'})
        with self.assertRaisesRegex(upgrade.UpgradeError,'conflicting'):self.generate()

    def test_converter_port_collision_is_rejected(self):
        self.deployment['spec']['template']['spec']['containers'][0]['ports']=[{'containerPort':8099}]
        with self.assertRaisesRegex(upgrade.UpgradeError,'port 8099'):self.generate()

    def test_existing_converter_is_not_overwritten(self):
        self.deployment['spec']['template']['spec']['containers'].append({'name':'converter','image':'unknown:foo'})
        with self.assertRaisesRegex(upgrade.UpgradeError,'already exists'):self.generate()

    def test_existing_conversion_mount_is_not_overwritten(self):
        self.deployment['spec']['template']['spec']['containers'][0]['volumeMounts'].append({'name':'old','mountPath':'/conversions'})
        with self.assertRaisesRegex(upgrade.UpgradeError,'existing conversion'):self.generate()

    def test_existing_volume_is_not_overwritten(self):
        self.deployment['spec']['template']['spec']['volumes'].append({'name':'converter-tmp','emptyDir':{}})
        with self.assertRaisesRegex(upgrade.UpgradeError,'volume name'):self.generate()

    def test_nonzero_max_unavailable_denied(self):
        self.deployment['spec']['strategy']={'type':'RollingUpdate','rollingUpdate':{'maxUnavailable':1,'maxSurge':1}}
        with self.assertRaisesRegex(upgrade.UpgradeError,'maxUnavailable'):self.generate()

    def test_recreate_strategy_denied(self):
        self.deployment['spec']['strategy']={'type':'Recreate'}
        with self.assertRaisesRegex(upgrade.UpgradeError,'Recreate'):self.generate()

    def test_no_fsgroup_no_change(self):
        self.deployment['spec']['template']['spec']['securityContext'].pop('fsGroup')
        with self.assertRaisesRegex(upgrade.UpgradeError,'fsGroup'):self.generate()

    def test_unusual_fsgroup_preserved(self):
        self.deployment['spec']['template']['spec']['securityContext']['fsGroup']=1234
        out=apply_json_patch(self.deployment,self.generate())
        self.assertEqual(out['spec']['template']['spec']['securityContext']['fsGroup'],1234)
        self.assertEqual(out['spec']['template']['spec']['containers'][-1]['securityContext']['runAsGroup'],1234)

    def test_helm_managed_rejected(self):
        self.deployment['metadata']['labels']['app.kubernetes.io/managed-by']='Helm'
        with self.assertRaisesRegex(upgrade.UpgradeError,'Helm'):self.generate()

    def test_unpinned_or_malformed_image_rejected(self):
        for image in ('quorivio-converter','example', 'bad image:rc','example.com/conv\n:rc','docker.io:443/conv','repo/conv@sha256:bad','https://repo/conv:tag'):
            with self.subTest(image=image), self.assertRaises(upgrade.UpgradeError):
                upgrade.build_patch(self.deployment,None,'quorivio-app-secrets',image)

    def test_app_secret_detected_via_database_url(self):
        app=self.deployment['spec']['template']['spec']['containers'][0]
        self.assertEqual(upgrade.discover_secret(app,None),'quorivio-app-secrets')

    def test_app_secret_detected_via_envfrom(self):
        app=self.deployment['spec']['template']['spec']['containers'][0]
        app.pop('env')
        self.assertEqual(upgrade.discover_secret(app,None),'quorivio-app-secrets')

    def test_mixed_secrets_fail_closed(self):
        app=self.deployment['spec']['template']['spec']['containers'][0]
        app['env'].append({'name':'AUTH_SECRET','valueFrom':{'secretKeyRef':{'name':'different-secret','key':'AUTH_SECRET'}}})
        with self.assertRaisesRegex(upgrade.UpgradeError,'multiple'):upgrade.discover_secret(app,None)

    def test_check_token_requirements(self):
        self.assertTrue(upgrade.check_token(self.secret))
        self.secret['data'].pop('QUORIVIO_WORKER_TOKEN')
        self.assertFalse(upgrade.check_token(self.secret))
        self.secret['data']['QUORIVIO_WORKER_TOKEN']=base64.b64encode(b'short').decode()
        with self.assertRaisesRegex(upgrade.UpgradeError,'shorter'):upgrade.check_token(self.secret)


class FakeKube:
    def __init__(self,dep,secret):
        self.deploy=copy.deepcopy(dep);self.secret=copy.deepcopy(secret)
        self.calls=[];self.context='dev-cluster';self.fail_dry=False
    def run(self,args,*,kubectl='kubectl',input_data=None,timeout=25):
        self.calls.append((list(args),input_data))
        if args[:2]==['config','current-context']:return self.context+'\n'
        ns=args[args.index('-n')+1]
        assert ns=='quorivio'
        if 'get' in args:
            kind=args[args.index('get')+1]
            if kind=='deployment':return json.dumps(self.deploy)
            if kind=='secret':return json.dumps(self.secret)
        if 'patch' in args:
            if self.fail_dry and '--dry-run=server' in args:raise upgrade.UpgradeError('dry-run rejected')
            if input_data:
                obj=self.secret
                patch=json.loads(input_data)
                if '--dry-run=server' not in args:
                    self.secret=apply_json_patch(obj,patch)
                return 'secret/quorivio-app-secrets\n'
            if '--dry-run=server' not in args:
                from pathlib import Path
                path=next(p.split('=',1)[1] for p in args if p.startswith('--patch-file='))
                self.deploy=apply_json_patch(self.deploy,json.loads(Path(path).read_text()))
            return 'deployment/quorivio\n'
        if 'rollout' in args:return 'successfully rolled out\n'
        raise AssertionError(args)


class Operations(unittest.TestCase):
    def setUp(self):
        self.dep,self.secret=fixture();self.fake=FakeKube(self.dep,self.secret)
        self.patch=patch.object(upgrade,'run_kubectl',side_effect=self.fake.run)
        self.patch.start();self.addCleanup(self.patch.stop)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)/'converter-upgrade'

    def prepare(self):return upgrade.prepare_upgrade('quorivio','quorivio',self.directory,IMAGE)

    def test_plan_never_mutates_live_cluster(self):
        p=self.prepare()
        self.assertEqual(p['context'],'dev-cluster')
        self.assertFalse(any('patch' in a or 'rollout' in a for a,_ in self.fake.calls))
        self.assertEqual(self.fake.deploy,self.dep);self.assertEqual(self.fake.secret,self.secret)
        self.assertEqual(len(list(self.directory.iterdir())),3)
        self.assertEqual((self.directory/'converter-patch.json').stat().st_mode & 0o777,0o600)
        self.assertEqual(self.directory.stat().st_mode & 0o777,0o700)
        self.assertNotIn(TOKEN,(self.directory/'converter-plan.json').read_text())

    def test_dry_run_then_atomic_patch_and_rollout(self):
        self.prepare();upgrade.apply_upgrade(self.directory)
        args=[a for a,_ in self.fake.calls]
        self.assertEqual(len([x for x in args if 'patch' in x]),2)
        self.assertTrue(any('--dry-run=server' in x for x in args if 'patch' in x))
        self.assertTrue(any('rollout' in x for x in args))
        self.assertEqual(self.fake.deploy['spec']['template']['spec']['containers'][-1]['name'],'converter')
        self.assertEqual(self.fake.secret,self.secret)

    def test_changed_context_stops_without_patch(self):
        self.prepare();self.fake.context='production-context'
        with self.assertRaisesRegex(upgrade.UpgradeError,'context changed'):upgrade.apply_upgrade(self.directory)
        self.assertFalse(any('patch' in a for a,_ in self.fake.calls))

    def test_changed_deployment_stops_without_patch(self):
        self.prepare();self.fake.deploy['metadata']['resourceVersion']='401'
        with self.assertRaisesRegex(upgrade.UpgradeError,'changed since planning'):upgrade.apply_upgrade(self.directory)
        self.assertFalse(any('patch' in a for a,_ in self.fake.calls))

    def test_manual_patch_edit_fails_closed(self):
        self.prepare();path=self.directory/'converter-patch.json';path.write_text('[]\n')
        with self.assertRaisesRegex(upgrade.UpgradeError,'changed after generation'):upgrade.apply_upgrade(self.directory)

    def test_plan_not_reused_or_existing_base_overwritten(self):
        self.prepare()
        with self.assertRaisesRegex(upgrade.UpgradeError,'fresh'):self.prepare()
        self.assertEqual(self.fake.deploy,self.dep)

    def test_plan_does_not_create_when_token_missing(self):
        self.fake.secret['data'].pop('QUORIVIO_WORKER_TOKEN')
        with self.assertRaisesRegex(upgrade.UpgradeError,'ensure-converter-token'):self.prepare()
        self.assertFalse(self.directory.exists())

    def test_apply_dry_run_failure_does_not_mutate(self):
        self.prepare();self.fake.fail_dry=True
        with self.assertRaisesRegex(upgrade.UpgradeError,'dry-run'):upgrade.apply_upgrade(self.directory)
        self.assertEqual(self.fake.deploy,self.dep)

    def test_existing_secret_token_not_overwritten(self):
        name,created=upgrade.plan_token_provision('quorivio','quorivio',None,None)
        self.assertEqual(name,'quorivio-app-secrets');self.assertFalse(created)
        self.assertFalse(any('patch' in x for x,_ in self.fake.calls))

    def test_provision_token_only_adds_one_secret_key(self):
        self.fake.secret['data'].pop('QUORIVIO_WORKER_TOKEN')
        name,created=upgrade.plan_token_provision('quorivio','quorivio',None,None)
        self.assertTrue(created)
        self.assertTrue(upgrade.check_token(self.fake.secret))
        self.assertEqual(self.fake.secret['data']['DATABASE_URL'],self.secret['data']['DATABASE_URL'])
        self.assertEqual(len([x for x,_ in self.fake.calls if 'patch' in x]),2)
        self.assertTrue(all('--patch-file=/dev/stdin' in x for x,_ in self.fake.calls if 'patch' in x))
        self.assertFalse(self.directory.exists())

    def test_symlink_destination_refused(self):
        safe=Path(self.temp.name)/'unrelated';safe.mkdir();self.directory.symlink_to(safe)
        with self.assertRaisesRegex(upgrade.UpgradeError,'symlinked'):self.prepare()


if __name__=='__main__':unittest.main()

class WizardCli(unittest.TestCase):
    def test_upgrader_does_not_call_legacy_generate(self):
        import k8s_wizard
        with patch.object(upgrade,'prepare_upgrade',return_value={'context':'mock','namespace':'quorivio','deployment':'quorivio'}) as p, patch.object(k8s_wizard,'generate',side_effect=AssertionError('legacy manifest overwrite')), patch.object(k8s_wizard,'_generated_directory_from_args',return_value=Path('/tmp/test-rc246-generated')):
            from contextlib import redirect_stdout
            from io import StringIO
            with redirect_stdout(StringIO()):
                result=k8s_wizard.main(['--upgrade-converter','--unattended','--output=/tmp/test-rc246-plan',
                                         '--converter-image',IMAGE,'--set','namespace=quorivio'])
            self.assertEqual(result,0);self.assertEqual(p.call_count,1)

    def test_apply_rejects_unplanned_overrides(self):
        import k8s_wizard
        with self.assertRaises(SystemExit) as err:
            k8s_wizard.main(['--apply-converter','--output','/tmp/safe','--set','postgres_mode=internal'])
        self.assertEqual(err.exception.code,2)

    def test_upgrade_requires_fresh_output_flag(self):
        import k8s_wizard
        with self.assertRaises(SystemExit) as err:
            k8s_wizard.main(['--upgrade-converter','--converter-image',IMAGE,'--unattended'])
        self.assertEqual(err.exception.code,2)

    def test_upgrade_refuses_postgres_changes(self):
        import k8s_wizard
        with self.assertRaises(SystemExit) as err:
            k8s_wizard.main(['--upgrade-converter','--converter-image',IMAGE,'--output','/tmp/empty','--set','postgres_mode=external'])
        self.assertEqual(err.exception.code,2)

    def test_token_mode_is_explicit_and_no_value_logged(self):
        import k8s_wizard
        from contextlib import redirect_stdout
        from io import StringIO
        output=StringIO()
        with patch.object(upgrade,'plan_token_provision',return_value=('quorivio-app-secrets',True)) as p, patch.object(k8s_wizard,'_generated_directory_from_args',return_value=Path('/tmp/test-rc246-generated')), patch.object(upgrade,'reconcile_generated_token',return_value='/tmp/test-private-backup'):
            with redirect_stdout(output):result=k8s_wizard.main(['--ensure-converter-token'])
        self.assertEqual(result,0);self.assertEqual(p.call_count,1)
        self.assertNotIn(TOKEN,output.getvalue())
        self.assertIn('token not printed',output.getvalue())
