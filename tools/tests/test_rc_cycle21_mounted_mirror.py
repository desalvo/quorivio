"""RC21: immutable previous evidence, real mirror regression and no unearned credits."""
import json
import pathlib
import sys
import unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from verify_rc_cycle20_inventory import load_inventory as previous
from verify_rc_cycle21_inventory import load_inventory
from verify_rc_cycle61_inventory import verify_source, load_inventory as latest_inventory
from rc_gate_audit import audit
from rc_release_preflight import preflight
ROOT=pathlib.Path(__file__).resolve().parents[2]

class Cycle21Mirror(unittest.TestCase):
    def test_previous_inventory_immutable_and_current_source_exact(self):
        self.assertEqual(len(previous()),836)
        self.assertGreater(len(load_inventory()),len(previous()))
        self.assertEqual(verify_source(),len(latest_inventory()))
        self.assertIn('tools/backup_mirror.py',load_inventory())
    def test_full_postgres_mount_and_restored_data_acceptance(self):
        ci=(ROOT/'tools/ci_backup_restore.py').read_text()
        for phrase in ('mirror_backup(rotated_managed', 'verify_mirror(mirror_dir',
                       "if not os.path.ismount('/dev/shm')", 'quorivio_remote_mirror_restore_ci',
                       'restore_encrypted(mirror_dir / rotated_managed.name',
                       "tables(SOURCE) == tables(mirror_url)", 'PASS PostgreSQL 18 mounted-volume encrypted mirror'):
            self.assertIn(phrase,ci)
    def test_standard_ci_keeps_security_gates_and_new_inventory(self):
        ci=(ROOT/'.github/workflows/ci.yml').read_text()
        for text in ('python3 tools/verify_rc_cycle20_inventory.py --historical',
                     'python3 tools/verify_rc_cycle21_inventory.py --historical',
                     'python3 tools/verify_rc_cycle22_inventory.py',
                     'python3 tools/ci_backup_restore.py', 'gitleaks/gitleaks-action'):
            self.assertIn(text,ci)
        self.assertLess(ci.index('python3 tools/verify_rc_cycle22_inventory.py'),ci.index('Detect credential leaks'))
    def test_score_not_falsely_promoted(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        self.assertGreaterEqual(audit()['score'],77.0)
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertEqual(matrix['rc_cycle21_mounted_mirror_local_20261029']['increment_pp'],0)
        self.assertFalse(matrix['pending_local_batch']['strict_rc_ready'])
    def test_operator_docs_are_bilingual_and_explicitly_no_rto_claim(self):
        for lang in ('en','it'):
            text=(ROOT/f'docs/DR_MOUNTED_ENCRYPTED_MIRROR.{lang}.md').read_text()
            for expected in ('--mount-root','--work-dir','--key-file','--directory','RPO/RTO'):
                self.assertIn(expected,text)

if __name__=='__main__':unittest.main()
