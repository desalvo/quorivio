"""Regression: PostgreSQL int8 duration_ms is lossless JSON text (run 40379416187)."""
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ci_timed_widgets_postgres import duration_milliseconds

class DurationSerializationRegression(unittest.TestCase):
    def test_valid_int8_values(self):
        for duration in ('0','1','1000','9223372036854775807'):
            with self.subTest(duration=duration):
                self.assertEqual(duration_milliseconds(duration),int(duration))

    def test_reject_non_strings_or_lossy_json_numbers(self):
        for invalid in (0,0.0,True,None,{},[],b'12','1.5','1e3','-1','+1','',
                        '9223372036854775808','²', '١٢'):
            with self.subTest(invalid=invalid):
                with self.assertRaises(AssertionError):
                    duration_milliseconds(invalid)

    def test_both_endpoints_return_full_precision_bigint(self):
        server=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
        widget=server.split("app.get('/api/sessions/:id/activities/:aid/widgets/:wid/timed-leaderboard'",1)[1].split("app.get('/api/sessions/:id/activities/:aid/timed-leaderboard'",1)[0]
        legacy=server.split("app.get('/api/sessions/:id/activities/:aid/timed-leaderboard'",1)[1].split("app.post('/api/join/:code/respond'",1)[0]
        self.assertIn('w.elapsed_ms AS duration_ms',widget)
        self.assertIn('r.elapsed_ms AS duration_ms',legacy)
        self.assertNotIn('elapsed_ms::int',widget+legacy)

    def test_ci_asserts_with_lossless_parser(self):
        source=(ROOT/'tools/ci_timed_widgets_postgres.py').read_text(encoding='utf8')
        self.assertIn('duration_milliseconds(initial_duration)>=0',source)
        self.assertIn("[duration_milliseconds(r['duration_ms']) for r in ranks]",source)
        self.assertIn("duration_milliseconds(old_rank['ranking'][0]['duration_ms'])>=0",source)

if __name__=='__main__': unittest.main()
