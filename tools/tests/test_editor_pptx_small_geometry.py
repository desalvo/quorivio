"""Regression: canvas resizing must retain tiny PPTX shapes, including keyboard resize."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'apps/web/src/main.tsx').read_text()

class EditorSmallGeometryRegression(unittest.TestCase):
    def test_pointer_minimums_match_importer(self):
        self.assertIn('width+dx,0.01,100-x', SOURCE)
        self.assertIn('height+dy,0.01,100-y', SOURCE)
        self.assertIn('snap(width),0.01', SOURCE)
        self.assertIn('snap(height),0.01', SOURCE)

    def test_keyboard_minimums_match_pointer(self):
        self.assertIn('position.width+direction,0.01,100-position.x', SOURCE)
        self.assertIn('position.height+direction,0.01,100-position.y', SOURCE)

    def test_editable_text_keeps_arrow_keys(self):
        self.assertIn("closest('input,textarea,button,select,[contenteditable=true]')", SOURCE)

if __name__ == '__main__':
    unittest.main()
