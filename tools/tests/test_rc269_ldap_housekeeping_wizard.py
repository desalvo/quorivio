"""RC269 Kubernetes LDAP secret and exclusive-PVC deployment regression tests."""
import base64
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import k8s_wizard as wizard

class RC269LdapWizard(unittest.TestCase):
 def config(self):
  cfg=dict(wizard.DEFAULTS)
  cfg.update(host='demo.example.org',admin_password='strong-example-pass-1234',auth_secret='12345678901234567890123456789012',postgres_password='strong-example-db-pass',ldap_enabled=True,ldap_url='ldaps://ldap.example.org:636',ldap_bind_dn='cn=svc,dc=example,dc=org',ldap_bind_password='test-secret-that-must-be-private',ldap_base_dn='dc=example,dc=org')
  return cfg
 def test_secret_is_private_and_configmap_contains_no_bind_password(self):
  cfg=self.config();wizard.validate(cfg)
  with tempfile.TemporaryDirectory() as temp:
   dest=Path(temp)
   wizard.generate(cfg,dest)
   secret=(dest/'05-app-secret.yaml').read_text();mapping=(dest/'10-configmap.yaml').read_text();deploy=(dest/'20-deployment.yaml').read_text()
   self.assertIn('LDAP_BIND_PASSWORD:',secret)
   self.assertIn(base64.b64encode(cfg['ldap_bind_password'].encode()).decode(),secret)
   self.assertNotIn('LDAP_BIND_PASSWORD',mapping)
   self.assertNotIn(cfg['ldap_bind_password'],mapping)
   self.assertIn('LDAP_URL:',mapping)
   self.assertIn('type: Recreate',deploy)
   self.assertIn('imagePullPolicy: Always',deploy)
   self.assertEqual((dest/'05-app-secret.yaml').stat().st_mode&0o777,0o600)
 def test_ldap_plain_without_starttls_is_rejected(self):
  cfg=self.config();cfg['ldap_url']='ldap://ldap.example.org:389'
  with self.assertRaisesRegex(ValueError,'StartTLS'):wizard.validate(cfg)
  cfg['ldap_starttls']=True
  wizard.validate(cfg)
 def test_unknown_org_auto_provision_is_rejected(self):
  cfg=self.config();cfg['ldap_auto_provision']=True
  with self.assertRaisesRegex(ValueError,'organization'):wizard.validate(cfg)
if __name__=='__main__':unittest.main()
