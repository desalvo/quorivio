"""RC258: single-copy wizard and correct Kubernetes IntOrString rollout guards.

Run without real kubectl, cluster, repository modules or YAML dependencies.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'tools'
sys.path.insert(0,str(TOOLS))
import k8s_converter_upgrade as upgrade
import k8s_wizard

FAKE_KUBECTL = r'''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
path=Path(os.environ['FAKE_KUBECTL_STATE'])
db=json.loads(path.read_text())
a=sys.argv[1:]
if a[:2]==['config','current-context']:
 print('qa-cluster');sys.exit(0)
ns=a[a.index('-n')+1] if '-n' in a else ''
if ns != 'quorivio':sys.exit(3)
if 'get' in a:
 kind=a[a.index('get')+1];name=a[a.index('get')+2]
 obj=db.get(kind+'/'+name)
 if obj is None:
  if '--ignore-not-found=true' in a:sys.exit(0)
  sys.exit(4)
 print(json.dumps(obj));sys.exit(0)
if 'patch' in a:
 kind=a[a.index('patch')+1];name=a[a.index('patch')+2]
 ptr='deployment' if kind=='deployment' else 'secret'
 key=ptr+'/'+name
 obj=json.loads(json.dumps(db[key]))
 file=next((item.split('=',1)[1] for item in a if item.startswith('--patch-file=')),None)
 if not file:sys.exit(9)
 payload=sys.stdin.read() if file=='/dev/stdin' else Path(file).read_text()
 for op in json.loads(payload):
  parts=[p.replace('~1','/').replace('~0','~') for p in op['path'].strip('/').split('/')]
  parent=obj
  for part in parts[:-1]:
   parent=parent[int(part)] if isinstance(parent,list) else parent[part]
  last=parts[-1]
  if op['op']=='test':
   if (parent[int(last)] if isinstance(parent,list) else parent[last])!=op['value']:
    sys.exit(7)
  elif op['op']=='add':
   if isinstance(parent,list):
    if last!='-':sys.exit(8)
    parent.append(op['value'])
   else:parent[last]=op['value']
  else:sys.exit(9)
 if '--dry-run=server' not in a:
  db[key]=obj
  path.write_text(json.dumps(db))
 print(kind+'/'+name);sys.exit(0)
if 'rollout' in a:
 print('successfully rolled out');sys.exit(0)
sys.exit(10)
'''


def fixture(replicas=2,strategy=None,include_token=False):
 app={'name':'quorivio','image':'desalvo/quorivio:latest',
      'env':[{'name':'DATABASE_URL','valueFrom':{'secretKeyRef':{'name':'quorivio-app-secrets','key':'DATABASE_URL'}}}],
      'envFrom':[{'secretRef':{'name':'quorivio-app-secrets'}}],
      'volumeMounts':[{'name':'assets','mountPath':'/app/assets'}]}
 deployment={'apiVersion':'apps/v1','kind':'Deployment',
      'metadata':{'name':'quorivio','namespace':'quorivio','uid':'unit-uid','resourceVersion':'77','labels':{}},
      'spec':{'replicas':replicas,'strategy':strategy or {'type':'RollingUpdate','rollingUpdate':{'maxUnavailable':'25%','maxSurge':'25%'}},
      'template':{'metadata':{'labels':{'app':'quorivio'}},'spec':{'securityContext':{'fsGroup':1000},
      'containers':[app],'volumes':[{'name':'assets','persistentVolumeClaim':{'claimName':'quorivio-assets'}}]}}}}
 secret={'kind':'Secret','metadata':{'name':'quorivio-app-secrets','namespace':'quorivio','resourceVersion':'90'},'data':{'DATABASE_URL':base64.b64encode(b'postgres://db').decode()}}
 if include_token:secret['data']['QUORIVIO_WORKER_TOKEN']=base64.b64encode(b'a'*64).decode()
 return {'deployment/quorivio':deployment,'secret/quorivio-app-secrets':secret}


class RolloutPercentages(unittest.TestCase):
 def test_kubernetes_defaults_allow_up_to_three_replicas(self):
  for n in (1,2,3):
   with self.subTest(replicas=n):
    d=fixture(n)['deployment/quorivio']
    self.assertEqual(upgrade.effective_rollout_unavailability(d),0)
    patch,_=upgrade.build_patch(d,None,'quorivio-app-secrets','desalvo/quorivio-converter:latest')
    self.assertTrue(any(x['path']=='/spec/template/spec/containers/-' for x in patch))

 def test_percentage_rounds_down_and_rejects_real_loss(self):
  for n,percentage in [(4,'25%'),(9,'12%'),(2,'50%'),(1,'100%')]:
   with self.subTest(n=n,percentage=percentage):
    dep=fixture(n)['deployment/quorivio']
    dep['spec']['strategy']['rollingUpdate']['maxUnavailable']=percentage
    with self.assertRaisesRegex(upgrade.UpgradeError,'maxUnavailable'):
     upgrade.build_patch(dep,None,'quorivio-app-secrets','desalvo/quorivio-converter:latest')

 def test_zero_percent_with_large_replica_count(self):
  dep=fixture(10)['deployment/quorivio']
  dep['spec']['strategy']['rollingUpdate']['maxUnavailable']='0%'
  self.assertEqual(upgrade.effective_rollout_unavailability(dep),0)

 def test_default_kubernetes_rolling_update(self):
  dep=fixture(3)['deployment/quorivio']
  dep['spec'].pop('strategy')
  self.assertEqual(upgrade.effective_rollout_unavailability(dep),0)
  dep['spec']['replicas']=4
  self.assertEqual(upgrade.effective_rollout_unavailability(dep),1)
  with self.assertRaisesRegex(upgrade.UpgradeError,'maxUnavailable'):
   upgrade.build_patch(dep,None,'quorivio-app-secrets','desalvo/quorivio-converter:latest')

 def test_explicit_integer_can_disrupt(self):
  dep=fixture(1)['deployment/quorivio']
  dep['spec']['strategy']['rollingUpdate']['maxUnavailable']=1
  self.assertEqual(upgrade.effective_rollout_unavailability(dep),1)
  with self.assertRaisesRegex(upgrade.UpgradeError,'maxUnavailable'):
   upgrade.build_patch(dep,None,'quorivio-app-secrets','desalvo/quorivio-converter:latest')

 def test_recreate_and_stalled_rollingupdate_rejected(self):
  dep=fixture()['deployment/quorivio']
  dep['spec']['strategy']={'type':'Recreate'}
  with self.assertRaisesRegex(upgrade.UpgradeError,'Recreate'):
   upgrade.effective_rollout_unavailability(dep)
  dep['spec']['strategy']={'type':'RollingUpdate','rollingUpdate':{'maxUnavailable':0,'maxSurge':0}}
  with self.assertRaisesRegex(upgrade.UpgradeError,'stall'):
   upgrade.effective_rollout_unavailability(dep)

 def test_invalid_or_unknown_strategy_is_rejected(self):
  dep=fixture()['deployment/quorivio']
  for value in (True,-1,'foo','101%','-5%'):
   dep['spec']['strategy']['rollingUpdate']['maxUnavailable']=value
   with self.subTest(value=value),self.assertRaises(upgrade.UpgradeError):
    upgrade.effective_rollout_unavailability(dep)
  dep['spec']['strategy']={'type':'Unknown'}
  with self.assertRaises(upgrade.UpgradeError):
   upgrade.effective_rollout_unavailability(dep)


class SingleFileWizard(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.dir=Path(self.tmp.name)
  self.wizard=self.dir/'k8s_wizard.py'
  shutil.copy2(TOOLS/'k8s_wizard.py',self.wizard)
  self.fake=self.dir/'fake_kubectl.py'
  self.fake.write_text(FAKE_KUBECTL)
  self.fake.chmod(0o700)
  self.state=self.dir/'state.json'
  self.state.write_text(json.dumps(fixture()))
  self.env={**os.environ,'FAKE_KUBECTL_STATE':str(self.state),'PYTHONPATH':''}

 def run_cli(self,*args,ok=True):
  result=subprocess.run([sys.executable,str(self.wizard),'--no-self-update',*args],cwd=self.dir,env=self.env,
   text=True,capture_output=True,timeout=20)
  if ok:self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
  else:self.assertNotEqual(result.returncode,0)
  return result

 def test_embedded_sources_match_canonical_modules(self):
  for name in ('k8s_converter_upgrade','k8s_cluster_inspection'):
   source=(TOOLS/(name+'.py')).read_text()
   self.assertEqual(k8s_wizard._STANDALONE_COMPONENT_SOURCES[name],source)
   self.assertEqual(k8s_wizard._STANDALONE_COMPONENT_SHA256[name],hashlib.sha256(source.encode()).hexdigest())

 def test_one_file_generation_without_any_repository_module(self):
  result=self.run_cli('--unattended','--output',str(self.dir/'fresh-install'), '--set','host=qa.example.org')
  self.assertIn('Generated Kustomize base',result.stdout)
  out=self.dir/'fresh-install'
  self.assertTrue((out/'20-deployment.yaml').is_file())
  self.assertTrue((out/'05-app-secret.yaml').is_file())
  self.assertTrue((out/'kustomization.yaml').is_file())
  self.assertEqual((out/'05-app-secret.yaml').stat().st_mode & 0o777,0o600)
  self.assertFalse((self.dir/'k8s_converter_upgrade.py').exists())

 def test_one_file_inspection_without_kube_modules(self):
  result=self.run_cli('--inspect-cluster','--output',str(self.dir/'inspection'),
   '--kubectl',str(self.fake),'--set','namespace=quorivio','--set','name=quorivio')
  self.assertIn('Read-only inventory saved',result.stdout)
  data=json.loads((self.dir/'inspection/quorivio-cluster-discovery.json').read_text())
  self.assertEqual(data['overrides']['replicas'],2)
  self.assertEqual(data['overrides']['image'],'desalvo/quorivio:latest')

 def test_one_file_token_plan_apply_and_no_postgres_update(self):
  self.run_cli('--ensure-converter-token','--kubectl',str(self.fake), '--set','namespace=quorivio','--set','name=quorivio')
  updated=json.loads(self.state.read_text())
  self.assertIn('QUORIVIO_WORKER_TOKEN',updated['secret/quorivio-app-secrets']['data'])
  self.assertEqual(updated['deployment/quorivio']['spec']['replicas'],2)
  out=self.dir/'plan'
  result=self.run_cli('--upgrade-converter','--kubectl',str(self.fake),'--set','namespace=quorivio',
    '--set','name=quorivio','--converter-image','desalvo/quorivio-converter:latest','--output',str(out))
  self.assertIn('Converter-only upgrade plan prepared',result.stdout)
  self.assertEqual(json.loads(self.state.read_text())['deployment/quorivio']['spec']['template']['spec']['containers'][0]['name'],'quorivio')
  patch=json.loads((out/'converter-patch.json').read_text())
  self.assertNotIn('DATABASE_URL',json.dumps(patch))
  self.assertNotIn('postgres://db',json.dumps(patch))
  self.assertTrue(any(x['op']=='add' and x['path']=='/spec/template/spec/containers/-' for x in patch))
  self.run_cli('--apply-converter','--kubectl',str(self.fake),'--output',str(out))
  current=json.loads(self.state.read_text())['deployment/quorivio']
  self.assertEqual(len(current['spec']['template']['spec']['containers']),2)
  self.assertEqual(current['spec']['template']['spec']['containers'][-1]['image'],'desalvo/quorivio-converter:latest')
  self.assertEqual(current['spec']['strategy']['rollingUpdate']['maxUnavailable'],'25%')

 def test_four_replicas_safe_refusal_without_mutation(self):
  self.state.write_text(json.dumps(fixture(4,include_token=True)))
  before=self.state.read_text()
  error=self.run_cli('--upgrade-converter','--kubectl',str(self.fake),
    '--set','namespace=quorivio','--set','name=quorivio',
    '--converter-image','desalvo/quorivio-converter:latest','--output',str(self.dir/'plan'),ok=False)
  self.assertIn('maxUnavailable',error.stderr)
  self.assertEqual(before,self.state.read_text())

if __name__=='__main__':unittest.main()
