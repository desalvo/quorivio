"""Bounded, CI-evidenced engineering acceptance never silently approves the full RC."""
import json, unittest
from pathlib import Path
from sys import path
ROOT=Path(__file__).resolve().parents[2];path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
class VerifiedSubgateTests(unittest.TestCase):
 def test_reconciled_weights_and_score_are_derivable(self):
  d=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text());g={x['id']:x for x in d['gates']}
  self.assertEqual(sum(x['weight'] for x in g.values()),100)
  self.assertEqual(audit()['score'],d['scoring_reconciliation_20261028_cycle7']['new_score'])
  self.assertEqual(d['scoring_reconciliation_20261028_cycle2']['new_score'],60)
  self.assertEqual(len(g),32)
  for source,child in [('A3','A3-AUTO'),('B2','B2-DB'),('B4','B4-LOAD')]:
   self.assertEqual(g[child]['weight'],2)
   self.assertEqual(g[child]['status'],'accepted')
   self.assertEqual(g[source]['status'],'partial')
   self.assertEqual(g[child]['verified_run_id'],40638652838)
   self.assertTrue(g[source]['remaining'])
  for source,child,run in [('B1','B1-WS',40638652838),('C2','C2-TLS',40638652838),('D2','D2-DR',40638652838),('D3','D3-IMAGE',40595463258)]:
   self.assertEqual(g[child]['weight'],2)
   self.assertEqual(g[child]['status'],'accepted')
   self.assertEqual(g[child]['verified_run_id'],run)
   self.assertEqual(g[source]['status'],'partial')
   self.assertTrue(g[source]['remaining'])
  self.assertEqual(g['C4-PROFILE']['status'],'accepted')
  self.assertEqual(g['C4']['status'],'partial')
  self.assertEqual(g['C4-PROFILE']['verified_run_id'],40638652838)
 def test_independent_release_checks_remain_blocking(self):
  result=preflight()
  self.assertFalse(result['release_candidate_ready'])
  self.assertEqual(result['score'],67)
  self.assertEqual(result['accepted_gates'],15)
  self.assertEqual(result['gate_count'],32)
 def test_receipt_is_not_evidence_for_uncommitted_topic_results(self):
  d=json.loads((ROOT/'docs/validation/RC_FULL_CI_40638652838_EVIDENCE_REVIEW.json').read_text())
  self.assertEqual(d['user_confirmed_sha'],'a32ef78902a656262d346a0fa622604a4deda405')
  self.assertEqual(d['observed_jobs']['Production publication'],'skipped')
  self.assertIn('AFTER run',' '.join(d['limitations']))
if __name__=='__main__':unittest.main()
