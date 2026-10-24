"""Contract regressions for authoring accessibility and accurate PPTX UI guidance."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AccessibilityAndPortabilityCopy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (ROOT / 'apps/web/src/style.css').read_text()
        cls.ui = (ROOT / 'apps/web/src/main.tsx').read_text()

    def test_keyboard_focus_and_reduced_motion(self):
        self.assertIn('.page-editor-thumb:focus-visible', self.css)
        self.assertIn('.audience-widget-layout input:focus-visible', self.css)
        self.assertIn('@media (prefers-reduced-motion: reduce)', self.css)
        self.assertIn('@media (forced-colors: active)', self.css)

    def test_mobile_page_controls_have_touch_targets(self):
        self.assertIn('.powerpoint-editor .page-editor-thumb-actions button', self.css)
        self.assertIn('min-height: 44px;', self.css)

    def test_pptx_import_guidance_reflects_real_support(self):
        self.assertIn('immagini PNG/JPEG e alcune forme semplici', self.ui)
        self.assertIn('SmartArt, animazioni e temi complessi', self.ui)
        self.assertNotIn('Immagini, animazioni, SmartArt e formattazioni complesse non vengono convertite', self.ui)


if __name__ == '__main__':
    unittest.main()
