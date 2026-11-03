"""RC146: prevent stale handoff headings from silently shipping again."""
from __future__ import annotations

import unittest
from pathlib import Path

from tools.verify_rc_release_status import FILES, FLAGS, verify_headers
from tools.verify_rc_current_inventory import current_verifier_module

ROOT = Path(__file__).resolve().parents[2]


class ReleaseHeaderHotfixTests(unittest.TestCase):
    def test_rc146_release_and_localized_percentages_survive_as_history(self):
        # RC146 is immutable history after the next cycle. The active headers
        # must follow the *current* inventory rather than always be RC146.
        self.assertEqual(verify_headers(ROOT), len(FILES))
        for name in FILES:
            entire = (ROOT / 'docs' / name).read_text(encoding='utf8')
            current = entire.split('\n---\n', 1)[0]
            self.assertIn('RC146', entire, name)
            self.assertTrue(all(flag in current for flag in FLAGS), name)
            score = '85,25%' if name.endswith('.it.md') else '85.25%'
            self.assertIn(score, current, name)

    def test_ci_keeps_rc146_receipt_historical(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('python3 tools/verify_rc_cycle145_inventory.py --historical', workflow)
        self.assertIn('python3 tools/verify_rc_cycle146_inventory.py --historical', workflow)
        self.assertIn('tools.tests.test_rc146_release_header_fix', workflow)
        self.assertGreaterEqual(int(current_verifier_module().__name__.split('cycle')[1].split('_')[0]), 147)

    def test_earlier_mobile_fixes_and_archives_survive(self):
        docs = ROOT / 'docs'
        self.assertIn('RC145', (docs / 'DEVELOPMENT_STATUS.md').read_text(encoding='utf8'))
        self.assertIn('RC144', (docs / 'COMPLETION_HANDOFF.md').read_text(encoding='utf8'))
        self.assertIn('RC143', (docs / 'COMPLETION_HANDOFF.it.md').read_text(encoding='utf8'))
        self.assertTrue((docs / 'validation/RC_CYCLE145_PACKAGE_INVENTORY_20261103.json').is_file())

if __name__ == '__main__':
    unittest.main()
