"""RC246: converter image publication must remain an explicit, separate manual action."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
WORKFLOW=ROOT/'.github/workflows/converter-image.yml'
K8S=ROOT/'tools/k8s_wizard.py'


class ManualConverterPublisher(unittest.TestCase):
    def setUp(self):self.workflow=WORKFLOW.read_text(encoding='utf8')

    def test_dispatch_only_explicit_approval(self):
        s=self.workflow
        self.assertIn('workflow_dispatch:',s)
        self.assertNotIn('\n  push:',s)
        self.assertNotIn('\n  pull_request:',s)
        self.assertIn('inputs.confirm_publish == true',s)
        self.assertIn("github.ref == 'refs/heads/main'",s)
        self.assertIn('environment: production',s)

    def test_dedicated_converter_dockerfile_and_registry(self):
        s=self.workflow
        self.assertIn('file: Dockerfile.converter',s)
        self.assertIn('desalvo/quorivio-converter:$image_tag',s)
        self.assertIn('platforms: linux/amd64,linux/arm64',s)
        self.assertIn('docker/setup-qemu-action@v3',s)
        self.assertIn('sbom: true',s)
        self.assertIn('provenance: mode=max',s)

    def test_credential_hygiene(self):
        s=self.workflow
        self.assertIn('username: ${{ vars.DOCKERHUB_USERNAME }}',s)
        self.assertIn('password: ${{ secrets.DOCKERHUB_TOKEN }}',s)
        self.assertIn('persist-credentials: false',s)
        self.assertNotIn('password: "',s)
        self.assertNotIn('sudo docker login',s)

    def test_immutable_and_two_arch_validation(self):
        s=self.workflow
        self.assertIn('image_tag=latest',s)
        self.assertIn('refs/tags/',s)
        self.assertIn('docker buildx imagetools inspect',s)
        self.assertIn("grep -q 'linux/amd64'",s)
        self.assertIn("grep -q 'linux/arm64'",s)
        self.assertIn('^sha256:[0-9a-f]{64}$',s)

    def test_wizard_never_clears_old_installation(self):
        s=K8S.read_text(encoding='utf8')
        self.assertIn("modes.add_argument('--upgrade-converter'",s)
        self.assertIn("modes.add_argument('--apply-converter'",s)
        self.assertIn("modes.add_argument('--ensure-converter-token'",s)
        self.assertIn('prepare_upgrade(',s)
        self.assertIn('apply_upgrade(',s)
        self.assertIn('plan_token_provision(',s)
        self.assertNotIn('kubectl apply -k',s)


if __name__=='__main__':unittest.main()
