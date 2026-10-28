"""Consistent receipt of the first green Full CI for the multi-widget hotfix."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RUN=40595463258
SHA="e2dc3a97bd15d82a50c23a98b1fb83c2bd1841c9"
class FullCiEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt=json.loads((ROOT/'docs/validation/RC_FULL_CI_GREEN_40595463258.json').read_text())
        cls.matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
    def test_receipt_run_sha_and_success(self):
        self.assertEqual(self.receipt['head_sha'],SHA)
        self.assertEqual(self.receipt['run_id'],RUN)
        self.assertEqual(self.receipt['run_conclusion'],'success')
        self.assertTrue(all(x=='success' for x in self.receipt['observed_jobs'].values()))
    def test_publication_is_not_misclassified_as_build_only(self):
        pub=self.receipt['image_publication']
        self.assertEqual(pub['job'],'success')
        self.assertIn('latest',pub['tags'])
        self.assertIn('sha-e2dc3a97bd15',pub['tags'])
        self.assertIn('sha256:',pub['digest'])
    def test_strict_rc_not_claimed_complete(self):
        self.assertIn('skipped',self.receipt['strict_rc_gate'])
        self.assertFalse(self.receipt['rc_gate_state']['ready'])
        self.assertEqual(len(self.matrix['gates']),18)
        self.assertEqual(sum(g['weight'] for g in self.matrix['gates']),100)
        self.assertEqual(sum(g['weight']*(1 if g['status']=='accepted' else 0.5 if g['status']=='partial' else 0) for g in self.matrix['gates']),53.0)
    def test_open_gates_do_not_claim_release_readiness(self):
        self.assertEqual(sum(g['status']=='accepted' for g in self.matrix['gates']),1)
        self.assertEqual(sum(g['status']=='partial' for g in self.matrix['gates']),17)
        for g in self.matrix['gates']:
            self.assertTrue(g['remaining'].strip())
            self.assertNotIn('40592859476 successor',g['remaining'])
    def test_bilingual_status_mentions_verified_run(self):
        for path in ['DEVELOPMENT_STATUS.md','DEVELOPMENT_STATUS.it.md']:
            txt=(ROOT/'docs'/path).read_text()
            self.assertIn(str(RUN),txt[:3800])
            self.assertIn(SHA,txt[:3800])
if __name__=='__main__':unittest.main()
