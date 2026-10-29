"""Authenticated, owner-only backup encryption and rotation regression tests."""
import os
import pathlib
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from backup_envelope import decrypt, encrypt, key_bytes, private_keygen, rotate, MAGIC, NONCE_SIZE, TAG_SIZE


class BackupEnvelopeSecurity(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = pathlib.Path(self.t.name)
        self.old = self.root / 'old.key'
        self.new = self.root / 'new.key'
        private_keygen(self.old)
        private_keygen(self.new)
        self.plaintext = self.root / 'original.tgz'
        self.plaintext.write_bytes(os.urandom(1048576 + 31))
        self.encrypted = self.root / 'snapshot.qenc'
        self.restored = self.root / 'restored.tgz'

    def test_random_key_and_file_mode(self):
        self.assertEqual(len(key_bytes(self.old)), 32)
        self.assertNotEqual(key_bytes(self.old), key_bytes(self.new))
        self.assertEqual(stat.S_IMODE(self.old.stat().st_mode), 0o600)
        with self.assertRaises(FileExistsError): private_keygen(self.old)

    def test_encryption_roundtrip_and_private_file(self):
        encrypt(self.plaintext, self.encrypted, self.old)
        ciphertext = self.encrypted.read_bytes()
        self.assertTrue(ciphertext.startswith(MAGIC))
        self.assertEqual(len(ciphertext), len(self.plaintext.read_bytes())+len(MAGIC)+NONCE_SIZE+TAG_SIZE)
        self.assertNotIn(self.plaintext.read_bytes()[:64], ciphertext)
        self.assertEqual(stat.S_IMODE(self.encrypted.stat().st_mode),0o600)
        decrypt(self.encrypted, self.restored, self.old)
        self.assertEqual(self.restored.read_bytes(), self.plaintext.read_bytes())
        self.assertEqual(stat.S_IMODE(self.restored.stat().st_mode),0o600)

    def test_wrong_key_does_not_publish_plaintext(self):
        encrypt(self.plaintext, self.encrypted, self.old)
        with self.assertRaisesRegex(ValueError,'authentication failed'):
            decrypt(self.encrypted,self.restored,self.new)
        self.assertFalse(self.restored.exists())
        self.assertFalse(list(self.root.glob('.quorivio-envelope-*')))

    def test_tamper_header_ciphertext_tag_and_truncation(self):
        encrypt(self.plaintext, self.encrypted,self.old)
        original = self.encrypted.read_bytes()
        for case, mutation in (
            ('header', bytes([original[0]^1])+original[1:]),
            ('nonce', original[:8]+bytes([original[8]^1])+original[9:]),
            ('ciphertext',original[:45]+bytes([original[45]^1])+original[46:]),
            ('tag',original[:-1]+bytes([original[-1]^1])),
            ('truncated',original[:10]),
            ('trailing', original+b'garbage'),
        ):
            with self.subTest(case=case):
                damaged=self.root/(case+'.qenc');damaged.write_bytes(mutation)
                with self.assertRaises(ValueError):decrypt(damaged,self.restored,self.old)
                self.assertFalse(self.restored.exists())

    def test_refuse_overwrite_and_symlink(self):
        encrypt(self.plaintext,self.encrypted,self.old)
        with self.assertRaises(FileExistsError):encrypt(self.plaintext,self.encrypted,self.old)
        self.restored.symlink_to(self.plaintext)
        with self.assertRaises(FileExistsError):decrypt(self.encrypted,self.restored,self.old)
        self.assertEqual(self.plaintext.stat().st_size, 1048576+31)

    def test_insecure_key_and_invalid_length(self):
        self.old.chmod(0o644)
        with self.assertRaises(ValueError):encrypt(self.plaintext,self.encrypted,self.old)
        self.old.chmod(0o600);self.old.write_bytes(b'x'*31)
        with self.assertRaises(ValueError):encrypt(self.plaintext,self.encrypted,self.old)
        self.old.unlink();self.old.symlink_to(self.new)
        with self.assertRaises(OSError):encrypt(self.plaintext,self.encrypted,self.old)

    def test_key_rotation_and_wrong_old_key_fail_closed(self):
        encrypt(self.plaintext,self.encrypted,self.old)
        rotated = self.root/'rotated.qenc'
        with self.assertRaises(ValueError):rotate(self.encrypted,rotated,self.new,self.old)
        self.assertFalse(rotated.exists())
        rotate(self.encrypted,rotated,self.old,self.new)
        with self.assertRaises(ValueError):decrypt(rotated,self.restored,self.old)
        self.assertFalse(self.restored.exists())
        decrypt(rotated,self.restored,self.new)
        self.assertEqual(self.restored.read_bytes(),self.plaintext.read_bytes())
        self.assertNotEqual(rotated.read_bytes(),self.encrypted.read_bytes())

    def test_empty_input_still_authenticated(self):
        self.plaintext.write_bytes(b'')
        encrypt(self.plaintext,self.encrypted,self.old)
        decrypt(self.encrypted,self.restored,self.old)
        self.assertEqual(self.restored.read_bytes(),b'')


if __name__ == '__main__':unittest.main()
