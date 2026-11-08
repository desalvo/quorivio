"""RC262: disk telemetry is PVC-correct, standalone and never rewrites secrets."""
import copy
import json
import re
import sys
import tempfile
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import k8s_wizard as wizard
import k8s_disk_monitor_upgrade as monitor


def statefulset():
 return {
  'apiVersion':'apps/v1','kind':'StatefulSet',
  'metadata':{'name':'quorivio-postgres','namespace':'quorivio','uid':'uid-1','resourceVersion':'123'},
  'spec':{'template':{'spec':{'containers':[{
    'name':'postgres','image':'postgres:18.6-alpine','imagePullPolicy':'IfNotPresent',
    'env':[{'name':'POSTGRES_DB','value':'quorivio'},{'name':'POSTGRES_USER','value':'quorivio'},
           {'name':'POSTGRES_PASSWORD','valueFrom':{'secretKeyRef':{'name':'quorivio-app-secrets','key':'POSTGRES_PASSWORD'}}}],
    'volumeMounts':[{'name':'data','mountPath':'/var/lib/postgresql'}]
   }]}}}}

class DiskMonitorTests(unittest.TestCase):
 def setUp(self):
  td=tempfile.TemporaryDirectory();self.addCleanup(td.cleanup);self.root=Path(td.name)
  self.generated=self.root/'k8s-generated'
  wizard.generate(dict(wizard.DEFAULTS),self.generated)
  self.s=statefulset();self.actions=[]
  self.fakepatch=patch.object(monitor,'_run',side_effect=self.fake_run)
  self.fakepatch.start();self.addCleanup(self.fakepatch.stop)
 def fake_run(self,args,kubectl='kubectl',stdin=None,timeout=30):
  self.actions.append(args)
  if args[:2]==['config','current-context']:return 'cluster-staging\n'
  if 'get' in args and 'statefulset' in args:return json.dumps(self.s)
  if 'patch' in args and '--dry-run=server' in args:return 'statefulset.apps/quorivio-postgres\n'
  if 'patch' in args:
   planfile=next(x.split('=',1)[1] for x in args if x.startswith('--patch-file='))
   operations=json.loads(Path(planfile).read_text())
   new_container=copy.deepcopy(operations[-1]['value'])
   new_container['terminationMessagePath']='/dev/termination-log'
   new_container['terminationMessagePolicy']='File'
   self.s['spec']['template']['spec']['containers'].append(new_container)
   self.s['metadata']['resourceVersion']='124'
   return 'statefulset.apps/quorivio-postgres patched\n'
  if 'rollout' in args:return 'statefulset rolling update complete\n'
  raise AssertionError('unexpected kubectl invocation '+str(args))
 def test_new_cluster_generated_probe_is_readonly_with_secret_reference(self):
  yaml=(self.generated/'12-postgres-statefulset.yaml').read_text()
  self.assertIn('name: db-disk-probe',yaml)
  self.assertIn('readOnly: true',yaml)
  self.assertIn('INSERT INTO disk_monitor_samples',yaml)
  self.assertNotIn('password123',yaml)
  self.assertIn('key: POSTGRES_PASSWORD',yaml)
 def test_full_plan_then_explicit_apply_and_manifest_overlay(self):
  directory=self.root/'plan'
  plan=monitor.plan_disk_monitor('quorivio','quorivio',directory,self.generated)
  self.assertEqual(plan['context'],'cluster-staging')
  self.assertEqual(len([c for c in self.s['spec']['template']['spec']['containers'] if c['name']=='db-disk-probe']),0)
  with self.assertRaisesRegex(monitor.DiskMonitorUpgradeError,'restart'):
   monitor.apply_disk_monitor(directory,False)
  result=monitor.apply_disk_monitor(directory,True)
  self.assertEqual(result['statefulset'],'quorivio-postgres')
  self.assertEqual(len(self.s['spec']['template']['spec']['containers']),2)
  self.assertIn('  - path: 97-postgres-disk-probe-patch.json',(self.generated/'kustomization.yaml').read_text())
  overlay=json.loads((self.generated/'97-postgres-disk-probe-patch.json').read_text())
  self.assertEqual(overlay['spec']['template']['spec']['containers'][0]['name'],'db-disk-probe')
  self.assertEqual(len([a for a in self.actions if 'patch' in a and '--dry-run=server' not in a]),1)
  monitor.sync_disk_monitor('quorivio','quorivio',self.generated)
  self.assertEqual(len([a for a in self.actions if 'patch' in a and '--dry-run=server' not in a]),1)
 def test_identity_drift_rejected_before_live_change(self):
  directory=self.root/'plan'
  monitor.plan_disk_monitor('quorivio','quorivio',directory,self.generated)
  self.s['metadata']['resourceVersion']='999'
  with self.assertRaisesRegex(monitor.DiskMonitorUpgradeError,'changed'):
   monitor.apply_disk_monitor(directory,True)
  self.assertFalse(any('patch' in x for x in self.actions))
 def test_generated_drift_rejected(self):
  directory=self.root/'plan'
  monitor.plan_disk_monitor('quorivio','quorivio',directory,self.generated)
  (self.generated/'12-postgres-statefulset.yaml').write_text('changed\n')
  with self.assertRaisesRegex(monitor.DiskMonitorUpgradeError,'changed'):
   monitor.apply_disk_monitor(directory,True)
 def test_synced_probe_requires_exact_security_profile(self):
  probe=monitor.disk_probe_sidecar(self.s)
  self.s['spec']['template']['spec']['containers'].append(copy.deepcopy(probe))
  self.s['spec']['template']['spec']['containers'][-1]['securityContext']['allowPrivilegeEscalation']=True
  with self.assertRaisesRegex(monitor.DiskMonitorUpgradeError,'security'):
   monitor.sync_disk_monitor('quorivio','quorivio',self.generated)
 def test_api_defaulted_termination_fields_are_only_accepted_exactly(self):
  probe=monitor.disk_probe_sidecar(self.s)
  probe['terminationMessagePath']='/dev/termination-log'
  probe['terminationMessagePolicy']='File'
  self.s['spec']['template']['spec']['containers'].append(probe)
  monitor.sync_disk_monitor('quorivio','quorivio',self.generated)
  for key,value in [('terminationMessagePath','/var/log/evil'),('terminationMessagePolicy','FallbackToLogsOnError')]:
   with self.subTest(key=key):
    probe[key]=value
    with self.assertRaisesRegex(monitor.DiskMonitorUpgradeError,'drift'):
     monitor.sync_disk_monitor('quorivio','quorivio',self.generated)
    probe[key]={'terminationMessagePath':'/dev/termination-log','terminationMessagePolicy':'File'}[key]

 def test_unexpected_added_fields_refused_even_when_defaults_are_valid(self):
  probe=monitor.disk_probe_sidecar(self.s)
  probe['terminationMessagePath']='/dev/termination-log'
  probe['terminationMessagePolicy']='File'
  self.s['spec']['template']['spec']['containers'].append(probe)
  probe['workingDir']='/unexpected'
  with self.assertRaisesRegex(monitor.DiskMonitorUpgradeError,'workingDir'):
   monitor.sync_disk_monitor('quorivio','quorivio',self.generated)

 def test_standalone_embedded_sync_accepts_kubernetes_defaults(self):
  standalone=wizard._standalone_component('k8s_disk_monitor_upgrade')
  expected=standalone.disk_probe_sidecar(self.s)
  with_defaults=copy.deepcopy(expected)
  with_defaults.update({'terminationMessagePath':'/dev/termination-log','terminationMessagePolicy':'File'})
  standalone._verified_live_probe(with_defaults,expected)
  with_defaults['securityContext']['allowPrivilegeEscalation']=True
  with self.assertRaisesRegex(standalone.DiskMonitorUpgradeError,'security'):
   standalone._verified_live_probe(with_defaults,expected)

 def test_standalone_sync_recovers_applied_probe_without_kubectl_writes(self):
  # Model the user's scenario: rollout already succeeded, the older wizard
  # rejected Kubernetes-defaulted termination fields, and only local
  # generated manifests need reconciliation. The CLI runs in a fresh folder
  # containing ONLY k8s_wizard.py and a fake kubectl executable.
  existing=monitor.disk_probe_sidecar(self.s)
  existing.update({'terminationMessagePath':'/dev/termination-log','terminationMessagePolicy':'File'})
  self.s['spec']['template']['spec']['containers'].append(existing)
  with tempfile.TemporaryDirectory() as temp:
   isolated=Path(temp)
   standalone=isolated/'k8s_wizard.py'
   standalone.write_bytes((ROOT/'tools/k8s_wizard.py').read_bytes())
   tool=isolated/'kubectl'
   fixture=isolated/'statefulset.json'
   fixture.write_text(json.dumps(self.s))
   audit=isolated/'kubectl-calls.txt'
   tool.write_text("""#!/usr/bin/env python3
import json,sys,pathlib
args=sys.argv[1:]
with (pathlib.Path(__file__).parent/'kubectl-calls.txt').open('a') as stream:
 stream.write(' '.join(args)+'\\n')
if args==['config','current-context']:
 print('cluster-staging')
elif 'get' in args and 'statefulset' in args:
 print((pathlib.Path(__file__).parent/'statefulset.json').read_text())
else:
 print('unexpected kubectl write',file=sys.stderr)
 sys.exit(9)
""")
   tool.chmod(0o700)
   result=subprocess.run([sys.executable,str(standalone),'--no-self-update','--sync-disk-monitor',
       '--generated-dir',str(self.generated),'--set','namespace=quorivio','--set','name=quorivio',
       '--kubectl',str(tool)],capture_output=True,text=True,cwd=isolated)
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertTrue((self.generated/'97-postgres-disk-probe-patch.json').is_file())
   calls=audit.read_text()
   self.assertNotIn('patch',calls)
   self.assertNotIn('rollout',calls)

 def test_probe_script_posix_shell_syntax(self):
  r=subprocess.run(['/bin/sh','-n'],input=monitor.PROBE_SCRIPT,text=True,capture_output=True)
  self.assertEqual(r.returncode,0,r.stderr)
  self.assertIn('df -Pk /var/lib/postgresql',monitor.PROBE_SCRIPT)
  self.assertIn('sleep 300',monitor.PROBE_SCRIPT)
 def test_standalone_version_and_embedded_probe(self):
  with tempfile.TemporaryDirectory() as temp:
   target=Path(temp)/'k8s_wizard.py';target.write_bytes((ROOT/'tools/k8s_wizard.py').read_bytes())
   r=subprocess.run([sys.executable,str(target),'--version'],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr)
   import importlib.util
   spec=importlib.util.spec_from_file_location('single_disk_wizard',str(target));module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
   self.assertIn(module.WIZARD_VERSION,r.stdout)
   self.assertGreaterEqual(int(module.WIZARD_VERSION.rsplit('rc',1)[-1]),263)
   embedded=module._standalone_component('k8s_disk_monitor_upgrade')
   self.assertEqual(embedded.PROBE_SCRIPT,monitor.PROBE_SCRIPT)
if __name__=='__main__':unittest.main()
