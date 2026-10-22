import unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
class ManagedAntivirusTest(unittest.TestCase):
    def test_compose_bundles_scanner_privately(self):
        cfg=yaml.safe_load((ROOT/'compose.yaml').read_text())
        self.assertIn('clamav',cfg['services'])
        self.assertNotIn('ports',cfg['services']['clamav'])
        app=cfg['services']['app']
        self.assertEqual(app['environment']['QUORIVIO_AV_REQUIRED'],'true')
        self.assertEqual(app['environment']['CLAMAV_HOST'],'clamav')
        self.assertIn('clamav',app['depends_on'])
        self.assertIn('clamav-signatures',cfg['volumes'])
    def test_helm_bundles_private_sidecar(self):
        text=(ROOT/'helm/quorivio/templates/deployment.yaml').read_text()
        self.assertIn('name: clamav',text)
        self.assertIn('127.0.0.1',text)
        self.assertIn('QUORIVIO_AV_REQUIRED',text)
    def test_provider_defaults_have_no_secrets(self):
        env=(ROOT/'.env.example').read_text()
        self.assertIn('https://accounts.google.com',env)
        self.assertIn('https://github.com/login/oauth/authorize',env)
        self.assertIn('https://www.facebook.com/',env)
