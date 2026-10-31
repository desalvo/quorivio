"""Cycle24 evidence-scoped runtime deployment gate without premature credit."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_cycle23_inventory import load_inventory as historical
from verify_rc_cycle62_inventory import load_inventory, verify_source

class RC24(unittest.TestCase):
    def test_historical_receipt_immutable_and_current_tree_exact(self):
        self.assertEqual(len(historical()),860)
        self.assertGreater(len(load_inventory()),len(historical()))
        self.assertEqual(verify_source(),len(load_inventory()))

    def test_unchanged_scoring_and_external_parent_gates(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        self.assertEqual(len(matrix['gates']),55)
        self.assertEqual(sum(g['weight'] for g in matrix['gates']),100)
        self.assertEqual((audit()['score'],preflight()['accepted_gates']),(81.75,38))
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertFalse(matrix['pending_local_batch']['kubernetes_kind_runtime_verified'])
        self.assertFalse(matrix['pending_local_batch']['new_feature_promoted'])
        self.assertTrue(matrix['pending_local_batch']['new_ci_required'])
        self.assertEqual(matrix['last_verified_full_ci']['head_sha'],
                         'c0fe7f7b9e41c0295387d84996a7b531b91b69a0')

    def test_ci_checks_historical_before_current_and_leak_detection(self):
        s=(ROOT/'.github/workflows/ci.yml').read_text()
        older='python3 tools/verify_rc_cycle23_inventory.py --historical'
        newer='python3 tools/verify_rc_cycle41_inventory.py'
        self.assertIn(older,s)
        self.assertIn(newer,s)
        self.assertLess(s.index(older),s.index(newer))
        self.assertLess(s.index(newer),s.index('Detect credential leaks'))
        self.assertIn("if: github.event_name == 'workflow_dispatch' && inputs.kubernetes_runtime_test",s)

    def test_report_and_operator_limits_are_explicit(self):
        report=json.loads((ROOT/'docs/validation/RC_CYCLE24_KIND_RUNTIME_LOCAL_20261029.json').read_text())
        self.assertEqual((report['score_before'],report['score_after']),(79,79))
        self.assertFalse(report['kubernetes_runtime_verified'])
        self.assertFalse(report['strict_rc_ready'])
        for lang in ('en','it'):
            text=(ROOT/f'docs/K8S_KIND_SINGLE_NODE_RUNTIME.{lang}.md').read_text()
            for word in ('KIND','PostgreSQL 18','ReadWriteMany','kubernetes_runtime_test=true','Podman'):
                self.assertIn(word,text)

if __name__=='__main__':unittest.main()
