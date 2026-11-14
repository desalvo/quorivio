"""RC340: app and converter images must refresh together in default deployments."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class PairedImages(unittest.TestCase):
    def test_helm_defaults_do_not_pin_converter_to_legacy_dev_image(self):
        values = (ROOT/'helm/quorivio/values.yaml').read_text(encoding='utf8')
        deployment = (ROOT/'helm/quorivio/templates/deployment.yaml').read_text(encoding='utf8')
        self.assertIn('repository: desalvo/quorivio', values)
        self.assertIn('tag: latest', values)
        self.assertIn('pullPolicy: Always', values)
        self.assertIn('image: "desalvo/quorivio-converter:latest"', values)
        self.assertIn('imagePullPolicy: Always', values)
        self.assertNotIn('quorivio-converter:0.1.0-dev', values)
        self.assertIn('image: {{ .Values.converter.image | quote }}', deployment)
        self.assertIn('imagePullPolicy: {{ .Values.converter.imagePullPolicy }}', deployment)

    def test_compose_can_pull_matching_published_converter_image(self):
        compose = (ROOT/'compose.yaml').read_text(encoding='utf8')
        self.assertIn('QUORIVIO_IMAGE:-desalvo/quorivio:latest', compose)
        self.assertIn('QUORIVIO_CONVERTER_IMAGE:-desalvo/quorivio-converter:latest', compose)
        self.assertIn('dockerfile: Dockerfile.converter', compose)
        self.assertIn('QUORIVIO_CAPTURE_BASE_URL: http://app:8080', compose)

if __name__ == '__main__':
    unittest.main()
