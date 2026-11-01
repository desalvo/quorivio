"""Real encrypted backup/restore operator workflow and no-cleartext rekeying tests."""
import os
import pathlib
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import backup_envelope
import secure_instance_backup as sealed


class EncryptedInstanceWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.scratch = self.root / 'protected-spool'
        self.scratch.mkdir(mode=0o700)
        self.assets = self.root / 'assets'
        (self.assets / 'session').mkdir(parents=True)
        (self.assets / 'session' / 'image.bin').write_bytes(b'private file!')
        self.old = self.root / 'old.key'
        self.new = self.root / 'new.key'
        backup_envelope.private_keygen(self.old)
        backup_envelope.private_keygen(self.new)
        self.archive = self.root / 'sealed.qenc'

    @staticmethod
    def fake_pg(args, **kwargs):
        if args[0] == 'pg_dump':
            pathlib.Path(args[args.index('--file')+1]).write_bytes(b'DB DUMP: secret')

    def make(self):
        with patch('instance_backup.subprocess.run', side_effect=self.fake_pg):
            return sealed.backup_encrypted(self.archive, self.assets, 'postgres://dummy', self.old, self.scratch)

    def test_first_class_backup_and_verify_no_cleartext_or_overwrite(self):
        original = self.make()
        self.assertTrue(self.archive.read_bytes().startswith(backup_envelope.MAGIC))
        self.assertNotIn(b'DB DUMP: secret', self.archive.read_bytes())
        self.assertEqual(stat.S_IMODE(self.archive.stat().st_mode), 0o600)
        self.assertEqual(sealed.verify_encrypted(self.archive, self.old, self.scratch), original)
        self.assertEqual(list(self.scratch.iterdir()), [])
        with self.assertRaises(FileExistsError):
            self.make()
        self.assertEqual(list(self.scratch.iterdir()), [])

    def test_guarded_restore_roundtrip_into_empty_database(self):
        manifest = self.make()
        destination = self.root / 'recovered-assets'
        with patch('secure_instance_backup.assert_empty_database'), \
             patch('instance_backup.assert_empty_database'), \
             patch('instance_backup.subprocess.run', side_effect=self.fake_pg):
            result = sealed.restore_encrypted(self.archive, destination, 'postgres://empty',
                                               self.old, self.scratch, sealed.CONFIRM)
        self.assertEqual(result, manifest)
        self.assertEqual((destination / 'session' / 'image.bin').read_bytes(), b'private file!')
        self.assertEqual(list(self.scratch.iterdir()), [])

    def test_bad_confirmation_and_populated_database_fail_before_decrypt(self):
        self.make()
        with patch('secure_instance_backup.decrypt') as decrypt:
            with self.assertRaises(ValueError):
                sealed.restore_encrypted(self.archive, self.root / 'restore',
                    'postgres://empty', self.old, self.scratch, 'no')
            with patch('secure_instance_backup.assert_empty_database', side_effect=ValueError('populated')):
                with self.assertRaises(ValueError):
                    sealed.restore_encrypted(self.archive, self.root / 'restore',
                        'postgres://empty', self.old, self.scratch, sealed.CONFIRM)
            decrypt.assert_not_called()
        self.assertEqual(list(self.scratch.iterdir()), [])

    def test_bad_key_and_tampering_publish_neither_assets_nor_cleartext(self):
        self.make()
        with self.assertRaisesRegex(ValueError, 'authentication failed'):
            sealed.verify_encrypted(self.archive, self.new, self.scratch)
        data = bytearray(self.archive.read_bytes())
        data[-3] ^= 0x01
        self.archive.write_bytes(data)
        with patch('secure_instance_backup.assert_empty_database'), \
             patch('instance_backup.assert_empty_database'):
            with self.assertRaisesRegex(ValueError, 'authentication failed'):
                sealed.restore_encrypted(self.archive, self.root / 'restore',
                    'postgres://empty', self.old, self.scratch, sealed.CONFIRM)
        self.assertFalse((self.root / 'restore').exists())
        self.assertEqual(list(self.scratch.iterdir()), [])

    def test_refuse_unsafe_workspaces_without_dumping(self):
        self.scratch.chmod(0o755)
        with patch('secure_instance_backup.make_backup') as dump:
            with self.assertRaises(ValueError):
                sealed.backup_encrypted(self.archive, self.assets, 'postgres://dummy',
                                        self.old, self.scratch)
            dump.assert_not_called()
        self.scratch.chmod(0o700)
        (self.root / 'link').symlink_to(self.scratch)
        with self.assertRaises(ValueError):
            sealed.verify_encrypted(self.archive, self.old, self.root / 'link')

    def test_existing_assets_refused_even_if_key_valid(self):
        self.make()
        (self.root / 'nonempty').mkdir()
        (self.root / 'nonempty' / 'existing').write_bytes(b'x')
        with patch('secure_instance_backup.assert_empty_database') as db:
            with self.assertRaises(ValueError):
                sealed.restore_encrypted(self.archive, self.root / 'nonempty', 'postgres://empty',
                    self.old, self.scratch, sealed.CONFIRM)
            db.assert_not_called()

    def test_rotation_is_streaming_and_fails_closed(self):
        self.make()
        rotated = self.root / 'rotated.qenc'
        # A separate TemporaryDirectory must never be used to hold plaintext on rekey.
        with patch.object(backup_envelope.tempfile, 'TemporaryDirectory', side_effect=AssertionError('cleartext spool forbidden')):
            backup_envelope.rotate(self.archive, rotated, self.old, self.new)
        self.assertEqual(sealed.verify_encrypted(rotated, self.new, self.scratch),
                         sealed.verify_encrypted(self.archive, self.old, self.scratch))
        self.assertEqual(list(self.scratch.iterdir()), [])
        with self.assertRaises(ValueError):
            backup_envelope.rotate(self.archive, self.root / 'same.qenc', self.old, self.old)
        self.assertFalse((self.root / 'same.qenc').exists())
        bad = self.root / 'bad.qenc'
        corrupted = bytearray(self.archive.read_bytes()); corrupted[-1] ^= 1
        bad.write_bytes(corrupted)
        with self.assertRaisesRegex(ValueError, 'authentication failed'):
            backup_envelope.rotate(bad, self.root / 'never.qenc', self.old, self.new)
        self.assertFalse((self.root / 'never.qenc').exists())
        self.assertFalse(list(self.root.glob('.quorivio-envelope-*')))

    def test_large_streaming_rekey_roundtrip(self):
        raw = self.root / 'very-large.bin'
        raw.write_bytes(os.urandom(backup_envelope.CHUNK * 3 + 47))
        wrapped = self.root / 'large.qenc'; converted = self.root / 'large-rotated.qenc'
        backup_envelope.encrypt(raw, wrapped, self.old)
        backup_envelope.rotate(wrapped, converted, self.old, self.new)
        restored = self.root / 'large-restored.bin'
        backup_envelope.decrypt(converted, restored, self.new)
        self.assertEqual(restored.read_bytes(), raw.read_bytes())
        self.assertNotEqual(converted.read_bytes(), wrapped.read_bytes())

if __name__ == '__main__':
    unittest.main()
