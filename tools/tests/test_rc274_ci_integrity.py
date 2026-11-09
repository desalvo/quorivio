"""RC274 regression: installed npm deps may not mutate release receipts.
Legacy pre-install tests must follow the deterministic install boundary.
"""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
SRC=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
ASSET=(ROOT/'tools/tests/test_asset_erasure_delivery.py').read_text(encoding='utf8')
class RC274CiIntegrity(unittest.TestCase):
 def test_npm_ci_does_not_rewrite_pinned_lock(self):
  self.assertGreaterEqual(CI.count('run: npm ci --ignore-scripts --no-audit --no-fund'),2)
  self.assertNotIn('run: npm install --ignore-scripts --no-audit --no-fund',CI)
  self.assertLess(CI.index('RC274 answer truth'),CI.index('run: npm ci --ignore-scripts'))
 def test_privacy_assertion_scoped_to_single_endpoint(self):
  route=SRC.split("app.get('/api/admin/privacy/erasure-status'",1)[1].split('});',1)[0]
  self.assertIn('requireAuth,requireAdmin',route)
  self.assertNotIn('SELECT *',route)
  self.assertIn("split(\"});\",1)[0]",ASSET)
 def test_historical_test_order_contracts_moved_without_relaxing_order(self):
  for path in (ROOT/'tools/tests').glob('*.py'):
   if path.name=='test_rc274_ci_integrity.py':continue
   source=path.read_text(encoding='utf8')
   self.assertNotIn('npm install --ignore-scripts',source,path.name)
  self.assertIn('python3 tools/verify_rc_cycle273_inventory.py --historical',CI)
  self.assertIn('python3 tools/verify_rc_cycle274_inventory.py',CI)
if __name__=='__main__':unittest.main()
