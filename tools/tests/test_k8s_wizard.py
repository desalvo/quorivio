import sys,unittest,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from k8s_wizard import DEFAULTS,generate,validate
class WizardTests(unittest.TestCase):
 def test_deterministic(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);generate(dict(DEFAULTS),d);a={f.name:f.read_bytes() for f in d.iterdir()};generate(dict(DEFAULTS),d);self.assertEqual(a,{f.name:f.read_bytes() for f in d.iterdir()})
 def test_overrides_only(self):
  with tempfile.TemporaryDirectory() as td:
   c=dict(DEFAULTS,host='q.example.org');generate(c,Path(td));self.assertEqual((Path(td)/'quorivio-overrides.json').read_text().strip(),'\u007b\n  "host": "q.example.org"\n\u007d')
 def test_invalid_host(self):
  with self.assertRaises(ValueError):validate(dict(DEFAULTS,host='hello:bad'))
 def test_no_plain_secret(self):
  with tempfile.TemporaryDirectory() as td:
   generate(dict(DEFAULTS),Path(td));self.assertNotIn('password:',(Path(td)/'20-deployment.yaml').read_text())
if __name__=='__main__':unittest.main()

class InfrastructureVariants(unittest.TestCase):
 def test_internal_postgres(self):
  with tempfile.TemporaryDirectory() as td:
   generate(dict(DEFAULTS),Path(td));self.assertTrue((Path(td)/'12-postgres-statefulset.yaml').exists())
   self.assertIn('postgres:18.6-alpine',(Path(td)/'12-postgres-statefulset.yaml').read_text())
   self.assertIn('DATABASE_URL',(Path(td)/'20-deployment.yaml').read_text())
 def test_external_postgres_without_statefulset(self):
  with tempfile.TemporaryDirectory() as td:
   cfg=validate(dict(DEFAULTS,postgres_mode='external',postgres_host='db.example.org',postgres_sslmode='verify-full'))
   generate(cfg,Path(td));self.assertFalse((Path(td)/'12-postgres-statefulset.yaml').exists())
   self.assertIn('db.example.org',(Path(td)/'10-configmap.yaml').read_text())
 def test_haproxy_variants(self):
  for variant,annotation in [('community','kubernetes.io/ingress.class'),('haproxytech','haproxy.org/ingress.class')]:
   with self.subTest(variant=variant), tempfile.TemporaryDirectory() as td:
    generate(validate(dict(DEFAULTS,ingress_controller='haproxy',haproxy_variant=variant)),Path(td))
    self.assertIn(annotation,(Path(td)/'40-ingress.yaml').read_text())
 def test_nginx(self):
  with tempfile.TemporaryDirectory() as td:
   generate(dict(DEFAULTS),Path(td));ingress=(Path(td)/'40-ingress.yaml').read_text()
   self.assertIn('ingressClassName: nginx',ingress)
   self.assertNotIn('ingress.class:',ingress)
 def test_reject_external_without_tls(self):
  with self.assertRaises(ValueError):validate(dict(DEFAULTS,postgres_mode='external',postgres_host='db.example.org',postgres_sslmode='disable'))
 def test_reject_multi_replica(self):
  with self.assertRaises(ValueError):validate(dict(DEFAULTS,replicas=2))

 def test_switch_internal_to_external_removes_stale_files(self):
  with tempfile.TemporaryDirectory() as td:
   generate(dict(DEFAULTS),Path(td))
   generate(validate(dict(DEFAULTS,postgres_mode='external',postgres_host='db.example.org')),Path(td))
   self.assertFalse((Path(td)/'12-postgres-statefulset.yaml').exists())
   self.assertNotIn('12-postgres-statefulset.yaml',(Path(td)/'kustomization.yaml').read_text())
