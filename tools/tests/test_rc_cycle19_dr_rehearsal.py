"""Cycle 19 verifies real DR acceptance wiring without claiming production sign-off."""
import json
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from verify_rc_cycle18_inventory import load_inventory as historical_18
from verify_rc_cycle19_inventory import load_inventory as current_19

ROOT=pathlib.Path(__file__).resolve().parents[2]

class Cycle19DR(unittest.TestCase):
    def test_real_postgres_ci_drill_and_receipt_artifact(self):
        body=(ROOT/'tools/ci_backup_restore.py').read_text()
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        for needle in ('restore_drill(rotated_managed, drill_assets, drill_url',
                       "drill_db = 'quorivio_restore_drill_acceptance'",
                       "'DR rehearsal schema mismatch'", "'DR rehearsal left plaintext files'"):
            self.assertIn(needle,body)
        self.assertIn('Upload sanitized disposable DR rehearsal metrics',workflow)
        self.assertIn('dr-rehearsal-ci-only',workflow)
        self.assertIn('retention-days: 7',workflow)
        self.assertIn('python3 tools/verify_rc_cycle18_inventory.py --historical',workflow)
        self.assertIn('python3 tools/verify_rc_cycle19_inventory.py',workflow)
        self.assertLess(workflow.index('python3 tools/verify_rc_cycle19_inventory.py'),
                        workflow.index('Detect credential leaks'))

    def test_retention_never_automatically_enabled_in_deployment(self):
        code=(ROOT/'tools/backup_retention.py').read_text()
        self.assertIn("apply: bool = False",code)
        self.assertIn("min_keep: int = 3",code)
        self.assertIn('PRUNE-QUORIVIO-ENCRYPTED-BACKUPS',code)
        for lang in ('en','it'):
            doc=(ROOT/f'docs/DR_REHEARSAL_AND_RETENTION.{lang}.md').read_text()
            self.assertIn('backup_retention.py',doc)
            self.assertIn('secure_instance_backup.py drill',doc)
            self.assertIn('RPO',doc)
            self.assertIn('RTO',doc)

    def test_historical_manifest_preserved_and_new_sources_complete(self):
        self.assertEqual(len(historical_18()),823)
        current=current_19()
        self.assertGreater(len(current),len(historical_18()))
        self.assertEqual(len(current),832)  # immutable cycle-19 snapshot, not today's source files
        for name in ('tools/backup_retention.py','tools/tests/test_backup_retention.py',
                     'tools/tests/test_dr_rehearsal_receipt.py',
                     'docs/DR_REHEARSAL_AND_RETENTION.en.md',
                     'docs/DR_REHEARSAL_AND_RETENTION.it.md'):
            self.assertIn(name,current)

    def test_strict_rc_still_blocked_without_independent_recovery(self):
        d=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        self.assertGreaterEqual(audit()['score'],77.0)
        self.assertEqual(sum(g['weight'] for g in d['gates']),100)
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertEqual(d['rc_cycle17_encrypted_backup_local_20261029']['delta_pp'],0)

if __name__=='__main__': unittest.main()
