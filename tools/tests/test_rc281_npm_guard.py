"""RC281: preserve the RC274 legacy installer ban without false positive in RC280.

The RC280 negative assertion must still reject a non-reproducible install step;
the RC274 scanner is deliberately kept strict over historical Python tests.
"""
import unittest
from pathlib import Path
from tools.tests.test_rc274_ci_integrity import RC274CiIntegrity
from tools.tests.test_rc280_npm_lock import RC280LockfileContract

ROOT = Path(__file__).resolve().parents[2]
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
PREVIOUS = (ROOT / 'tools/tests/test_rc280_npm_lock.py').read_text(encoding='utf8')

class RC281NpmGuard(unittest.TestCase):
 def test_historical_ci_scanner_accepts_negative_assertions(self):
  RC274CiIntegrity('test_historical_test_order_contracts_moved_without_relaxing_order').test_historical_test_order_contracts_moved_without_relaxing_order()

 def test_ldap_lockfile_gate_still_rejects_nonreproducible_install(self):
  RC280LockfileContract('test_ci_tests_before_npm_ci_in_both_jobs').test_ci_tests_before_npm_ci_in_both_jobs()
  legacy='run: npm'+' install --ignore-scripts --no-audit --no-fund'
  self.assertNotIn(legacy, CI)
  self.assertIn("self.assertNotIn('run: npm'+' install", PREVIOUS)

 def test_rc281_guard_runs_early_without_mutating_dependencies(self):
  marker='python3 -m unittest tools.tests.test_rc274_ci_integrity tools.tests.test_rc280_npm_lock tools.tests.test_rc281_npm_guard -q'
  self.assertEqual(CI.count(marker),1)
  self.assertLess(CI.index(marker),CI.index('run: npm ci --ignore-scripts'))
  self.assertIn('python3 tools/verify_rc_cycle280_inventory.py --historical', CI)
  self.assertIn('python3 tools/verify_rc_cycle281_inventory.py', CI)

if __name__=='__main__': unittest.main()
