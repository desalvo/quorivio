"""RC96: prevent recurrent false CI failures at a calendar-day rollover."""
from __future__ import annotations

import re
import unittest
from datetime import datetime
from pathlib import Path

from verify_rc_current_inventory import current_verifier_module
from ci_inventory_reference_guard import verify_references

ROOT = Path(__file__).resolve().parents[2]


class ReleaseDateAndStatusAcceptance(unittest.TestCase):
    def test_active_inventory_has_calendar_date_and_current_verifier(self):
        module = current_verifier_module()
        self.assertEqual(module.__name__, 'verify_rc_cycle96_inventory')
        match = re.fullmatch(r'docs/validation/RC_CYCLE96_PACKAGE_INVENTORY_(20[0-9]{6})\.json', module.MANIFEST)
        self.assertIsNotNone(match)
        self.assertEqual(datetime.strptime(match.group(1), '%Y%m%d').strftime('%Y%m%d'), match.group(1))
        self.assertGreaterEqual(verify_references(enforce_git=False), 34)

    def test_all_four_current_status_headers_keep_explicit_release_flags(self):
        for name in ('DEVELOPMENT_STATUS.md','DEVELOPMENT_STATUS.it.md',
                     'COMPLETION_HANDOFF.md','COMPLETION_HANDOFF.it.md'):
            with self.subTest(name=name):
                current = (ROOT/'docs'/name).read_text(encoding='utf8').split('\n---\n',1)[0]
                self.assertIn('RC96', current)
                for flag in ('rc_strict=false', 'publish_image=false', 'publish_latest=false'):
                    self.assertIn(flag, current)

    def test_previous_receipts_remain_historical_in_workflow(self):
        wf=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('python3 tools/verify_rc_cycle95_inventory.py --historical',wf)
        self.assertIn('python3 tools/verify_rc_cycle96_inventory.py',wf)
        self.assertLess(wf.index('python3 tools/verify_rc_cycle95_inventory.py --historical'),
                        wf.index('python3 tools/verify_rc_cycle96_inventory.py'))


if __name__ == '__main__':
    unittest.main()
