"""Retention must verify complete sealed backups and protect legal holds before deletion."""
import hashlib
import io
import json
import os
import pathlib
import sys
import tarfile
import tempfile
import time
import unittest
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from backup_envelope import MAGIC, encrypt, private_keygen
from backup_retention import CONFIRM, DAY, prune_encrypted, retention_plan


class RetentionPolicy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.base = self.root / 'backups'
        self.base.mkdir(mode=0o700)
        self.workspace = self.root / 'work'
        self.workspace.mkdir(mode=0o700)
        self.key = self.root / 'key-1'
        self.other_key = self.root / 'key-2'
        private_keygen(self.key)
        private_keygen(self.other_key)
        self.holds = self.root / 'holds.json'
        self.set_holds([])
        self.now = time.time()

    def set_holds(self, names):
        self.holds.write_text(json.dumps({'version': 1, 'hold': names}))
        self.holds.chmod(0o600)

    def apply(self, **kwargs):
        options = dict(days=30, min_keep=1, apply=True, confirmation=CONFIRM,
                       holds_file=self.holds, key_files=(self.key,), work_dir=self.workspace)
        options.update(kwargs)
        return prune_encrypted(self.base, **options)

    def add_backup(self, name, age_days, *, key=None):
        """Real authenticated envelope, with a valid Quorivio tar/manifest."""
        p = self.base / name
        clear = self.workspace / 'source.tgz'
        payload = b'CI-only synthetic PostgreSQL dump with no personal content'
        obj = {'path': 'database.dump', 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()}
        manifest = {'format': 'quorivio-instance-backup', 'version': 1,
                    'created_at': datetime.now(timezone.utc).isoformat(), 'files': [obj]}
        data = json.dumps(manifest).encode('utf-8')
        with tarfile.open(clear, 'w:gz') as tar:
            for path, content in (('manifest.json', data), ('database.dump', payload)):
                entry = tarfile.TarInfo(path)
                entry.size = len(content)
                tar.addfile(entry, io.BytesIO(content))
        encrypt(clear, p, self.key if key is None else key)
        clear.unlink()
        ts = self.now - age_days * DAY
        os.utime(p, (ts, ts))
        return p

    def test_dry_run_does_not_delete_and_keeps_newest_three_even_when_stale(self):
        files = [self.add_backup(f'{n}.qenc', d) for n, d in enumerate([80,70,60,50,40])]
        result = prune_encrypted(self.base, days=30, min_keep=3)
        self.assertEqual(result['action'], 'dry_run')
        self.assertEqual(result['removed_count'], 0)
        self.assertEqual(set(result['candidates']), {'0.qenc', '1.qenc'})
        self.assertTrue(all(p.exists() for p in files))

    def test_actual_apply_needs_opt_in_and_never_deletes_key_or_other_files(self):
        new = self.add_backup('new.qenc', 1)
        old = self.add_backup('old.qenc', 90)
        non_backup = self.base / 'encryption.key'
        non_backup.write_bytes(b'not for deletion')
        with self.assertRaisesRegex(ValueError, 'confirmation'):
            prune_encrypted(self.base, days=30, min_keep=1, apply=True)
        result = self.apply()
        self.assertEqual(result['removed_count'], 1)
        self.assertEqual(result['authenticated_snapshots'], 2)
        self.assertFalse(old.exists())
        self.assertTrue(new.exists())
        self.assertEqual(non_backup.read_bytes(), b'not for deletion')
        self.assertEqual(list(self.workspace.iterdir()), [])

    def test_symlink_file_refuses_entire_operation(self):
        self.add_backup('safe.qenc', 80)
        target = self.base / 'outside.key'
        target.write_bytes(b'unchanged')
        (self.base / 'link.qenc').symlink_to(target)
        with self.assertRaises(ValueError):
            self.apply()
        self.assertTrue((self.base / 'safe.qenc').exists())
        self.assertEqual(target.read_bytes(), b'unchanged')

    def test_public_directory_refused(self):
        self.base.chmod(0o755)
        with self.assertRaisesRegex(ValueError, '0700'):
            retention_plan(self.base)

    def test_bad_magic_refused_before_deletion(self):
        self.add_backup('old.qenc', 80)
        bad = self.base / 'malformed.qenc'
        bad.write_bytes(b'not sealed')
        bad.chmod(0o600)
        with self.assertRaisesRegex(ValueError, 'not Quorivio'):
            self.apply()
        self.assertTrue((self.base / 'old.qenc').exists())

    def test_retain_one_regardless_of_age(self):
        p = self.add_backup('only.qenc', 900)
        result = self.apply()
        self.assertEqual(result['removed_count'], 0)
        self.assertTrue(p.exists())

    def test_bad_policy_values_fail_closed(self):
        for val in (0, -1, 40000, True):
            with self.subTest(val=val), self.assertRaises(ValueError):
                retention_plan(self.base, days=val)

    def test_newer_mtime_retains_independent_of_filename(self):
        a=self.add_backup('a.qenc', 1)
        b=self.add_backup('b.qenc', 50)
        c=self.add_backup('c.qenc', 60)
        result=prune_encrypted(self.base, days=30, min_keep=1)
        self.assertIn('a.qenc', result['kept'])
        self.assertEqual(set(result['candidates']), {'b.qenc', 'c.qenc'})

    def test_corrupt_newest_archive_prevents_any_deletion(self):
        newer = self.add_backup('latest.qenc', 1)
        older = self.add_backup('old.qenc', 90)
        content = bytearray(newer.read_bytes())
        content[-20] ^= 0x13
        newer.write_bytes(content)
        with self.assertRaisesRegex(ValueError, 'authentication or content verification failed'):
            self.apply()
        self.assertTrue(newer.exists())
        self.assertTrue(older.exists())
        self.assertEqual(list(self.workspace.iterdir()), [])

    def test_missing_wrong_key_or_work_dir_refuses_apply(self):
        a = self.add_backup('latest.qenc', 1)
        b = self.add_backup('older.qenc', 90)
        for options in ({'key_files': ()}, {'work_dir': None}, {'holds_file': None}):
            with self.subTest(options=options), self.assertRaisesRegex(ValueError, 'requires'):
                self.apply(**options)
        with self.assertRaisesRegex(ValueError, 'authentication or content verification failed'):
            self.apply(key_files=(self.other_key,))
        self.assertTrue(a.exists() and b.exists())

    def test_multiple_generations_keys_verified_before_deletion(self):
        current = self.add_backup('latest.qenc', 1, key=self.other_key)
        old = self.add_backup('old.qenc', 90)
        result = self.apply(key_files=(self.key, self.other_key))
        self.assertEqual(result['authenticated_snapshots'], 2)
        self.assertFalse(old.exists())
        self.assertTrue(current.exists())

    def test_legal_hold_keeps_old_backup_and_does_not_count_as_minimum(self):
        current = self.add_backup('latest.qenc', 1)
        middle = self.add_backup('middle.qenc', 90)
        held = self.add_backup('held.qenc', 100)
        self.set_holds(['held.qenc'])
        report = self.apply()
        self.assertEqual(report['legal_holds'], ['held.qenc'])
        self.assertEqual(report['removed_count'], 1)
        self.assertTrue(current.exists() and held.exists())
        self.assertFalse(middle.exists())

    def test_held_newest_is_additional_to_minimum_unheld_copies(self):
        held = self.add_backup('held.qenc', 1)
        keep = self.add_backup('keep.qenc', 90)
        delete = self.add_backup('delete.qenc', 100)
        self.set_holds(['held.qenc'])
        result = self.apply()
        self.assertEqual(result['removed_count'], 1)
        self.assertTrue(held.exists() and keep.exists())
        self.assertFalse(delete.exists())

    def test_missing_legal_hold_fails_closed(self):
        self.add_backup('latest.qenc', 1)
        old = self.add_backup('old.qenc', 90)
        self.set_holds(['removed-or-offsite.qenc'])
        with self.assertRaisesRegex(ValueError, 'absent'):
            self.apply()
        self.assertTrue(old.exists())

    def test_hold_registry_symlink_bad_permissions_and_malformed_entries(self):
        self.add_backup('latest.qenc', 1)
        old = self.add_backup('old.qenc', 90)
        for entries in (['../old.qenc'], ['old.qenc', 'old.qenc'], ['bad/path.qenc'], [22]):
            with self.subTest(entries=entries):
                self.set_holds(entries)
                with self.assertRaises(ValueError):
                    self.apply()
                self.assertTrue(old.exists())
        self.set_holds([])
        self.holds.chmod(0o644)
        with self.assertRaisesRegex(ValueError, 'owner-only'):
            self.apply()
        self.holds.chmod(0o600)
        alias = self.root / 'hold-alias.json'
        alias.symlink_to(self.holds)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.apply(holds_file=alias)
        self.assertTrue(old.exists())

    def test_mid_scan_mutation_fails_before_any_delete(self):
        a = self.add_backup('latest.qenc', 1)
        b = self.add_backup('old.qenc', 90)
        from unittest.mock import patch
        from backup_retention import verify_encrypted as real_verify
        def mutate(*args):
            result = real_verify(*args)
            if args[0] == a:
                os.utime(b, None)
            return result
        with patch('backup_retention.verify_encrypted', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'changed during retention validation'):
                self.apply()
        self.assertTrue(a.exists() and b.exists())


if __name__ == '__main__': unittest.main()
