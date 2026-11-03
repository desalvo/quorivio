"""RC146: prevent stale handoff headings from silently shipping again."""
from __future__ import annotations

import unittest
from pathlib import Path

from tools.verify_rc_release_status import FILES, FLAGS, verify_headers
from tools.verify_rc_current_inventory import current_verifier_module

ROOT = Path(__file__).resolve().parents[2]


class ReleaseHeaderHotfixTests(unittest.TestCase):
    def test_active_release_and_localized_percentages(self):
        self.assertEqual(verify_headers(ROOT, 146), len(FILES))
        for name in FILES:
            current = (ROOT / 'docs' / name).read_text(encoding='utf8').split('\n---\n', 1)[0]
            self.assertTrue(current.startswith('# Quorivio 0.1.0-dev — RC146 —'), name)
            self.assertTrue(all(flag in current for flag in FLAGS), name)
            score = '85,25%' if name.endswith('.it.md') else '85.25%'
            self.assertIn(score, current, name)

    def test_ci_uses_rc146_as_current_and_rc145_as_historical(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('python3 tools/verify_rc_cycle145_inventory.py --historical', workflow)
        self.assertIn('python3 tools/verify_rc_cycle146_inventory.py', workflow)
        self.assertIn('tools.tests.test_rc146_release_header_fix', workflow)
        self.assertEqual(current_verifier_module().__name__, 'verify_rc_cycle146_inventory')

    def test_earlier_mobile_fixes_and_archives_survive(self):
        docs = ROOT / 'docs'
        self.assertIn('RC145', (docs / 'DEVELOPMENT_STATUS.md').read_text(encoding='utf8'))
        self.assertIn('RC144', (docs / 'COMPLETION_HANDOFF.md').read_text(encoding='utf8'))
        self.assertIn('RC143', (docs / 'COMPLETION_HANDOFF.it.md').read_text(encoding='utf8'))
        self.assertTrue((docs / 'validation/RC_CYCLE145_PACKAGE_INVENTORY_20261103.json').is_file())

if __name__ == '__main__':
    unittest.main()
