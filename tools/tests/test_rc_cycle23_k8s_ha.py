"""Cycle23: keep verified RC scoring distinct from new unverified deployment improvements."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_cycle22_inventory import load_inventory as previous
from verify_rc_cycle23_inventory import load_inventory
from verify_rc_cycle57_inventory import load_inventory as current_inventory, verify_source

class Cycle23RC(unittest.TestCase):
    def test_frozen_historical_catalog_and_current_tree(self):
        self.assertEqual(len(previous()),851)
        self.assertGreater(len(load_inventory()),len(previous()))
        self.assertEqual(verify_source(),len(current_inventory()))

    def test_unchanged_evidence_weight_and_pending_external_gates(self):
        m=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        self.assertEqual(len(m['gates']),53)
        self.assertEqual(sum(x['weight'] for x in m['gates']),100)
        self.assertEqual((audit()['score'],preflight()['accepted_gates']),(81.25,36))
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertEqual(m['last_verified_full_ci']['head_sha'],'caf6331f15ccf39c218791503b8c6d0ca3503dce')
        p=m['pending_local_batch']
        self.assertFalse(p['new_feature_promoted'])
        self.assertTrue(p['new_ci_required'])
        self.assertFalse(p['kubernetes_kind_api_smoke_verified'])
        self.assertFalse(p['graceful_shutdown_postgres_e2e_verified'])
        self.assertFalse(p['strict_rc_ready'])
        self.assertEqual(m['rc_cycle23_k8s_ha_local_20261029']['score_delta_pp'],0)

    def test_current_and_historical_inventories_before_secret_scan(self):
        text=(ROOT/'.github/workflows/ci.yml').read_text()
        before='python3 tools/verify_rc_cycle22_inventory.py --historical'
        after='python3 tools/verify_rc_cycle41_inventory.py'
        self.assertIn(before,text)
        self.assertIn(after,text)
        self.assertLess(text.index(before),text.index(after))
        self.assertLess(text.index(after),text.index('Detect credential leaks'))
        self.assertIn('gitleaks/gitleaks-action@v2',text)

    def test_operator_docs_and_report_are_explicit_about_limits(self):
        report=json.loads((ROOT/'docs/validation/RC_CYCLE23_K8S_HA_LOCAL_20261029.json').read_text())
        self.assertEqual((report['score_before'],report['score_after']),(79,79))
        self.assertEqual(report['promotion_delta'],0)
        self.assertFalse(report['strict_rc_ready'])
        for lang in ('en','it'):
            s=(ROOT/f'docs/K8S_HA_ROLLING_AND_API_ACCEPTANCE.{lang}.md').read_text()
            for fragment in ('maxUnavailable','SIGTERM','1012','RWX','RPO'):
                if fragment=='RPO':continue
                self.assertIn(fragment,s)
            self.assertIn('kubernetes_manifest_test=true',s)

if __name__=='__main__':unittest.main()
