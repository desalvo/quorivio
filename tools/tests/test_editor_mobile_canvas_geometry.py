"""Keep mobile authoring coordinates aligned with persisted canvas geometry."""
from pathlib import Path
import unittest

CSS = (Path(__file__).resolve().parents[2] / 'apps/web/src/style.css').read_text()

class MobileCanvasGeometryTest(unittest.TestCase):
    def test_mobile_authoring_does_not_reflow_widgets(self):
        rule = CSS.split('/* Mobile authoring: retain the stored 16:9 coordinate system.', 1)[1]
        self.assertIn('.powerpoint-editor .canvas-with-rulers .widget-canvas-item', rule)
        self.assertIn('position: absolute !important', rule)
        self.assertIn('aspect-ratio: 16 / 9', rule)
        self.assertIn('min-width: 600px', rule)
        self.assertIn('overflow-x: auto', rule)
    def test_mobile_keyboard_alternatives_are_touch_sized(self):
        rule = CSS.split('/* Mobile authoring: retain the stored 16:9 coordinate system.', 1)[1]
        self.assertIn('.powerpoint-editor .canvas-accessible-row button', rule)
        self.assertIn('min-height: 44px', rule)

if __name__ == '__main__':
    unittest.main()
