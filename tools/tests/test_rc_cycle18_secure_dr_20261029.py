"""Cycle-18: verify production-facing operator path without fabricated RC credit."""
import json
import pathlib
import unittest
from rc_gate_audit import audit
from rc_release_preflight import preflight
ROOT = pathlib.Path(__file__).resolve().parents[2]

class RC18SecureDR(unittest.TestCase):
    def test_ci_keeps_legacy_acceptance_and_exercises_new_operator_path(self):
        body = (ROOT / 'tools/ci_backup_restore.py').read_text()
        for snippet in ('make_backup(backup, original_assets, SOURCE)',
                        'rotate(encrypted, rotated, old_key, new_key)',
                        'backup_encrypted(managed_archive, original_assets, SOURCE,',
                        'verify_encrypted(managed_archive, old_key, protected_spool)',
                        'restore_encrypted(managed_archive, alternate_assets, alternate_url,',
                        "alternate_db = 'quorivio_restore_sealed_acceptance'",
                        'Managed encrypted schema mismatch', 'Managed encrypted {table} row count differs'):
            self.assertIn(snippet, body)
        self.assertNotIn("managed_manifest['files'] == manifest['files']", body)  # pg_dump headers carry timestamps
        self.assertIn("'cryptography>=43,<47'", (ROOT / '.github/workflows/ci.yml').read_text())

    def test_rotation_never_spools_plaintext(self):
        code = (ROOT / 'tools/backup_envelope.py').read_text()
        fragment = code.split('def rotate(', 1)[1].split('\ndef main()', 1)[0]
        self.assertNotIn('TemporaryDirectory', fragment)
        self.assertIn('encipher.update(decipher.update(chunk))', fragment)
        self.assertIn('decipher.finalize()', fragment)
        self.assertIn('exclusive_output(target)', fragment)

    def test_dr_procedures_are_bilingual_and_explicitly_nonautomatic(self):
        for lang in ('it','en'):
            doc = (ROOT / f'docs/DR_SECURE_WORKFLOW.{lang}.md').read_text()
            for s in ('backup', 'verify', 'rotate', 'restore', 'RPO/RTO', 'secure_instance_backup.py'):
                self.assertIn(s, doc)

    def test_gates_not_promoted_without_github_evidence(self):
        d = json.loads((ROOT / 'docs/RC_GATE_MATRIX.json').read_text())
        self.assertGreaterEqual(audit()['score'], 77.0)
        self.assertEqual(sum(g['weight'] for g in d['gates']), 100)
        self.assertEqual(len(preflight()['unaccepted_gates']), 17)
        self.assertFalse(preflight()['release_candidate_ready'])
        self.assertEqual(d['rc_cycle17_encrypted_backup_local_20261029']['delta_pp'],0)

    def test_latest_manifest_is_current_and_previous_is_historical(self):
        wf = (ROOT / '.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/verify_rc_cycle17_inventory.py --historical', wf)
        self.assertIn('python3 tools/verify_rc_cycle18_inventory.py', wf)
        self.assertLess(wf.index('python3 tools/verify_rc_cycle18_inventory.py'), wf.index('Detect credential leaks'))

if __name__ == '__main__':unittest.main()
