"""Cycle 58: checked GitHub acceptance receipt and bounded session DB refresh contract."""
from __future__ import annotations
import json
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight

class RC58VerifiedAcceptance(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  cls.gates={gate['id']:gate for gate in cls.matrix['gates']}
  cls.receipt=json.loads((ROOT/'docs/validation/RC_CYCLE58_GITHUB_VERIFIED_20261031.json').read_text())
  cls.refresh=(ROOT/'apps/api/src/live-periodic-refresh.ts').read_text()
  cls.server=(ROOT/'apps/api/src/server.ts').read_text()

 def test_two_new_gates_are_accepted_with_distinct_scopes_and_one_provenance(self):
  ids=['B1-IDLE-TWO-REPLICA','B4-500-GLOBAL-SLO']
  self.assertEqual(self.matrix['last_maintainer_confirmed_commit'],'c0fe7f7b9e41c0295387d84996a7b531b91b69a0')
  self.assertEqual(len(self.matrix['gates']),55)
  for gid in ids:
   sub=self.gates[gid]
   self.assertEqual((sub['status'],sub['weight']),('accepted',0.5))
   self.assertEqual((sub['verified_run_id'],sub['verified_job_id']),(41152939003,124393360139))
   self.assertEqual(sub['verified_commit_sha'],self.receipt['committed_sha'])
   self.assertIn('PASS ',sub['evidence'])
  self.assertEqual(self.gates['B1']['weight'],0.5)
  self.assertEqual(self.gates['B4']['weight'],0.5)
  self.assertEqual(self.gates['B1']['status'],'partial')
  self.assertEqual(self.gates['B4']['status'],'partial')
  self.assertNotEqual(self.gates[ids[0]]['scope'],self.gates[ids[1]]['scope'])

 def test_percent_81_75_is_derived_not_marketing(self):
  a=audit();p=preflight()
  self.assertEqual((a['score'],p['score']), (81.75,81.75))
  self.assertEqual((p['gate_count'],p['accepted_gates'],len(p['unaccepted_gates'])),(55,38,17))
  self.assertFalse(p['release_candidate_ready'])
  self.assertEqual(self.receipt['calculation']['after']-self.receipt['calculation']['before'],0.5)
  self.assertEqual(self.receipt['calculation']['gate_weight_total'],100)
  self.assertEqual(self.matrix['rc_cycle58_verified_reconciliation_20261031']['new_score'],81.75)

 def test_explicit_unvalidated_limits_remain(self):
  self.assertTrue(self.receipt['source_ci_success'])
  self.assertEqual(self.receipt['source_job_id'],124393360139)
  self.assertIn('kubernetes_tls_test=false', ' '.join(self.receipt['scope_limits']))
  self.assertIn('not executed',self.matrix['rc_cycle58_verified_reconciliation_20261031']['kubernetes_tls'])
  self.assertTrue(any('RWX' in s for s in self.receipt['scope_limits']))

 def test_bounded_refresh_is_used_in_production_and_not_one_per_socket(self):
  for token in ['MAX_LIVE_REFRESH_CONCURRENCY = 32','DEFAULT_LIVE_REFRESH_CONCURRENCY = 8',
                'Math.min(maxConcurrent, ids.length)','if (running) return;',
                'options.isSessionActive','inFlight.delete(sessionId)']:
   self.assertIn(token,self.refresh)
  self.assertIn('maxConcurrent:8',self.server)
  self.assertIn('isSessionActive:sid=>!!sockets.get(sid)?.size',self.server)
  self.assertIn('activeSessions:()=>sockets.keys()',self.server)
  self.assertIn('readAndSend:broadcastLocal',self.server)
  self.assertNotIn('pg_notify',self.refresh)
  self.assertIn('500 distinct active sessions', (ROOT/'apps/api/test/live-periodic-refresh-cycle58.test.ts').read_text())

 def test_status_handoff_records_new_git_baseline(self):
  for rel in ['DEVELOPMENT_STATUS.it.md','DEVELOPMENT_STATUS.md','COMPLETION_HANDOFF.it.md','COMPLETION_HANDOFF.md']:
   s=(ROOT/'docs'/rel).read_text()[:1700]
   for t in ('81.75' if not rel.endswith('.it.md') else '81,75', '41152939003', 'c0fe7f7b9e41c0295387d84996a7b531b91b69a0','rc_strict=false'):
    self.assertIn(t,s)

if __name__=='__main__': unittest.main()
