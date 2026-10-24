from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'apps/web/src/main.tsx').read_text()
CLIPBOARD = (ROOT / 'apps/web/src/widget-clipboard.ts').read_text()

class CanvasCloneAndQuizFallback(unittest.TestCase):
    def test_duplicate_copies_nested_configuration_independently(self):
        self.assertIn('structuredClone(source)', CLIPBOARD)
        self.assertIn('onChange([...widgets,copy]);setActive(copy.id)', SOURCE)

    def test_old_answer_key_used_if_new_list_empty(self):
        self.assertIn('selectedQuestion.correctOptionIds?.length?selectedQuestion.correctOptionIds:[selectedQuestion.correctOptionId]', SOURCE)
        self.assertNotIn('selectedQuestion.correctOptionIds||[selectedQuestion.correctOptionId]', SOURCE)

    def test_duplicate_position_remains_nonnegative(self):
        self.assertIn('Math.max(0,Math.min(100-width', CLIPBOARD)
        self.assertIn('Math.max(0,Math.min(100-height', CLIPBOARD)
