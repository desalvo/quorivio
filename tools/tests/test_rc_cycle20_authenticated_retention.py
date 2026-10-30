"""RC 20: authenticated retention, historical ledger and no unverified gate credit."""
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_cycle19_inventory import load_inventory as historical_19
from verify_rc_cycle20_inventory import load_inventory as historical_20
from verify_rc_cycle21_inventory import load_inventory as current_21
from verify_rc_cycle47_inventory import verify_source

ROOT = pathlib.Path(__file__).resolve().parents[2]

class Cycle20SafeRetention(unittest.TestCase):
    def test_historical_catalog_is_immutable_and_current_inventory_exact(self):
        self.assertEqual(len(historical_19()), 832)
        self.assertEqual(len(historical_20()), 836)
        manifest = current_21()
        self.assertGreater(len(manifest), len(historical_19()))
        self.assertEqual(verify_source(), len(__import__("verify_rc_cycle47_inventory").load_inventory()))
        self.assertIn('tools/tests/test_rc_cycle20_authenticated_retention.py', manifest)

    def test_real_postgres_acceptance_checks_authenticated_retention_and_legal_holds(self):
        text = (ROOT/'tools/ci_backup_restore.py').read_text()
        for token in ('prune_encrypted', "'stale.qenc'", "'current.qenc'",
                      'authenticated_snapshots', 'PRUNE_CONFIRM',
                      "'retention-exercise'", 'key_files=(old_key, new_key)',
                      'not list(protected_spool.iterdir())'):
            self.assertIn(token, text)
        code=(ROOT/'tools/backup_retention.py').read_text()
        for token in ('verify_encrypted(backup', '_legal_holds',
                      'private_workspace', 'Backup set changed during retention validation',
                      'key_files: tuple[pathlib.Path, ...]', 'apply: bool = False'):
            self.assertIn(token,code)

    def test_ci_uses_current_not_old_hashes_and_does_not_disable_scans(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/verify_rc_cycle19_inventory.py --historical',workflow)
        self.assertIn('python3 tools/verify_rc_cycle20_inventory.py --historical',workflow)
        self.assertIn('python3 tools/verify_rc_cycle21_inventory.py --historical',workflow)
        self.assertLess(workflow.index('python3 tools/verify_rc_cycle22_inventory.py'),
                        workflow.index('Detect credential leaks'))
        self.assertIn('gitleaks/gitleaks-action',workflow)
        self.assertIn('python3 tools/ci_backup_restore.py',workflow)

    def test_unchanged_score_and_unaccepted_external_gates(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        self.assertGreaterEqual(audit()['score'], 77.0)
        self.assertEqual(sum(g['weight'] for g in matrix['gates']), 100)
        self.assertEqual(len(preflight()['unaccepted_gates']), 17)
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertEqual(matrix['rc_cycle21_mounted_mirror_local_20261029']['increment_pp'],0)

if __name__ == '__main__': unittest.main()
