"""Manual lock recovery refuses unsafe or ambiguous workspace states."""
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from recover_conversion_lock import inspect_and_recover, main

class LockRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        self.job='a'*32
        self.work=self.root/self.job
        self.work.mkdir()
        (self.work/'source.pdf').write_bytes(b'%PDF')
        (self.work/'.conversion-lock').mkdir()

    def test_dry_run_does_not_delete(self):
        self.assertFalse(inspect_and_recover(self.root,self.job)['recovered'])
        self.assertTrue((self.work/'.conversion-lock').exists())

    def test_explicit_confirmation_removes_lock(self):
        self.assertTrue(inspect_and_recover(self.root,self.job,confirm=True)['recovered'])
        self.assertFalse((self.work/'.conversion-lock').exists())

    def test_rejects_existing_output(self):
        (self.work/'pages').mkdir()
        with self.assertRaisesRegex(ValueError,'output exists'):
            inspect_and_recover(self.root,self.job,confirm=True)

    def test_rejects_nonempty_lock(self):
        (self.work/'.conversion-lock'/'active').touch()
        with self.assertRaisesRegex(ValueError,'nonempty'):
            inspect_and_recover(self.root,self.job,confirm=True)

    def test_rejects_symlinked_lock(self):
        (self.work/'.conversion-lock').rmdir()
        (self.work/'.conversion-lock').symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'unsafe'):
            inspect_and_recover(self.root,self.job,confirm=True)

    def test_requires_workers_stopped_acknowledgment(self):
        with self.assertRaises(SystemExit):
            main([self.job,'--root',str(self.root),'--recover'])
        self.assertTrue((self.work/'.conversion-lock').exists())

    def test_bad_id_rejected(self):
        with self.assertRaisesRegex(ValueError,'invalid job'):
            inspect_and_recover(self.root,'../oops')
