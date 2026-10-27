from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=(ROOT/'apps/web/src/main.tsx').read_text()

class WidgetQuestionEditorRegression(unittest.TestCase):
    def test_integrated_editor_has_one_inspector_only(self):
        self.assertIn('contextWidget&&!onInspectWidget&&<div className="canvas-context-properties">', SOURCE)
        self.assertIn('contextWidget===w.id&&<div className="canvas-context-menu"', SOURCE)
        self.assertIn('editor-widget-drawer',SOURCE)
        self.assertIn('aria-label="Chiudi proprietà widget"',SOURCE)
    def test_question_modes(self):
        self.assertIn('Modalità risposta widget',SOURCE)
        self.assertIn('<option value="multiple">',SOURCE)
    def test_timed_quiz_duration_and_correct_options(self):
        self.assertIn('Durata (secondi, 5–600)',SOURCE)
        self.assertIn('correctOptionIds:ids',SOURCE)
    def test_option_limit_and_ids(self):
        self.assertIn('length>=12',SOURCE)
        self.assertIn("crypto.randomUUID().replace(/-/g,'').slice(0,24)",SOURCE)

if __name__=='__main__': unittest.main()
