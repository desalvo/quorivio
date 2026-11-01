import tempfile
import unittest
from pathlib import Path
from tools.k8s_wizard import DEFAULTS, generate, validate, parse_node_selector

class KubernetesWizardDeploymentTests(unittest.TestCase):
    def render(self, **settings):
        cfg={**DEFAULTS,**settings}
        validate(cfg)
        with tempfile.TemporaryDirectory() as d:
            generate(cfg,Path(d))
            return {p.name:p.read_text() for p in Path(d).glob('*.yaml')}
    def test_default_image(self):
        self.assertEqual(DEFAULTS['image'],'desalvo/quorivio:latest')
    def test_ingress_tls_without_app_secret(self):
        y=self.render(tls_termination=True,tls_secret='')['40-ingress.yaml']
        self.assertIn('  tls:',y)
        self.assertNotIn('secretName:',y)
    def test_ingress_with_secret(self):
        self.assertIn('secretName: my-cert',self.render(tls_secret='my-cert')['40-ingress.yaml'])
    def test_tls_disabled(self):
        self.assertNotIn('  tls:',self.render(tls_termination=False)['40-ingress.yaml'])
    def test_selectors_scoped_to_pods(self):
        result=self.render(app_node_selector='kubernetes.io/arch=amd64,disktype=ssd',postgres_node_selector='disk=fast')
        self.assertIn('"kubernetes.io/arch": "amd64"',result['20-deployment.yaml'])
        self.assertNotIn('"disk": "fast"',result['20-deployment.yaml'])
        self.assertIn('"disk": "fast"',result['12-postgres-statefulset.yaml'])
        self.assertNotIn('"disktype": "ssd"',result['12-postgres-statefulset.yaml'])
    def test_invalid_selector_rejected(self):
        for selector in ['bad','wrong key=x','key=x,key=y','/key=value','k=invalid value']:
            with self.subTest(selector=selector):
                with self.assertRaises(ValueError):parse_node_selector(selector)
    def test_external_database_has_no_postgres_pod(self):
        y=self.render(postgres_mode='external',postgres_host='pg.example.com',postgres_node_selector='disk=ssd',postgres_password='test-only-database-password')
        self.assertNotIn('12-postgres-statefulset.yaml',y)
if __name__=='__main__':unittest.main()
