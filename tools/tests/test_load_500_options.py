"""CLI regression checks without sending any requests."""
import pathlib, subprocess, sys, unittest
SCRIPT=pathlib.Path(__file__).resolve().parents[1]/'load_500.py'

class AnonymousLoadOptions(unittest.TestCase):
 def run_cli(self,*args):
  return subprocess.run([sys.executable,str(SCRIPT),*args],capture_output=True,text=True)
 def test_requires_qr_url_not_account_login(self):
  outcome=self.run_cli('--join-url','https://test.example/join/QR_TOKEN','--session-id','uuid','--users','501')
  self.assertNotEqual(outcome.returncode,0)
  self.assertIn('users must be 1..500',outcome.stderr)
 def test_requires_valid_shard(self):
  outcome=self.run_cli('--join-url','https://test.example/join/QR_TOKEN','--session-id','uuid','--users','500','--shards','5','--shard-index','5')
  self.assertNotEqual(outcome.returncode,0)
  self.assertIn('invalid shards/index',outcome.stderr)
 def test_rejects_arbitrary_destination_path(self):
  outcome=self.run_cli('--join-url','https://test.example/admin','--session-id','uuid')
  self.assertNotEqual(outcome.returncode,0)
  self.assertIn('join-url must be',outcome.stderr)
