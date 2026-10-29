"""Real AES-GCM encrypted archive mirroring tests, including safe mount guards."""
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from backup_envelope import private_keygen
from backup_mirror import mirror_backup, verify_mirror
from secure_instance_backup import backup_encrypted, verify_encrypted


class MirrorAcceptance(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = pathlib.Path(self.t.name)
        self.volume = self.root/'separate-mounted-volume'
        self.volume.mkdir(mode=0o700)
        self.work = self.root/'encrypted-scratch'
        self.work.mkdir(mode=0o700)
        self.assets = self.root/'assets'
        (self.assets/'session').mkdir(parents=True)
        (self.assets/'session'/'data.bin').write_bytes(b'personally identifiable secret content')
        self.key = self.root/'key'
        private_keygen(self.key)
        self.original = self.root/'source.qenc'
        def fake_pg(args, **kw):
            if args[0] == 'pg_dump':
                pathlib.Path(args[args.index('--file')+1]).write_bytes(b'CI PostgreSQL dump fixture')
        with patch('instance_backup.subprocess.run', side_effect=fake_pg):
            self.manifest = backup_encrypted(self.original, self.assets, 'postgres://disposable', self.key, self.work)
        self.assertEqual(list(self.work.iterdir()), [])

    def push(self):
        with patch('backup_mirror.os.path.ismount', return_value=True):
            return mirror_backup(self.original, self.volume, self.volume, self.key, self.work)

    def check(self, **kw):
        with patch('backup_mirror.os.path.ismount', return_value=True):
            return verify_mirror(self.volume, self.volume, 'source.qenc', kw.get('key', self.key), self.work)

    def test_mirror_actual_authenticated_roundtrip_with_receipt(self):
        record = self.push()
        dest = self.volume/'source.qenc'
        self.assertEqual(dest.read_bytes(), self.original.read_bytes())
        self.assertEqual(dest.stat().st_mode & 0o077, 0)
        self.assertEqual(verify_encrypted(dest, self.key, self.work), self.manifest)
        self.assertEqual(self.check()['status'], 'verified')
        self.assertEqual(record['verified_files'], 2)
        self.assertEqual(record['size_bytes'], self.original.stat().st_size)
        self.assertNotIn('personally identifiable', str(record))
        self.assertNotIn(str(self.root), str(record))
        self.assertEqual(list(self.work.iterdir()), [])

    def test_actual_tmpfs_mount_copy_and_verification_when_available(self):
        if not os.path.ismount('/dev/shm'):
            self.skipTest('OS does not expose mounted tmpfs')
        with tempfile.TemporaryDirectory(prefix='quorivio-actual-mount-', dir='/dev/shm') as name:
            mounted = pathlib.Path(name)
            mounted.chmod(0o700)
            mirror_backup(self.original, mounted, pathlib.Path('/dev/shm'), self.key, self.work)
            check = verify_mirror(mounted, pathlib.Path('/dev/shm'), 'source.qenc', self.key, self.work)
            self.assertEqual(check['files'], 2)
            self.assertEqual(list(self.work.iterdir()), [])

    def test_fail_closed_if_remote_mount_disconnected(self):
        with self.assertRaisesRegex(ValueError, 'not mounted'):
            mirror_backup(self.original, self.volume, self.volume, self.key, self.work)
        self.assertFalse(list(self.volume.iterdir()))

    def test_never_store_keys_or_decryption_workspace_on_mirror_mount(self):
        unsafe_key = self.volume/'unsafe.key'
        private_keygen(unsafe_key)
        unsafe_work = self.volume/'unsafe-work'
        unsafe_work.mkdir(mode=0o700)
        with patch('backup_mirror.os.path.ismount', return_value=True):
            with self.assertRaisesRegex(ValueError, 'key must be kept outside'):
                mirror_backup(self.original, self.volume, self.volume, unsafe_key, self.work)
            with self.assertRaisesRegex(ValueError, 'workspace must be outside'):
                mirror_backup(self.original, self.volume, self.volume, self.key, unsafe_work)
        self.assertFalse((self.volume/'source.qenc').exists())

    def test_wrong_key_does_not_publish_anything(self):
        wrong = self.root/'wrong.key'
        private_keygen(wrong)
        with patch('backup_mirror.os.path.ismount', return_value=True):
            with self.assertRaises(ValueError):
                mirror_backup(self.original, self.volume, self.volume, wrong, self.work)
        self.assertFalse(list(self.volume.iterdir()))
        self.assertEqual(list(self.work.iterdir()), [])

    def test_tampered_archive_does_not_publish(self):
        self.original.write_bytes(self.original.read_bytes()[:-2]+b'ZZ')
        with patch('backup_mirror.os.path.ismount', return_value=True):
            with self.assertRaisesRegex(ValueError, 'authentication failed'):
                mirror_backup(self.original, self.volume, self.volume, self.key, self.work)
        self.assertFalse(list(self.volume.iterdir()))

    def test_no_overwrite_even_on_repeat(self):
        self.push()
        current = (self.volume/'source.qenc').read_bytes()
        with self.assertRaises(FileExistsError):self.push()
        self.assertEqual((self.volume/'source.qenc').read_bytes(), current)

    def test_invalid_mount_root_and_symlink_are_rejected(self):
        with patch('backup_mirror.os.path.ismount', return_value=True):
            with self.assertRaises(ValueError):
                mirror_backup(self.original, self.volume, pathlib.Path('/'), self.key, self.work)
            symlink = self.root/'link'
            symlink.symlink_to(self.volume)
            with self.assertRaises(ValueError):
                mirror_backup(self.original, symlink, symlink, self.key, self.work)
        self.assertFalse(list(self.volume.iterdir()))

    def test_archive_corruption_and_forged_receipt_detected(self):
        self.push()
        backup = self.volume/'source.qenc'
        backup.write_bytes(backup.read_bytes()[:-2]+b'ZZ')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            self.check()
        self.assertEqual(list(self.work.iterdir()), [])

    def test_receipt_corruption_detected_without_decryption(self):
        self.push()
        receipt = self.volume/'source.qenc.receipt.json'
        record = json.loads(receipt.read_text())
        record['sha256_hex_groups'][0] = '00000000'
        receipt.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            self.check()

    def test_source_mutation_during_copy_fails_closed(self):
        import backup_mirror
        real = backup_mirror.verify_encrypted
        def mutating(path, key, work):
            self.original.write_bytes(self.original.read_bytes()+b'X')
            return real(path, key, work)
        with patch('backup_mirror.os.path.ismount', return_value=True), \
             patch('backup_mirror.verify_encrypted', side_effect=mutating):
            with self.assertRaisesRegex(ValueError, 'Source changed after copy'):
                mirror_backup(self.original, self.volume, self.volume, self.key, self.work)
        self.assertFalse(list(self.volume.iterdir()))

    def test_receipt_destination_preoccupied_fails_closed(self):
        (self.volume/'source.qenc.receipt.json').write_text('reserved')
        with self.assertRaises(FileExistsError):self.push()
        self.assertFalse((self.volume/'source.qenc').exists())

    def test_missing_receipt_rejected(self):
        self.push()
        (self.volume/'source.qenc.receipt.json').unlink()
        with self.assertRaises(FileNotFoundError):self.check()

    def test_mirror_private_directory_enforced(self):
        self.volume.chmod(0o755)
        with self.assertRaisesRegex(ValueError, 'owner-only'):
            self.push()
        self.volume.chmod(0o700)

if __name__=='__main__':unittest.main()
