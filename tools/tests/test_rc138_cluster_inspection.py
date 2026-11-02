"""RC138: read-only wizard import must preserve existing cluster resources and secrets."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from k8s_cluster_inspection import derive_nonsecret_config,inspect_resources,save_report
from k8s_wizard import main

class ReadOnlyClusterInspection(unittest.TestCase):
 def test_import_live_nonsecret_metadata_without_secret_reads(self):
  resources={
   'deployment':{'spec':{'replicas':1,'template':{'spec':{'nodeSelector':{'kubernetes.io/arch':'amd64'},'securityContext':{'fsGroup':1000},'containers':[{'name':'quorivio','image':'desalvo/quorivio:latest'}]}}}},
   'configmap':{'data':{'CLAMAV_HOST':'quorivio-clamav','QUORIVIO_AV_REQUIRED':'true','PUBLIC_BASE_URL':'https://talk.example.org','MAX_UPLOAD_MB':'100'}},
   'assets_pvc':{'spec':{'storageClassName':'csi-proxmox-cephfs-sc','accessModes':['ReadWriteOnce'],'resources':{'requests':{'storage':'30Gi'}}}},
   'ingress':{'spec':{'ingressClassName':'haproxy','rules':[{'host':'talk.example.org'}],'tls':[{'secretName':'quorivio-tls'}]}},
   'clamav_deployment':{'kind':'Deployment'},'clamav_service':{'kind':'Service'},
   'postgres_statefulset':{'spec':{'template':{'spec':{'containers':[{'image':'postgres:18.6-alpine'}]}}}},
   'postgres_service':{'kind':'Service'}
  }
  report=derive_nonsecret_config(resources,'quorivio','quorivio')
  cfg=report['overrides']
  for k,v in {'host':'talk.example.org','asset_storage_size':'30Gi','asset_storage_class':'csi-proxmox-cephfs-sc','antivirus_mode':'managed','postgres_mode':'internal','app_node_selector':'kubernetes.io/arch=amd64'}.items():self.assertEqual(cfg[k],v)
  self.assertFalse(any('password' in k.lower() or 'secret' in k.lower() and k!='tls_secret' for k in cfg))
  with tempfile.TemporaryDirectory() as tmp:
   save_report(Path(tmp),report)
   self.assertNotIn('AUTH_SECRET',(Path(tmp)/'quorivio-cluster-discovery.json').read_text())
   self.assertFalse((Path(tmp)/'05-app-secret.yaml').exists())
 def test_inspector_only_issues_get_commands_and_sanitizes_failures(self):
  class Result:
   returncode=0
   stdout=''
  calls=[]
  def fake(args,**kwargs):calls.append(args);return Result()
  with patch('k8s_cluster_inspection.subprocess.run',side_effect=fake):
   inspected=inspect_resources('quorivio','quorivio')
  self.assertEqual(len(inspected),8)
  self.assertTrue(all('get' in args and 'apply' not in args and 'delete' not in args and 'secret' not in args for args in calls))
  self.assertRaises(ValueError,inspect_resources,'quorivio; rm -rf /','quorivio')
 def test_cli_inspect_exits_without_generating_manifests_or_secrets(self):
  with tempfile.TemporaryDirectory() as tmp, patch('k8s_cluster_inspection.inspect_resources',return_value={}):
   rc=main(['--inspect-cluster','--output',tmp,'--set','namespace=quorivio'])
   self.assertEqual(rc,0)
   self.assertTrue((Path(tmp)/'quorivio-cluster-discovery.json').exists())
   self.assertFalse((Path(tmp)/'05-app-secret.yaml').exists())
   self.assertFalse((Path(tmp)/'20-deployment.yaml').exists())
