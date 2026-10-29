"""Regression: distinct audited previously green subgates, local-only timer pending CI."""
import json
from pathlib import Path
import unittest
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
DOC=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())

class Cycle5GateAudit(unittest.TestCase):
 def test_bounded_historical_scanner_and_documentation_checks(self):
  gates={g['id']:g for g in DOC['gates']}
  self.assertGreaterEqual(len(gates),33)
  self.assertEqual(sum(x['weight'] for x in gates.values()),100)
  for parent,sub in [('D4','D4-SCAN'),('D5','D5-TECHDOC')]:
   self.assertEqual(gates[parent]['status'],'partial')
   self.assertGreaterEqual(gates[parent]['weight'],2)  # later verified subgates may narrow the residual without closing external acceptance
   self.assertEqual((gates[sub]['status'],gates[sub]['weight']),('accepted',2))
   self.assertIn('40638652838',gates[sub]['evidence'])
   self.assertIn('a32ef78902a656262d346a0fa622604a4deda405',gates[sub]['evidence'])
  self.assertIn('pentest',gates['D4']['remaining'])
  self.assertIn('editorial',gates['D5']['remaining'])
  self.assertEqual(DOC['scoring_reconciliation_20261028_cycle5']['baseline_score'],63)
  self.assertGreaterEqual(audit()['score'],68)
 def test_no_pending_timer_credit_and_rc_not_ready(self):
  self.assertFalse(DOC['pending_local_batch']['new_feature_promoted'])
  self.assertTrue(DOC['pending_local_batch']['new_ci_required'])
  receipt=preflight()
  self.assertGreaterEqual(receipt['score'],68)
  self.assertGreaterEqual(receipt['accepted_gates'],16)
  self.assertGreaterEqual(receipt['gate_count'],33)
  self.assertFalse(receipt['release_candidate_ready'])
 def test_real_bilingual_docs_present_but_unreviewed(self):
  for language in ('it','en'):
   self.assertTrue((ROOT/f'README{".it" if language=="it" else ""}.md').is_file())
   for guide in ('admin-guide','user-guide'):
    file=ROOT/'docs/manuals'/f'{guide}.{language}.pdf'
    self.assertGreater(file.stat().st_size,1000)
if __name__=='__main__':unittest.main()
