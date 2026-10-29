"""RC cycle 14: independent native browser engine evidence is bounded and traceable."""
import json
import unittest
from pathlib import Path
from rc_gate_audit import audit
from rc_release_preflight import preflight

ROOT = Path(__file__).resolve().parents[2]
SHA = 'cf49c3e1d3e58d4ec4d65862a92b742348a11435'
RUN = 40847463104
JOB = 123360950163

class Cycle14VerifiedNativeEngines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text(encoding='utf8'))
        cls.gates={g['id']:g for g in cls.matrix['gates']}
    def test_bounded_native_evidence_distinct_from_chromium(self):
        for name, parent in [('A3-NATIVE-STAGE','A3'),('A4-NATIVE-MODAL','A4')]:
            with self.subTest(name=name):
                g=self.gates[name]
                self.assertEqual((g['status'],g['weight']),('accepted',1))
                self.assertEqual((g['verified_run_id'],g['verified_job_id'],g['verified_commit_sha']),(RUN,JOB,SHA))
                self.assertIn('Firefox',g['evidence'])
                self.assertIn('WebKit',g['evidence'])
                self.assertEqual(self.gates[parent]['status'],'partial')
                self.assertIn('independent',self.gates[parent]['remaining'].lower())
        self.assertNotEqual(self.gates['A3-NATIVE-STAGE']['verified_run_id'],self.gates['A3-GEOMETRY']['verified_run_id'])
        self.assertNotEqual(self.gates['A4-NATIVE-MODAL']['verified_run_id'],self.gates['A4-FOCUS']['verified_run_id'])
    def test_score_weights_and_unaccepted_gates(self):
        self.assertGreaterEqual(len(self.gates),42)
        self.assertEqual(sum(g['weight'] for g in self.gates.values()),100)
        self.assertGreaterEqual(audit()['score'],75.0)  # cycle14 historical score remains in receipt
        self.assertGreaterEqual(preflight()['accepted_gates'],25)
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        summary=self.matrix['scoring_reconciliation_20261029_cycle14']
        self.assertEqual((summary['baseline_score'],summary['reconciled_score'],summary['delta_pp']),(74,75,1))
        self.assertFalse(summary['independent_testing_complete'])
    def test_native_job_tests_real_built_react_with_no_fallback(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        script=(ROOT/'tools/ci_rehearsal_singleton_offline_chromium.py').read_text()
        self.assertIn('python3 tools/ci_cross_browser_rc.py --engines firefox webkit',workflow)
        self.assertIn('python3 tools/ci_rehearsal_singleton_offline_chromium.py --engines firefox webkit',workflow)
        self.assertIn("getattr(p,engine).launch(**options)",script)
        self.assertIn('await expect(dashboard_overlay).to_have_count(1)',script)
        self.assertIn("await expect(dlg.locator('.rehearsal-pane')).to_have_count(2)",script)
        self.assertIn('python3 tools/verify_rc_cycle14_inventory.py',workflow)

if __name__=='__main__': unittest.main()
