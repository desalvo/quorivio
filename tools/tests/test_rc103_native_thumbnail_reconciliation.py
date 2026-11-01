"""RC103: independently evidenced A2 native DnD accounting without false RC promotion."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight

class NativeThumbnailAccountingRC103(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        cls.receipt=json.loads((ROOT/'docs/validation/RC_CYCLE103_NATIVE_THUMBNAIL_RECONCILIATION_20261101.json').read_text())
        cls.gates={x['id']:x for x in cls.matrix['gates']}

    def test_verified_github_source_and_exact_scope(self):
        receipt=self.receipt
        self.assertEqual(receipt['source']['run_id'],41265300884)
        self.assertEqual(receipt['source']['head_sha'], 'b3d753e06f6eca2bf771bae7699c65f9370ed399')
        self.assertEqual((receipt['source']['campaign_required_jobs_passed'],receipt['source']['campaign_required_jobs_total']),(11,11))
        self.assertEqual(receipt['source']['publication_jobs'],'skipped')
        self.assertEqual(len(receipt['bounded_evidence']['firefox_webkit']['logged_pass_records']),4)
        for engine in ('firefox','webkit'):
            for width in (1440,390):
                self.assertTrue(any(f'{engine} {width}px' in line for line in receipt['bounded_evidence']['firefox_webkit']['logged_pass_records']))

    def test_gate_weight_partition_and_no_double_credit(self):
        a2=self.gates['A2']; bounded=self.gates['A2-NATIVE-DND']
        self.assertEqual((a2['weight'],a2['status']),(2,'partial'))
        self.assertEqual((bounded['weight'],bounded['status']),(1,'accepted'))
        self.assertEqual(bounded['verified_run_id'],self.receipt['source']['run_id'])
        self.assertEqual(set(bounded['verified_job_ids']),{124726769311,124728693190})
        self.assertIn('Actual browser drag events'.lower(), self.receipt['bounded_evidence']['fixture_limit'].lower())
        for previous in ('A2-ORDER','A2-PAGE-JSON'):
            self.assertEqual(self.gates[previous]['status'],'accepted')
            self.assertNotEqual(self.gates[previous]['scope'],bounded['scope'])
        self.assertIn('physical',a2['remaining'])
        self.assertIn('pixel-accurate',a2['remaining'])
        self.assertEqual(sum(g['weight'] for g in self.matrix['gates']),100)

    def test_progress_only_from_verified_github_and_not_local_pptx(self):
        expected=self.receipt['accounting']
        self.assertEqual((expected['before'], expected['after'],expected['delta']),(84.75,85.25,0.5))
        self.assertEqual((audit()['score'],preflight()['score']),(85.25,85.25))
        self.assertEqual((preflight()['gate_count'],preflight()['accepted_gates'],len(preflight()['unaccepted_gates'])),(60,43,17))
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertTrue(self.receipt['local_cycle_103']['requires_new_ci'])
        self.assertFalse(self.receipt['local_cycle_103']['docker_publication'])

    def test_ci_preserves_three_native_browser_engines(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        source=(ROOT/'tools/ci_page_thumbnail_native.py').read_text()
        self.assertIn('python3 tools/ci_page_thumbnail_native.py --engines chromium',workflow)
        self.assertIn('python3 tools/ci_page_thumbnail_native.py --engines firefox webkit',workflow)
        for text in ('await rows.nth(0).drag_to','await rows.nth(1).locator','commitThenLose','rejectNext'):
            self.assertIn(text,source)

if __name__=='__main__':unittest.main()
