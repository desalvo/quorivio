"""Cycle 17: encrypted DR acceptance is mandatory but not yet remotely verified."""
import json
import pathlib
import unittest
from rc_gate_audit import audit
from rc_release_preflight import preflight

ROOT = pathlib.Path(__file__).resolve().parents[2]

class Cycle17EncryptedDR(unittest.TestCase):
    def test_ci_uses_real_postgres_restore_with_envelope_and_crypto_installed(self):
        source = (ROOT/'tools/ci_backup_restore.py').read_text()
        wf = (ROOT/'.github/workflows/ci.yml').read_text()
        for fragment in ('private_keygen(old_key)', 'private_keygen(new_key)',
                        'encrypt(backup, encrypted, old_key)', 'rotate(encrypted, rotated, old_key, new_key)',
                        'decrypt(rotated, decrypted, new_key)', 'restore(decrypted, restored_assets, target',
                        'Schema table list differs after restore', 'Rotated encrypted backup data mismatch'):
            self.assertIn(fragment, source)
        self.assertIn("'cryptography>=43,<47'", wf)
        self.assertIn('python3 tools/ci_backup_restore.py', wf)
        self.assertLess(wf.index("'cryptography>=43,<47'"),wf.index('python3 tools/ci_backup_restore.py'))
        self.assertIn('python3 tools/verify_rc_cycle16_inventory.py --historical',wf)
        self.assertIn('python3 tools/verify_rc_cycle17_inventory.py',wf)

    def test_score_retains_17_unaccepted_parent_gates(self):
        m = json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        gates = {g['id']:g for g in m['gates']}
        self.assertEqual(len(gates),45)
        self.assertEqual(sum(g['weight'] for g in gates.values()),100)
        self.assertEqual(audit()['score'],77.0)
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertFalse(preflight()['release_candidate_ready'])
        for parent in ('D2','D6'):
            self.assertEqual(gates[parent]['status'],'partial')
        self.assertTrue(m['pending_local_batch']['new_ci_required'])
        self.assertFalse(m['pending_local_batch']['new_feature_promoted'])
        self.assertEqual(m['rc_cycle17_encrypted_backup_local_20261029']['delta_pp'],0)

    def test_operator_docs_do_not_claim_auto_encryption_or_production_rto(self):
        en=(ROOT/'docs/DR_ENCRYPTED_BACKUPS.en.md').read_text()
        it=(ROOT/'docs/DR_ENCRYPTED_BACKUPS.it.md').read_text()
        self.assertIn('does **not** encrypt by itself',en)
        self.assertIn('RPO/RTO',en)
        self.assertIn('non esegue la cifratura automaticamente',it)
        self.assertIn('RPO/RTO',it)
        self.assertIn('AES-256-GCM',en)

if __name__=='__main__':unittest.main()
