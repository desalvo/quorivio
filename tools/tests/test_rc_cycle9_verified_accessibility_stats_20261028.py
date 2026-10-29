"""Conservative audit of three distinct previously-green bounded RC subgates.

GitHub remote evidence is historical and must not imply this uncommitted batch
was verified, nor may one system test be counted twice under different scopes.
"""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight

class Cycle9Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text(encoding='utf-8'))
        cls.g={x['id']:x for x in cls.d['gates']}
    def test_weight_conservation_and_proven_scope(self):
        self.assertGreaterEqual(len(self.g),36)
        self.assertEqual(sum(v['weight'] for v in self.g.values()),100)
        self.assertGreaterEqual(audit()['score'],71.0)
        self.assertGreaterEqual(preflight()['accepted_gates'],19)
        self.assertEqual(len(audit()['unaccepted']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        for parent,child,parent_weight in [('A2','A2-ORDER',4),('A4','A4-FOCUS',4),('B3','B3-QUESTION-STATS',2)]:
            with self.subTest(parent=parent):
                a,b=self.g[parent],self.g[child]
                self.assertEqual((a['status'],a['weight']),('partial',parent_weight))
                self.assertEqual((b['status'],b['weight']),('accepted',2))
                self.assertEqual(b['verified_run_id'],40717525524)
                self.assertEqual(b['verified_job_id'],123073117101)
                self.assertEqual(b['verified_commit_sha'],'f6738592c648bc620e01b92d2bbaa6b90b459287')
                self.assertIn('40717525524',b['evidence'])
                self.assertTrue(a['remaining'])
                self.assertNotIn('independently approved',b['scope'].lower())
        self.assertEqual(self.g['A3-AUTO']['weight'],2)
        self.assertEqual(self.g['B3-AUDIENCE']['weight'],2)

    def test_historical_and_new_scores_are_independently_recorded(self):
        receipt=self.d['scoring_reconciliation_20261028_cycle9']
        self.assertEqual((receipt['baseline_score'],receipt['reconciled_score'],receipt['delta_pp']),(68,71,3))
        self.assertEqual(self.d['scoring_reconciliation_20261028_cycle8']['new_score'],68)
        self.assertEqual(set(receipt['accepted_subgates']),{'A2-ORDER','A4-FOCUS','B3-QUESTION-STATS'})
        self.assertFalse(receipt['strict_rc_ready'])
        self.assertEqual(self.d['last_verified_full_ci']['run_id'],40717525524)
        self.assertFalse(self.d['pending_local_batch']['new_feature_promoted'])
        self.assertTrue(self.d['pending_local_batch']['new_ci_required'])

    def test_fresh_recovery_ui_is_not_promoted_by_prior_run(self):
        web=(ROOT/'apps/web/src/main.tsx').read_text()
        browser=(ROOT/'tools/ci_recovery_url_chromium.py').read_text()
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('resetPasswordConfirmation',web)
        self.assertIn('resetSubmitLock.current',web)
        self.assertIn('resetSubmitPending||!resetToken',web)
        self.assertIn('resetPassword!==resetPasswordConfirmation',web)
        self.assertIn('double submit must be deduplicated',browser)
        self.assertIn('python3 tools/ci_recovery_url_chromium.py',workflow)
        self.assertEqual(self.g['C1']['status'],'partial')
        self.assertEqual(self.g['C1-RECOVERY']['verified_run_id'],40717525524)

    def test_human_acceptance_remains_explicit(self):
        for parent in ['A1','A2','A3','A4','B1','B2','B3','B4','C1','C2','C3','C4','D2','D3','D4','D5','D6']:
            self.assertEqual(self.g[parent]['status'],'partial')
        self.assertIn('Firefox/WebKit',self.g['A2']['remaining'])
        self.assertIn('screen-reader',self.g['A4']['remaining'])
        self.assertIn('external',self.g['C3']['remaining'].lower())
        self.assertFalse(preflight()['release_candidate_ready'])

if __name__=='__main__':unittest.main()
