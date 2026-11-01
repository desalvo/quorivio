"""Security regression for bounded account-auth RC credit and pending full recovery E2E."""
from pathlib import Path
import json
import os
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import ci_password_recovery_postgres as recovery
from rc_release_preflight import preflight
from rc_gate_audit import audit

class RecoveryAcceptance(unittest.TestCase):
 def test_ci_executes_disposable_recovery_on_real_postgresql_and_smtps(self):
  ci=(ROOT/'.github/workflows/ci.yml').read_text()
  source=(ROOT/'tools/ci_password_recovery_postgres.py').read_text()
  self.assertIn('run: python3 tools/ci_password_recovery_postgres.py',ci)
  self.assertIn('QUORIVIO_CI_RECOVERY_TEST:',ci)
  for part in ('password-reset/request','password-reset/confirm','password_reset_tokens',
               'used_at IS NOT NULL','ThreadPoolExecutor','smtp','multi-session revocation',
               'email_mfa_enrollments', 'email_mfa_challenges'):
   self.assertIn(part.lower(),source.lower())
  self.assertNotIn('print(token)',source)
 def test_real_test_never_runs_unintentionally_or_against_public_host(self):
  defaults={'QUORIVIO_CI_RECOVERY_TEST':'1','GITHUB_RUN_ID':'40638652838',
            'DATABASE_URL':'postgres://user:pass@127.0.0.1/db',
            'QUORIVIO_CI_NEW_PASSWORD':'safely-placeholder',
            'QUORIVIO_CI_ADMIN_EMAIL':'admin@example.invalid',
            'QUORIVIO_CI_LOAD_TOKEN':'t'*64}
  with patch.dict(os.environ,defaults,clear=True):
   with patch.object(recovery,'BASE','https://example.com:443'):
    with self.assertRaises(AssertionError):recovery.assert_disposable()
   with patch.object(recovery,'BASE','http://127.0.0.1:8080'):
    with self.assertRaises(AssertionError):recovery.assert_disposable()
 def test_all_credential_rotation_paths_invalidate_pending_mfa_atomically(self):
  server=(ROOT/'apps/api/src/server.ts').read_text()
  reset=server.split("app.post('/api/auth/password-reset/confirm'")[1].split("// OIDC authorization")[0]
  change=server.split("app.post('/api/auth/change-password'")[1].split("app.post('/api/auth")[0]
  for block in (reset, change):
   self.assertIn("DELETE FROM email_mfa_challenges WHERE user_id=$1",block)
   self.assertIn("DELETE FROM email_mfa_enrollments WHERE user_id=$1",block)
   self.assertIn("await cx.query('COMMIT')" if block is change else "await client.query('COMMIT')", block)
 def test_only_previously_green_auth_subgate_is_credited(self):
  doc=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  gates={g['id']:g for g in doc['gates']}
  self.assertEqual(gates['C1']['status'],'partial')
  self.assertGreaterEqual(gates['C1']['weight'],1)  # preserve residual independent acceptance
  auth=gates['C1-AUTH']
  self.assertEqual((auth['status'],auth['weight'],auth['verified_run_id']),('accepted',2,40638652838))
  self.assertEqual(sum(g['weight'] for g in gates.values()),100)
  self.assertIn('Browser-mediated account recovery',gates['C1']['remaining'])
  self.assertGreaterEqual(audit()['score'],68.0)
  rc=preflight()
  self.assertGreaterEqual(rc['score'],68.0)
  self.assertGreaterEqual(rc['gate_count'],33)
  self.assertGreaterEqual(rc['accepted_gates'],16)
  self.assertFalse(rc['release_candidate_ready'])
  self.assertTrue(doc['pending_local_batch']['new_ci_required'])
  self.assertFalse(doc['pending_local_batch']['new_feature_promoted'])

if __name__=='__main__':unittest.main()
