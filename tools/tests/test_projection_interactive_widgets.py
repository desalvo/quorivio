from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = (ROOT / 'apps/web/src/main.tsx').read_text()
CSS = (ROOT / 'apps/web/src/style.css').read_text()

class ProjectionInteractiveWidgetTests(unittest.TestCase):
    def test_question_and_quiz_have_projection_component(self):
        self.assertIn("if(kind==='question'||kind==='timed-quiz')", SRC)
        self.assertIn('projection-interactive-options', SRC)
        self.assertIn('options.map((option:any)', SRC)
    def test_correct_options_are_not_marked_on_projection(self):
        body = SRC.split("if(kind==='question'||kind==='timed-quiz'){")[1].split("if(kind==='text'||kind==='postit')")[0]
        self.assertNotIn('correctOptionId', body)
        self.assertNotIn('correctOptionIds', body)
    def test_widget_timers_and_text_body(self):
        self.assertIn('duration={widget.durationSeconds||activity.duration_seconds||30}', SRC)
        self.assertIn('projection-text-widget', SRC)
        self.assertIn('.projection-interactive-widget{', CSS)

if __name__ == '__main__': unittest.main()
