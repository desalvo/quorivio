"""DR rehearsal receipt: preflight, duration evidence and secret hygiene."""
from __future__ import annotations

import json
import pathlib
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from secure_instance_backup import CONFIRM, _backup_age_seconds, restore_drill


class DisasterRecoveryReceiptTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.spool = self.root / 'private'
        self.spool.mkdir(mode=0o700)
        self.assets = self.root / 'restored-assets'
        self.backup = self.root / 'sealed.qenc'
        self.key = self.root / 'private.key'
        self.receipt = self.root / 'receipt.json'
        self.manifest = {
            'created_at': (datetime.now(timezone.utc) - timedelta(minutes=4)).isoformat(),
            'files': [{'path': 'database.dump'}, {'path': 'assets/test/photo.png'}],
        }

    def run_drill(self, **opts):
        with patch('secure_instance_backup.verify_encrypted', return_value=self.manifest) as verify, \
             patch('secure_instance_backup.restore_encrypted', return_value=self.manifest) as restore:
            output = restore_drill(self.backup, self.assets, 'postgres://user:secret@db/test',
                                    self.key, self.spool, CONFIRM, self.receipt, **opts)
        return output, verify, restore

    def test_receipt_is_private_redacted_and_matches_result(self):
        result, verify, restore = self.run_drill(max_age_seconds=3600, max_restore_seconds=30)
        self.assertEqual(json.loads(self.receipt.read_text()), result)
        self.assertEqual(self.receipt.stat().st_mode & 0o777, 0o600)
        self.assertEqual(result['status'], 'restore_completed')
        self.assertEqual(result['objects_verified'], 2)
        self.assertTrue(result['age_threshold_met'])
        self.assertTrue(result['restore_duration_threshold_met'])
        self.assertIn('Not production RPO/RTO', result['limitations'])
        for forbidden in ('secret', 'postgres://', 'private.key', 'sealed.qenc', 'restored-assets', 'photo.png'):
            self.assertNotIn(forbidden, self.receipt.read_text())
        verify.assert_called_once()
        restore.assert_called_once()

    def test_existing_receipt_fails_before_any_database_operation(self):
        self.receipt.write_text('do not overwrite')
        with patch('secure_instance_backup.verify_encrypted') as verify:
            with self.assertRaises(FileExistsError):
                restore_drill(self.backup, self.assets, 'postgres://test', self.key,
                              self.spool, CONFIRM, self.receipt)
            verify.assert_not_called()
        self.assertEqual(self.receipt.read_text(), 'do not overwrite')

    def test_symlink_receipt_refused(self):
        victim = self.root / 'victim'
        victim.write_bytes(b'unchanged')
        self.receipt.symlink_to(victim)
        with patch('secure_instance_backup.verify_encrypted') as verify:
            with self.assertRaises(FileExistsError):
                restore_drill(self.backup, self.assets, 'postgres://test', self.key,
                              self.spool, CONFIRM, self.receipt)
            verify.assert_not_called()
        self.assertEqual(victim.read_bytes(), b'unchanged')

    def test_receipt_symlinked_ancestor_refused_without_restore(self):
        alternate = self.root / 'real-receipts'
        alternate.mkdir(mode=0o700)
        parent_link = self.root / 'alias'
        parent_link.symlink_to(alternate, target_is_directory=True)
        with patch('secure_instance_backup.verify_encrypted') as verify:
            with self.assertRaisesRegex(ValueError, 'symlink'):
                restore_drill(self.backup, self.assets, 'postgres://test', self.key,
                              self.spool, CONFIRM, parent_link / 'receipt.json')
            verify.assert_not_called()
        self.assertEqual(list(alternate.iterdir()), [])

    def test_wrong_confirmation_refused_before_inspection(self):
        with patch('secure_instance_backup.verify_encrypted') as verify:
            with self.assertRaisesRegex(ValueError, 'confirmation'):
                restore_drill(self.backup, self.assets, 'postgres://test', self.key,
                              self.spool, 'NOT CONFIRMED', self.receipt)
            verify.assert_not_called()
        self.assertFalse(self.receipt.exists())

    def test_stale_backup_refused_before_restore(self):
        with patch('secure_instance_backup.verify_encrypted', return_value=self.manifest), \
             patch('secure_instance_backup.restore_encrypted') as restore:
            with self.assertRaisesRegex(ValueError, 'age exceeds'):
                restore_drill(self.backup, self.assets, 'postgres://test', self.key,
                              self.spool, CONFIRM, self.receipt, max_age_seconds=10)
            restore.assert_not_called()
        self.assertFalse(self.receipt.exists())

    def test_late_duration_preserves_failed_policy_receipt_without_claiming_rollback(self):
        with patch('secure_instance_backup.verify_encrypted', return_value=self.manifest), \
             patch('secure_instance_backup.restore_encrypted', return_value=self.manifest), \
             patch('secure_instance_backup.time.monotonic', side_effect=[100.0, 103.0]):
            with self.assertRaisesRegex(ValueError, 'Restore completed but exceeded'):
                restore_drill(self.backup, self.assets, 'postgres://test', self.key,
                              self.spool, CONFIRM, self.receipt, max_restore_seconds=1.0)
        evidence = json.loads(self.receipt.read_text())
        self.assertEqual(evidence['status'], 'restore_completed')
        self.assertFalse(evidence['restore_duration_threshold_met'])
        self.assertEqual(evidence['restore_command_seconds'], 3)

    def test_manifest_switch_after_verify_refuses_receipt(self):
        changed = dict(self.manifest, created_at='2020-01-01T00:00:00+00:00')
        with patch('secure_instance_backup.verify_encrypted', return_value=self.manifest), \
             patch('secure_instance_backup.restore_encrypted', return_value=changed):
            with self.assertRaisesRegex(ValueError, 'manifest changed'):
                restore_drill(self.backup, self.assets, 'postgres://test', self.key,
                              self.spool, CONFIRM, self.receipt)
        self.assertFalse(self.receipt.exists())

    def test_timezones_future_dates_and_bad_limits(self):
        now = datetime.now(timezone.utc)
        self.assertLess(_backup_age_seconds((now-timedelta(seconds=1)).isoformat(), now), 2)
        for created_at in ('not-a-date', '2026-10-29T12:00:00'):
            with self.assertRaises(ValueError):
                _backup_age_seconds(created_at, now)
        with self.assertRaisesRegex(ValueError, 'future'):
            _backup_age_seconds((now+timedelta(hours=1)).isoformat(), now)
        for limit in (0, -1, float('inf'), float('nan'), 86400*366):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                restore_drill(self.backup, self.assets, 'postgres://test', self.key,
                              self.spool, CONFIRM, self.receipt, max_restore_seconds=limit)
        self.assertFalse(self.receipt.exists())


if __name__ == '__main__':
    unittest.main()
