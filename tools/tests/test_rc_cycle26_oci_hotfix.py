"""Formal cycle-26 remote failure and limited local repair evidence."""
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_cycle25_inventory import load_inventory as historical
from verify_rc_cycle26_inventory import load_inventory as historical_26
from verify_rc_cycle27_inventory import load_inventory,verify_source

class Cycle26RC(unittest.TestCase):
    def test_historical_archive_unmodified_and_current_git_hashes(self):
        self.assertEqual(len(historical()),872)
        self.assertEqual(len(historical_26()),877)
        self.assertGreater(len(load_inventory()),len(historical_26()))
        self.assertEqual(verify_source(),len(load_inventory()))

    def test_scoring_not_changed_by_failed_oci_run(self):
        m=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        self.assertEqual(sum(x['weight'] for x in m['gates']),100)
        self.assertEqual((len(m['gates']),audit()['score'],preflight()['accepted_gates']),(47,79.0,30))
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        h=m['rc_cycle26_ci_hotfix_20261030']
        self.assertEqual((h['origin_run_id'],h['failed_job']),(40975979003,123806382783))
        self.assertFalse(h['oci_runtime_amd64_verified'])
        self.assertFalse(h['oci_runtime_arm64_verified'])

    def test_ci_checks_historical_then_current_without_publication(self):
        wf=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/verify_rc_cycle25_inventory.py --historical',wf)
        self.assertIn('python3 tools/verify_rc_cycle26_inventory.py --historical',wf)
        self.assertIn('python3 tools/verify_rc_cycle27_inventory.py',wf)
        self.assertLess(wf.index('verify_rc_cycle25_inventory.py --historical'),wf.index('verify_rc_cycle26_inventory.py'))
        self.assertLess(wf.index('verify_rc_cycle27_inventory.py'),wf.index('Detect credential leaks'))
        self.assertIn('bash tools/ci_oci_runtime_smoke.sh quorivio:ci-oci-amd64 amd64',wf)
        self.assertIn('bash tools/ci_oci_runtime_smoke.sh quorivio:ci-oci-arm64 arm64',wf)
        self.assertIn('push: false',wf)

if __name__=='__main__': unittest.main()
