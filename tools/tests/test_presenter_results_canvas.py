"""Source contract regressions for presenter-only slide results."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT / 'apps/web/src/main.tsx').read_text()
CSS = (ROOT / 'apps/web/src/style.css').read_text()


class PresenterResultsTests(unittest.TestCase):
    def test_results_are_in_canvas_at_saved_geometry(self):
        component = UI.split('function PresenterPageResults(')[1].split('\nfunction AudienceExtensions(')[0]
        self.assertIn('projection-results-control', component)
        for coord in ('layout.x', 'layout.y', 'layout.width', 'layout.height', 'layout.rotation'):
            self.assertIn(coord, component)
        self.assertIn('aria-expanded={visible}', component)
        self.assertIn('aria-controls="presenter-page-results"', component)
        self.assertIn('!control&&', component)
        self.assertIn('.projection-results-control{position:absolute', CSS)

    def test_topic_questions_live_in_results_panel(self):
        component = UI.split('function PresenterPageResults(')[1].split('\nfunction AudienceExtensions(')[0]
        self.assertIn("w.kind==='topic-question'", component)
        self.assertIn('<TopicPresenterList', component)
        self.assertIn("activity.type==='timed_quiz'", component)
        self.assertIn('<TimedLeaderboard', component)

if __name__ == '__main__':
    unittest.main()
