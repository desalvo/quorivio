"""Regression for pointer events and mobile canvas geometry."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]

class EditorMobilePointerCss(unittest.TestCase):
    def test_mobile_canvas_retains_pointer_capture(self):
        css = (ROOT / 'apps/web/src/style.css').read_text()
        self.assertRegex(css, r'(?s)@media \(max-width: 700px\)\s*\{\s*\.powerpoint-editor \.canvas-with-rulers \.widget-canvas-item\s*\{\s*touch-action:\s*none;')
        self.assertRegex(css, r'(?s)\.powerpoint-editor \.canvas-with-rulers \.widget-canvas\s*\{\s*overflow:\s*visible;\s*min-height:\s*0;')
    def test_pointer_events_restricted_to_active_pointer(self):
        source = (ROOT / 'apps/web/src/main.tsx').read_text()
        self.assertIn('g.pointerId!==e.pointerId', source)
        self.assertIn('setPointerCapture(e.pointerId)', source)

if __name__ == '__main__':
    unittest.main()
