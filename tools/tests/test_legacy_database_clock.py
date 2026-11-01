"""Legacy quiz and timed widget use the same PostgreSQL deadline policy."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
SOURCE=(ROOT/'apps/api/src/server.ts').read_text()
class LegacyClockContract(unittest.TestCase):
 def test_legacy_submission_uses_database_clock(self):
  endpoint=SOURCE.split("app.post('/api/join/:code/respond'",1)[1].split("server.on('upgrade'",1)[0]
  self.assertIn("SELECT clock_timestamp() AS database_now",endpoint)
  self.assertIn("timedDeadline(act.opened_at",endpoint)
  self.assertNotIn("Date.now()>new Date(act.opened_at)",endpoint)
  self.assertIn("timing!.elapsedMs",endpoint)
 def test_both_paths_use_shared_policy(self):
  self.assertIn("timedDeadline(a.rows[0].opened_at",SOURCE)
  self.assertIn("timedDeadline(act.opened_at",SOURCE)
  self.assertTrue((ROOT/'apps/api/src/timed-deadline.ts').exists())
