"""RC100: reject stale headers even if a historical section mentions the active cycle."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.verify_rc_release_status import verify_headers, FILES, FLAGS

ROOT = Path(__file__).resolve().parents[2]


class ReleaseStatusGuardTests(unittest.TestCase):
    def test_all_current_headers_and_flags(self):
        self.assertEqual(verify_headers(ROOT), 4)

    def test_stale_active_heading_cannot_be_masked_by_historical_release_notes(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp) / 'docs'
            docs.mkdir()
            for name in FILES:
                (docs / name).write_text('# Quorivio RC98 stale\n' + ' '.join(FLAGS) +
                    '\n\n---\n\n# Release RC100 historical\n', encoding='utf8')
            with self.assertRaisesRegex(ValueError, 'active heading'):
                verify_headers(Path(tmp), 100)

    def test_missing_flag_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            docs = Path(tmp) / 'docs'
            docs.mkdir()
            for name in FILES:
                (docs / name).write_text('# Quorivio RC100 current\n' + ' '.join(FLAGS), encoding='utf8')
            (docs / FILES[0]).write_text('# Quorivio RC100 current\n' + ' '.join(FLAGS[:-1]), encoding='utf8')
            with self.assertRaisesRegex(ValueError, 'release flags'):
                verify_headers(Path(tmp), 100)

    def test_future_cycle_reference_uses_current_workflow(self):
        # The guard follows the single active inventory, not a hardcoded RC100.
        self.assertEqual(verify_headers(ROOT), len(FILES))


if __name__ == '__main__':
    unittest.main()
