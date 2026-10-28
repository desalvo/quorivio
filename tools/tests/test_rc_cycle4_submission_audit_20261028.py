"""Source-backed historical gate evidence and uncommitted submission semantics."""
from pathlib import Path
import json,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_release_preflight import preflight
LEDGER=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
class Cycle4(unittest.TestCase):
 def test_two_accepted_subgates_have_same_verified_github_commit(self):
  gates={x['id']:x for x in LEDGER['gates']}
  for id,parent in [('B3-AUDIENCE','B3'),('D6-ERASURE','D6')]:
   self.assertEqual(gates[id]['status'],'accepted')
   self.assertEqual(gates[id]['weight'],2)
   self.assertEqual(gates[id]['verified_run_id'],40638652838)
   self.assertEqual(gates[id]['verified_commit_sha'],'a32ef78902a656262d346a0fa622604a4deda405')
   self.assertEqual(gates[parent]['status'],'partial')
   self.assertTrue(gates[parent]['remaining'])
  self.assertEqual(gates['B3']['weight'],4)
  self.assertEqual(gates['D6']['weight'],3)
 def test_new_features_are_not_mistaken_for_ci_evidence(self):
  self.assertFalse(LEDGER['pending_local_batch']['new_feature_promoted'])
  self.assertTrue(LEDGER['pending_local_batch']['new_ci_required'])
  self.assertEqual(preflight()['score'],LEDGER['scoring_reconciliation_20261028_cycle7']['new_score'])
  self.assertFalse(preflight()['release_candidate_ready'])
  self.assertEqual(preflight()['accepted_gates'],15)
  self.assertEqual(preflight()['gate_count'],32)
 def test_total_weights_conserved(self):
  self.assertEqual(sum(x['weight'] for x in LEDGER['gates']),100)
  history=LEDGER['scoring_reconciliation_20261028_cycle4']
  self.assertEqual(history['new_score']-history['baseline_score'],2)
if __name__=='__main__':unittest.main()
