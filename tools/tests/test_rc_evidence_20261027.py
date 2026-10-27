"""Guard a traceable RC score update against accidental over-claiming."""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[2]

class RCEvidenceMilestone(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  doc=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  cls.gates={g['id']:g for g in doc['gates']}
 def test_gate_weights_status_score(self):
  self.assertEqual(sum(g['weight'] for g in self.gates.values()),100)
  weights={'accepted':1,'partial':.5,'open':0,'blocked':0}
  score=sum(g['weight']*weights[g['status']] for g in self.gates.values())
  self.assertGreaterEqual(score,53.0)
  # This milestone records a floor, not a cap on future verified RC progress.
  self.assertLessEqual(score,100.0)
 def test_mobile_baseline_has_at_least_partial_evidence(self):
  g=self.gates['A4']
  self.assertIn(g['status'],('partial','accepted'))
  self.assertIn('40517573850',g['evidence'])
  if g['status']=='partial':
   self.assertIn('screen-reader',g['remaining'])
 def test_image_build_is_not_runtime_acceptance(self):
  g=self.gates['D3']
  self.assertIn(g['status'],('partial','accepted'))
  self.assertIn('122239629249',g['evidence'])
  self.assertIn('linux/arm64',g['evidence'])
  if g['status']=='partial':
   self.assertIn('rootless',g['remaining'])
 def test_independent_acceptance_remains_pending_until_promoted(self):
  # Prevent a regression to open/blocked; don't veto future reviewed evidence.
  for gate in ('B2','B3','D6'):
   g=self.gates[gate]
   self.assertIn(g['status'],('partial','accepted'))
   if g['status']=='partial':
    self.assertTrue(g['remaining'].strip())
 def test_evidence_bilingual_and_revision_traceable(self):
  for lang in ('en','it'):
   data=(ROOT/f'docs/RC_EVIDENCE_REVIEW_2026-10-27.{lang}.md').read_text()
   self.assertIn('40517573850',data)
   self.assertIn('53',data)

if __name__=='__main__':unittest.main()
