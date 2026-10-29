"""GitHub-verified cycle 16 gate scopes and unverified reconnect regression.

These tests preserve the historical 75% receipt, keep 17 independent gates
partial, and require a new CI for source changes not covered by prior runs.
"""
import json
import unittest
from pathlib import Path
from rc_gate_audit import audit
from rc_release_preflight import preflight

ROOT=Path(__file__).resolve().parents[2]
RUN=40855898307
SHA='244945b1c79c5a7b20e8f743bd5646e041bade00'

class Cycle16VerifiedIntegration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text(encoding='utf8'))
  cls.gates={g['id']:g for g in cls.data['gates']}

 def test_three_verified_scopes_are_mutually_exclusive(self):
  bounded={
   'A1-NATIVE-REACT-ENTRY':('A1',2,123389289779,['dashboard','editor','Firefox','WebKit']),
   'A4-NATIVE-REACT-FOCUS':('A4',1,123389289779,['inert','focus','Firefox','WebKit']),
   'C1-RECOVERY-UI':('C1',1,123386671138,['React','Chromium','recovery']),
  }
  for subgate,(parent,weight,job,keywords) in bounded.items():
   with self.subTest(gate=subgate):
    gate=self.gates[subgate]
    self.assertEqual((gate['status'],gate['weight']),('accepted',weight))
    self.assertEqual((gate['verified_run_id'],gate['verified_job_id'],gate['verified_commit_sha']),(RUN,job,SHA))
    for keyword in keywords:self.assertIn(keyword,gate['evidence']+' '+gate['scope'])
    self.assertEqual(self.gates[parent]['status'],'partial')
    self.assertGreaterEqual(self.gates[parent]['weight'],1)
  self.assertIn('PostgreSQL',self.gates['C1-RECOVERY']['evidence'])
  self.assertNotEqual(self.gates['C1-RECOVERY-UI']['verified_run_id'],self.gates['C1-RECOVERY']['verified_run_id'])
  self.assertNotEqual(self.gates['A4-NATIVE-REACT-FOCUS']['verified_run_id'],self.gates['A4-NATIVE-MODAL']['verified_run_id'])

 def test_score_is_based_on_remote_success_not_local_new_checks(self):
  self.assertEqual(len(self.gates),45)
  self.assertEqual(sum(g['weight'] for g in self.gates.values()),100)
  self.assertEqual(audit()['score'],77)
  self.assertEqual(preflight()['accepted_gates'],28)
  self.assertEqual(len(preflight()['unaccepted_gates']),17)
  self.assertFalse(preflight()['release_candidate_ready'])
  previous=self.data['scoring_reconciliation_20261029_cycle14']
  self.assertEqual(previous['reconciled_score'],75)
  current=self.data['scoring_reconciliation_20261029_cycle16']
  self.assertEqual((current['baseline_score'],current['reconciled_score'],current['delta_pp']),(75,77,2))
  self.assertTrue(self.data['pending_local_batch']['new_ci_required'])
  self.assertFalse(self.data['pending_local_batch']['new_feature_promoted'])
  self.assertFalse(current['independent_testing_complete'])

 def test_new_replica_reconnect_is_real_and_fail_closed(self):
  code=(ROOT/'tools/ci_live_replicas.py').read_text(encoding='utf8')
  workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
  for fragment in ('await participant_ws.close()', 'visitor.ws_connect(ws_url(B, sid)',
    'disconnected A -> reconnected B participant snapshot','already_submitted',
    'reconnect leaked presenter results','reconnect leaked presence',
    'A -> B activity close after reconnect', 'session close after reconnect'):
   self.assertIn(fragment,code)
  self.assertIn('python3 tools/ci_live_replicas.py',workflow)
  self.assertNotIn('new_reconnect_result_verified',current:=self.data['scoring_reconciliation_20261029_cycle16'])

 def test_react_focus_probe_is_real_browser_and_native_ci(self):
  code=(ROOT/'tools/ci_rehearsal_singleton_offline_chromium.py').read_text(encoding='utf8')
  workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
  self.assertIn("e.id='ci-external-focus'",code)
  self.assertIn('dlg?.contains(document.activeElement)',code)
  self.assertIn('external programmatic focus escaped the React modal',code)
  self.assertIn("node=>node.inert",code)
  self.assertIn('python3 tools/ci_rehearsal_singleton_offline_chromium.py --engines firefox webkit',workflow)
  self.assertIn('python3 tools/ci_rehearsal_singleton_offline_chromium.py',workflow)

if __name__=='__main__': unittest.main()
