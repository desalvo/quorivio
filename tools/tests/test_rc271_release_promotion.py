"""RC271 regression for a stale current inventory and missing RC270 CI tests."""
from pathlib import Path
import re
import unittest

from tools.ci_inventory_reference_guard import COMMAND, verify_references
from tools.verify_rc_release_status import FILES, verify_headers
from tools.verify_rc_current_inventory import current_verifier_module

ROOT=Path(__file__).resolve().parents[2]

class RC271ReleasePromotion(unittest.TestCase):
    def test_current_inventory_matches_active_docs(self):
        self.assertRegex(current_verifier_module().__name__, r'^verify_rc_cycle[0-9]+_inventory$')
        current_cycle=re.search(r'cycle([0-9]+)',current_verifier_module().__name__).group(1)
        self.assertEqual(verify_headers(ROOT),len(FILES))
        for name in FILES:
            title=(ROOT/'docs'/name).read_text(encoding='utf8').splitlines()[0]
            self.assertRegex(title,rf'(?<![A-Za-z0-9])RC{current_cycle}(?![0-9])')
    def test_rc269_historical_and_rc271_current(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        commands=COMMAND.findall(workflow)
        self.assertIn(('verify_rc_cycle269_inventory.py','--historical'), commands)
        self.assertIn(('verify_rc_cycle271_inventory.py','--historical'), commands)
        self.assertEqual(commands[-1],(current_verifier_module().__name__+'.py',''))
        self.assertEqual(verify_references(ROOT,enforce_git=False),len(commands))
    def test_rc270_tests_run_before_npm(self):
        w=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('apps/api/test/rc270-backup-audit.test.ts',w)
        self.assertIn('tools.test_rc270_wizard_backup',w)
        self.assertIn('tools.tests.test_rc271_release_promotion',w)
        self.assertLess(w.index('RC270 full backup'),w.index('RC269 auth LDAP'))
        self.assertLess(w.index('RC271 metadata'),w.index('RC269 auth LDAP'))

if __name__=='__main__':
    unittest.main()
