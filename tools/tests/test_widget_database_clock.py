"""Regression contract for timed widget expiry and duration from PostgreSQL."""
from pathlib import Path
import unittest
SOURCE = (Path(__file__).resolve().parents[2] / 'apps/api/src/server.ts').read_text()

class WidgetDatabaseClockTests(unittest.TestCase):
    def test_clock_sampled_after_validation(self):
        endpoint = SOURCE.split("app.post('/api/join/:code/activities/:aid/widgets/:wid/respond'",1)[1].split("app.get('/api/sessions/:id/widget-answers'",1)[0]
        self.assertIn("SELECT clock_timestamp() AS database_now", endpoint)
        self.assertGreater(endpoint.index("SELECT clock_timestamp() AS database_now"), endpoint.index("attachment_not_in_session"))
        self.assertLess(endpoint.index("SELECT clock_timestamp() AS database_now"), endpoint.index("INSERT INTO widget_answers"))

    def test_expiry_and_elapsed_same_sample(self):
        self.assertIn("elapsed=timing.elapsedMs", SOURCE)
        self.assertIn("if(!timing.valid)", SOURCE)
        self.assertNotIn("new Date(a.rows[0].database_now)", SOURCE)

if __name__ == '__main__': unittest.main()
