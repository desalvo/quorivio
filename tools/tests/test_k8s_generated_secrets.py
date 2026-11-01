import base64, json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from k8s_wizard import DEFAULTS, generate, validate

class GeneratedSecretsTests(unittest.TestCase):
    def test_creates_required_secret_and_preserves_on_rerun(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)
            generate(dict(DEFAULTS),path)
            before=(path/'quorivio-overrides.json').read_bytes()
            secrets=json.loads(before)
            for k in ('admin_password','auth_secret','postgres_password'):
                self.assertTrue(len(secrets[k])>=12)
            yaml=(path/'05-app-secret.yaml').read_text()
            for k in ('DATABASE_URL','POSTGRES_PASSWORD','AUTH_SECRET','ADMIN_PASSWORD','ADMIN_EMAIL'):
                self.assertIn('  '+k+': ',yaml)
            self.assertIn('05-app-secret.yaml',(path/'kustomization.yaml').read_text())
            generate(dict(DEFAULTS),path)
            self.assertEqual(before,(path/'quorivio-overrides.json').read_bytes())
            self.assertEqual(os.stat(path/'quorivio-overrides.json').st_mode&0o777,0o600)
            self.assertEqual(os.stat(path/'05-app-secret.yaml').st_mode&0o777,0o600)
    def test_external_database_needs_real_password(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError,'requires postgres_password'):
                generate(validate(dict(DEFAULTS,postgres_mode='external',postgres_host='db.example.org')),Path(directory))
    def test_external_database_skips_internal_password_key(self):
        with tempfile.TemporaryDirectory() as directory:
            cfg=dict(DEFAULTS,postgres_mode='external',postgres_host='db.example.org',postgres_password='test-only-database-password')
            generate(validate(cfg),Path(directory))
            self.assertNotIn('  POSTGRES_PASSWORD:',(Path(directory)/'05-app-secret.yaml').read_text())
    def test_db_url_password_is_percent_encoded(self):
        with tempfile.TemporaryDirectory() as directory:
            cfg=dict(DEFAULTS,postgres_password='password:/@?#abcdef')
            generate(validate(cfg),Path(directory))
            text=(Path(directory)/'05-app-secret.yaml').read_text()
            line=next(line for line in text.splitlines() if line.startswith('  DATABASE_URL: '))
            decoded=base64.b64decode(line.split(': ',1)[1]).decode()
            self.assertIn('password%3A%2F%40%3F%23abcdef',decoded)
