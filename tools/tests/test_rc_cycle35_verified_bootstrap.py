"""Independently-reviewed CI evidence and pool fail-closed contracts (cycle 35)."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight

class Cycle35VerifiedBootstrap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        cls.g={x['id']:x for x in cls.m['gates']}
        cls.proof=json.loads((ROOT/'docs/validation/RC_CYCLE35_GITHUB_VERIFIED_20261030.json').read_text())

    def test_github_receipt_identifies_two_separate_passes(self):
        p=self.proof
        self.assertEqual((p['source_run'],p['source_job']),(41048187760,124037870206))
        self.assertEqual(p['committed_sha'],'f5ccf9a7545e7c17b4323d067db66aff5eca9b41')
        self.assertEqual(len(p['source_job_pass_lines']),2)
        self.assertIn('simultaneous fresh-schema API bootstrap',p['source_job_pass_lines'][0])
        self.assertIn('rolling SIGTERM',p['source_job_pass_lines'][1])
        self.assertFalse(p['new_code_covered_by_source_job'])
        self.assertFalse(p['external_slo_verified'])

    def test_splits_preserve_weight_and_scope(self):
        self.assertEqual(self.g['B1']['weight'],0.5)
        for key in ('B1-BOOTSTRAP-PG18','B1-GRACEFUL-DRAIN'):
            sub=self.g[key]
            self.assertEqual((sub['weight'],sub['status']),(0.5,'accepted'))
            self.assertEqual((sub['verified_run_id'],sub['verified_job_id']),(41048187760,124037870206))
            self.assertTrue(any(word in sub['remaining'].lower() for word in ('production','slo')))
        self.assertEqual(sum(x['weight'] for x in self.m['gates']),100)
        self.assertEqual(self.g['B1']['status'],'partial')

    def test_percentage_only_counts_bounded_prior_ci_evidence(self):
        p=preflight()
        self.assertEqual((audit()['score'],p['score']),(81.75,81.75))
        self.assertEqual((p['gate_count'],p['accepted_gates'],len(p['unaccepted_gates'])),(55,38,17))
        self.assertFalse(p['release_candidate_ready'])
        self.assertEqual(self.proof['new_score']-self.proof['old_score'],0.5)
        self.assertEqual(self.m['rc_cycle35_verified_reconciliation_20261030']['score_after'],80.75)

    def test_distinct_from_existing_websocket_and_ingress_evidence(self):
        for k in ('B1-WS','B1-RECONNECT','B4-KIND-INGRESS-RECOVERY'):
            self.assertIn(k,self.g)
            self.assertEqual(self.g[k]['status'],'accepted')
            self.assertNotEqual(self.g[k]['scope'] if 'scope' in self.g[k] else self.g[k]['evidence'],self.g['B1-BOOTSTRAP-PG18']['scope'])

    def test_failed_lock_never_reuses_untidy_connection(self):
        source=(ROOT/'apps/api/src/bootstrap-lock.ts').read_text()
        tests=(ROOT/'apps/api/test/bootstrap-lock.test.ts').read_text()
        self.assertIn('if (!locked || !sessionReset) destroy = true',source)
        self.assertIn('client.release(destroy)',source)
        self.assertIn('session setup failure never returns an uncertain connection',tests)
        self.assertIn('false unlock acknowledgement destroys the connection',tests)
        self.assertIn('lock acquisition failure does not unlock',tests)

    def test_immutable_cycle34_receipt_retained(self):
        from verify_rc_cycle34_inventory import load_inventory
        self.assertGreaterEqual(len(load_inventory()),935)
        previous=json.loads((ROOT/'docs/validation/RC_CYCLE34_GITHUB_VERIFIED_20261030.json').read_text())
        self.assertEqual(previous['score_after'],80.25)
        self.assertEqual(previous['verified_run_id'],41048187760)

    def test_workflow_keeps_historical_and_current_integrity(self):
        wf=(ROOT/'.github/workflows/ci.yml').read_text()
        old=wf.index('python3 tools/verify_rc_cycle34_inventory.py --historical')
        current=wf.index('python3 tools/verify_rc_cycle41_inventory.py')
        self.assertLess(old,current)
        self.assertLess(current,wf.index('Detect credential leaks'))

    def test_documentation_records_remaining_risks(self):
        for fn in ('DEVELOPMENT_STATUS.md','DEVELOPMENT_STATUS.it.md','COMPLETION_HANDOFF.md','COMPLETION_HANDOFF.it.md'):
            body=(ROOT/'docs'/fn).read_text()[:4000]
            self.assertIn('81,75' if fn.endswith('.it.md') else '81.75',body)
            # The immutable 2026-10-30 cycle-35 receipt above proves its original
            # commit. Current status headers must instead report the latest CI
            # failure, its unaccepted gates and remaining validation constraints.
            self.assertIn('41123318359',body)
            self.assertIn('c0fe7f7b9e41c0295387d84996a7b531b91b69a0',body)
            self.assertIn('rc_strict=false',body)

if __name__=='__main__':unittest.main()
