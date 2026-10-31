"""Cycle 27 ensures new deployment acceptance cannot be counted before remote evidence."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_cycle26_inventory import load_inventory as historical
from verify_rc_cycle57_inventory import load_inventory, verify_source


class Cycle27(unittest.TestCase):
    def test_historical_and_current_source_integrity(self):
        self.assertEqual(len(historical()), 877)
        current = load_inventory()
        self.assertGreater(len(current), len(historical()))
        self.assertEqual(verify_source(), len(current))
        for entry in ('tools/ci_rootless_podman_smoke.sh',
                      'tools/tests/test_ci_rootless_podman_smoke.py',
                      'docs/ROOTLESS_PODMAN_RUNTIME_ACCEPTANCE.it.md',
                      'docs/ROOTLESS_PODMAN_RUNTIME_ACCEPTANCE.en.md'):
            self.assertIn(entry, current)

    def test_workflow_immutable_then_current_catalog_before_leak_detection(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text()
        older = 'python3 tools/verify_rc_cycle26_inventory.py --historical'
        newer = 'python3 tools/verify_rc_cycle41_inventory.py'
        self.assertIn(older, workflow)
        self.assertIn(newer, workflow)
        self.assertLess(workflow.index(older), workflow.index(newer))
        self.assertLess(workflow.index(newer), workflow.index('Detect credential leaks'))
        self.assertIn('gitleaks/gitleaks-action@v2', workflow)
        self.assertIn("if: github.event_name == 'workflow_dispatch' && inputs.rootless_podman_test", workflow)
        self.assertIn("if: github.event_name == 'workflow_dispatch' && inputs.runtime_arch_test", workflow)
        self.assertIn('push: false', workflow)

    def test_failed_old_ci_does_not_promote_any_gate(self):
        matrix = json.loads((ROOT / 'docs/RC_GATE_MATRIX.json').read_text())
        receipt = matrix['rc_cycle27_rootless_podman_local_20261030']
        self.assertEqual((receipt['score_before'], receipt['score_after']), (79.0, 79.0))
        self.assertEqual((receipt['accepted_gates'], receipt['partial_gates']), (30, 17))
        self.assertFalse(receipt['rootless_podman_verified_remotely'])
        self.assertFalse(receipt['oci_hotfix_verified_remotely'])
        self.assertFalse(receipt['strict_rc_ready'])
        self.assertEqual(receipt['last_full_ci_run'], 40975979003)
        self.assertEqual(sum(g['weight'] for g in matrix['gates']), 100)
        self.assertEqual((audit()['score'], preflight()['accepted_gates'],
                          len(preflight()['unaccepted_gates'])), (81.25, 36, 17))
        self.assertFalse(preflight()['release_candidate_ready'])

    def test_truthful_operator_documentation_and_frozen_source_receipt(self):
        report = json.loads((ROOT / 'docs/validation/RC_CYCLE27_ROOTLESS_PODMAN_LOCAL_20261030.json').read_text())
        self.assertFalse(report['new_rootless_podman_job_executed'])
        self.assertFalse(report['oci_arch_hotfix_executed_remotely'])
        self.assertEqual(report['score_after'], 79)
        for language in ('en', 'it'):
            doc = (ROOT / f'docs/ROOTLESS_PODMAN_RUNTIME_ACCEPTANCE.{language}.md').read_text()
            for required in ('PostgreSQL 18', 'rootless_podman_test=true',
                             'runtime_arch_test=true', 'publish_image=false', '79,0%' if language == 'it' else '79.0%'):
                self.assertIn(required, doc)


if __name__ == '__main__':
    unittest.main()
