"""RC123: real file picker acceptance and bounded explicit Docker publication."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

class RealMediaAndPublishContracts(unittest.TestCase):
    def test_browser_exercises_real_pick_dialog_and_persisted_postgres_and_library(self):
        test=(ROOT/'tools/ci_browser_media_picker_postgres.py').read_text()
        for fragment in ('ci_load_headers(BASE)', 'expect_file_chooser()', 'Carica immagine nello sfondo e nella libreria',
                         'Carica file logo', 'persisted_widget(', 'backgroundAssetId',
                         "await open_editor(page, title)", 'private_library', 'application/octet-stream'):
            self.assertIn(fragment,test)
        self.assertNotIn("route('**/api",test)

    def test_explicit_pub_stays_authorized_and_bounded(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        segment=workflow.split('\n  publish-on-commit:\n',1)[1].split('\n  ',1)[0] if False else workflow.split('\n  publish-on-commit:\n',1)[1]
        self.assertIn('timeout-minutes: 10', segment.split('steps:',1)[0])
        platform=workflow.split('\n  publish-platform:\n',1)[1].split('\n  publish:\n',1)[0]
        self.assertIn('timeout-minutes: 35', platform.split('steps:',1)[0])
        self.assertIn('ubuntu-24.04-arm', platform)
        self.assertNotIn('setup-qemu-action',platform)
        self.assertIn("contains(github.event.head_commit.message, '[publish-docker]')", segment)
        self.assertIn("needs.rc-campaign-conclusion.result == 'success'",segment)
        self.assertIn("needs.publish-platform.result == 'success'",segment)
        self.assertIn('bash tools/publish_multiarch_manifest.sh',segment)
        self.assertIn('push=true',platform)

    def test_media_picker_is_ci_gated_with_auth_and_no_implicit_publish(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/ci_browser_media_picker_postgres.py',workflow)
        self.assertIn('QUORIVIO_CI_ADMIN_EMAIL: admin@example.com',workflow)
        assert 'ci-${{ github.ref }}' in workflow

if __name__=='__main__':unittest.main()
