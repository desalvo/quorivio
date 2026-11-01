"""RC41 contract tests: persisted visual themes without bypassing authored media/opacity."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ArtisticWidgetContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.domain = (ROOT / 'apps/api/src/domain.ts').read_text()
        cls.ui = (ROOT / 'apps/web/src/main.tsx').read_text()
        cls.css = (ROOT / 'apps/web/src/style.css').read_text()
        cls.helper = (ROOT / 'apps/web/src/widget-art.ts').read_text()

    def test_persisted_allowlisted_art_config(self):
        for token in ["artTheme?:'studio'|'glass'|'playful'|'minimal'", "artEffect?:'none'|'float'|'glow'|'tilt'", "v.artTheme===undefined", "v.artEffect===undefined"]:
            self.assertIn(token, self.domain)

    def test_identical_style_data_on_all_surfaces(self):
        self.assertEqual(self.ui.count('{...widgetArtData(w.style)}'), 4)
        for token in ['className="projection-widget"', 'className={\'rehearsal-widget rehearsal-\'+kind}', 'className={`page-widget widget-', 'className={\'widget-canvas-item ']:
            self.assertIn(token,self.ui)

    def test_explicit_fills_are_never_forced(self):
        self.assertIn('widgetHasAuthoredFill',self.helper)
        self.assertIn('data-art-custom-fill',self.helper)
        self.assertIn('data-art-custom-fill="true"',self.css)
        self.assertRegex(self.css,r'not\(\[data-art-custom-fill="true"\]\)')

    def test_art_controls_and_accessibility(self):
        self.assertIn('Tema artistico del widget',self.ui)
        self.assertIn('Effetto artistico del widget',self.ui)
        self.assertIn('widget-timer-design-preview',self.ui)
        self.assertIn('prefers-reduced-motion:reduce',self.css)
        self.assertIn('data-art-effect="tilt"',self.css)
        self.assertIn('data-art-theme="minimal"',self.css)


if __name__ == '__main__':
    unittest.main()
