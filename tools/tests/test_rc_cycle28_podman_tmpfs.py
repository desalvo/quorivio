"""Cycle 28: verified CI evidence, still-open rootless gate and exact current inventory."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_rc_cycle27_inventory import load_inventory as prior_inventory
from verify_rc_cycle33_inventory import load_inventory, verify_source
from rc_release_preflight import preflight


class Cycle28(unittest.TestCase):
    def test_immutable_history_and_current_checksum(self):
        self.assertEqual(len(prior_inventory()), 885)
        self.assertGreater(len(load_inventory()), len(prior_inventory()))
        self.assertEqual(verify_source(), len(load_inventory()))

    def test_workflow_runs_historical_before_current_before_leak_detection(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text()
        historic = 'python3 tools/verify_rc_cycle27_inventory.py --historical'
        latest = 'python3 tools/verify_rc_cycle33_inventory.py'
        leak = 'Detect credential leaks'
        self.assertIn(historic, workflow)
        self.assertIn(latest, workflow)
        self.assertLess(workflow.index(historic), workflow.index(latest))
        self.assertLess(workflow.index(latest), workflow.index(leak))
        self.assertIn('gitleaks/gitleaks-action@v2', workflow)

    def test_run_records_six_green_and_one_failed_without_promotion(self):
        matrix = json.loads((ROOT / 'docs/RC_GATE_MATRIX.json').read_text())
        receipt = matrix['rc_cycle28_podman_tmpfs_hotfix_20261030']
        self.assertEqual(receipt['source_run_id'], 40980312270)
        self.assertEqual(len(receipt['passed_jobs']), 6)
        self.assertEqual(receipt['failed_job'], 123820527939)
        self.assertTrue(receipt['oci_amd64_arm64_runtime_verified'])
        self.assertFalse(receipt['github_rootless_fixed_verified'])
        self.assertEqual(receipt['score_before'], receipt['score_after'])
        self.assertEqual((receipt['accepted_gates'],receipt['partial_gates']), (30,17))
        self.assertEqual(preflight()['accepted_gates'], 31)
        self.assertFalse(preflight()['release_candidate_ready'])
        report = json.loads((ROOT / 'docs/validation/RC_CYCLE28_PODMAN_TMPFS_HOTFIX_LOCAL_20261030.json').read_text())
        self.assertFalse(report['podman_rootless_app_started'])
        self.assertFalse(report['rootless_tmpfs_hotfix_github_executed'])

    def test_documented_unprivileged_tmpfs_and_no_automatic_publish(self):
        script = (ROOT/'tools/ci_rootless_podman_smoke.sh').read_text()
        self.assertIn('tmpfs-mode=0700,U=true', script)
        self.assertIn('fs.writeFileSync', script)
        self.assertNotIn('--privileged', script)
        for lang in ('it','en'):
            d = (ROOT/f'docs/ROOTLESS_PODMAN_TMPFS_HOTFIX_RC28.{lang}.md').read_text()
            self.assertIn('40980312270', d)
            self.assertIn('123820527939', d)
            self.assertIn('publish_image=false', d)
            self.assertIn('79,0%' if lang == 'it' else '79.0%', d)


if __name__ == '__main__':
    unittest.main()
