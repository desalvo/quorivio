"""Protect the canvas inspector from leaking selection across pages."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'apps/web/src/main.tsx').read_text()

class EditorPageIsolationTests(unittest.TestCase):
    def test_canvas_has_page_identity(self):
        self.assertIn('<WidgetCanvas key={`${selected}:${designActivity}`}', SOURCE)

    def test_inspector_cleared_for_removed_widgets(self):
        self.assertIn('if(active&&!widgets.some(w=>w.id===active))setActive(null)', SOURCE)
        self.assertIn('if(editing&&!widgets.some(w=>w.id===editing))setEditing(null)', SOURCE)
        self.assertIn('if(contextWidget&&!widgets.some(w=>w.id===contextWidget))setContextWidget(null)', SOURCE)

if __name__ == '__main__':
    unittest.main()
