import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from k8s_wizard import DEFAULTS
ROOT=Path(__file__).resolve().parents[2]
class ImageDefaults(unittest.TestCase):
 def test_kubernetes_image(self):
  self.assertEqual(DEFAULTS['image'], 'desalvo/quorivio:latest')
 def test_compose_image(self):
  self.assertIn('QUORIVIO_IMAGE:-desalvo/quorivio:latest', (ROOT/'compose.yaml').read_text())
 def test_ci_publish(self):
  workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  # Native images are pushed by digest, then the approved tags are
  # assembled only after both image architectures have been verified.
  import yaml
  jobs=yaml.safe_load(workflow)['jobs']
  self.assertIn('publish-platform', jobs['publish']['needs'])
  self.assertIn('push-by-digest=true', str(jobs['publish-platform']['steps']))
  self.assertIn('publish-converter-platform', jobs['publish']['needs'])
  self.assertIn('push-by-digest=true', str(jobs['publish-converter-platform']['steps']))
  self.assertIn('QUORIVIO_IMAGE_TAGS: ${{ steps.label.outputs.tags }}', workflow)
  self.assertIn('bash tools/publish_both_multiarch_manifest.sh',workflow)
  self.assertIn('inputs.publish_image == true', workflow)
  self.assertIn("github.event_name == 'workflow_dispatch'", workflow)
  self.assertIn('bash tools/resolve_image_tags.sh', workflow)
 def test_revote_migration(self):
  sql=(ROOT/'apps/api/src/schema.sql').read_text()
  self.assertIn('uq_responses_active_vote', sql)
  self.assertIn('WHERE invalidated_at IS NULL', sql)
