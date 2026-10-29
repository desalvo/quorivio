"""Evidence-specific recovery gate regression: never credit local-only browser UI."""
from pathlib import Path
import json
import unittest
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight

class ProvenRecoveryGate(unittest.TestCase):
 def test_score_is_only_verified_remote_recovery(self):
  ledger=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  gates={g['id']:g for g in ledger['gates']}
  self.assertEqual((gates['C1']['weight'],gates['C1']['status']),(2,'partial'))
  self.assertEqual((gates['C1-AUTH']['weight'],gates['C1-AUTH']['status']),(2,'accepted'))
  recovery=gates['C1-RECOVERY']
  self.assertEqual((recovery['weight'],recovery['status']),(2,'accepted'))
  self.assertEqual(recovery['verified_run_id'],40717525524)
  self.assertEqual(recovery['verified_commit_sha'],'f6738592c648bc620e01b92d2bbaa6b90b459287')
  self.assertIn('TLS SMTP',recovery['evidence'])
  self.assertIn('browser',gates['C1']['remaining'].lower())
  self.assertEqual(ledger['scoring_reconciliation_20261028_cycle7']['new_score'],67)
  self.assertEqual(ledger['scoring_reconciliation_20261028_cycle8']['new_score'],68)
  self.assertEqual(sum(g['weight'] for g in ledger['gates']),100)
  self.assertEqual(ledger['scoring_reconciliation_20261028_cycle8']['new_score'],68)
  self.assertGreaterEqual(audit()['score'],68)
  self.assertEqual(preflight()['score'],audit()['score'])
  self.assertFalse(preflight()['release_candidate_ready'])
 def test_new_browser_fixture_requires_next_real_ci(self):
  doc=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  self.assertTrue(doc['pending_local_batch']['new_ci_required'])
  self.assertFalse(doc['pending_local_batch']['new_feature_promoted'])
  self.assertEqual(doc['pending_local_batch']['gates_promoted'],doc['scoring_reconciliation_20261029_cycle14']['new_accepted_gates'])  # no recovery UI promotion
  code=(ROOT/'apps/web/src/password-recovery-url.ts').read_text()
  self.assertIn('history.replaceState',code)
  self.assertNotIn('localStorage',code)
  self.assertIn('content="no-referrer"',(ROOT/'apps/web/index.html').read_text())
  ci=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('python3 tools/ci_recovery_url_chromium.py',ci)
  self.assertIn('python3 tools/ci_password_recovery_postgres.py',ci)
  self.assertIn('tools/ci_recovery_url_chromium.py',json.dumps(doc['rc_recovery_url_hygiene_local_cycle_20261028']))
if __name__=='__main__':unittest.main()
