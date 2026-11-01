"""Acceptance is bounded to previously-green GitHub CI; fresh edits are local-only."""
import json
import unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight

class Cycle10Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        cls.gates={g['id']:g for g in cls.doc['gates']}

    def test_conservative_score_and_no_external_promotion(self):
        self.assertGreaterEqual(len(self.gates),40)
        self.assertEqual(sum(g['weight'] for g in self.gates.values()),100)
        self.assertGreaterEqual(audit()['score'],74.0)
        self.assertGreaterEqual(preflight()['accepted_gates'],23)
        self.assertEqual(len(audit()['unaccepted']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        for pid,cid,pw,cw in [('A1','A1-EDITOR-INTERACTION',4,2),('D3','D3-K8S-GENERATOR',1,1),('D4','D4-CONVERTER-BOUNDARY',2,1)]:
            with self.subTest(pid=pid):
                parent,child=self.gates[pid],self.gates[cid]
                # The cycle-10 original parent weight remains in its immutable
                # reconciliation receipt; later verified subgates may reduce
                # the CURRENT parent without invalidating the old test.
                self.assertEqual(parent['status'],'partial')
                self.assertGreaterEqual(parent['weight'],0.5)
                self.assertLessEqual(parent['weight'],pw)
                self.assertEqual((child['status'],child['weight']),('accepted',cw))
                self.assertEqual(child['verified_run_id'],40717525524)
                self.assertEqual(child['verified_job_id'],123073117101)
                self.assertEqual(child['verified_commit_sha'],'f6738592c648bc620e01b92d2bbaa6b90b459287')
                self.assertIn('40717525524',child['evidence'])
                self.assertTrue(parent['remaining'])
        self.assertEqual((self.gates['A3-GEOMETRY']['status'],self.gates['A3-GEOMETRY']['weight']),('accepted',2))
        for pid in ['A2','A4','B1','B2','B3','B4','C1','C2','C3','C4','D2','D5','D6']:
            self.assertEqual(self.gates[pid]['status'],'partial')

    def test_evidence_unique_and_new_code_is_uncredited(self):
        r=self.doc['scoring_reconciliation_20261029_cycle10']
        self.assertEqual((r['baseline_score'],r['reconciled_score'],r['delta_pp']),(71,74,3))
        self.assertEqual(len(r['non_duplicate_scope']),4)
        self.assertEqual(len(set(r['accepted_subgates'])),4)
        self.assertTrue(r['new_code_github_pending'])
        ledger=self.doc['pending_local_batch']
        self.assertTrue(ledger['new_ci_required'])
        self.assertFalse(ledger['new_feature_promoted'])
        self.assertFalse(ledger['strict_rc_ready'])
        self.assertEqual(self.doc['scoring_reconciliation_20261028_cycle9']['reconciled_score'],71)
        self.assertEqual(self.gates['A3-GEOMETRY']['verified_run_id'],40717525524)  # cycle-10 receipt remains immutable

    def test_real_accessibility_improvements_are_in_ci(self):
        web=(ROOT/'apps/web/src/main.tsx').read_text()
        dom=(ROOT/'apps/web/src/rehearsal-dialog.ts').read_text()
        browser=(ROOT/'tools/ci_recovery_url_chromium.py').read_text()
        portals=(ROOT/'tools/ci_rc_rehearsal_dynamic_portals_chromium.py').read_text()
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('aria-labelledby="reset-password-title"',web)
        self.assertIn('onSubmit={e=>{e.preventDefault();void confirmPasswordRecovery()}}',web)
        self.assertIn('type="submit"',web)
        self.assertIn(".press('Enter')",browser)
        self.assertIn('modal.contains(node)',dom)
        self.assertIn('background.delete(node)',dom)
        self.assertIn("appendChild(document.querySelector('#late-portal'))",portals)
        for b in ['ci_recovery_url_chromium.py','ci_rc_rehearsal_dynamic_portals_chromium.py']:
            self.assertIn(b,ci)

if __name__=='__main__':unittest.main()
