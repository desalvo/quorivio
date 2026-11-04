"""RC178: reject the desktop fixed-row clipping that RC171 wrapping exposed."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf-8')
BROWSER = (ROOT / 'tools/ci_editor_mock_layout_chromium.py').read_text(encoding='utf-8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')


def current_catalog_css(css: str) -> str:
    """Only the newest release rules can override the immutable old CSS."""
    return css.split('/* RC178: let the palette row follow its real, bounded wrapped content.', 1)[-1]


class WrappedPaletteAcceptance(unittest.TestCase):
    def test_current_auto_row_follows_bounded_wrapped_catalog(self):
        rules = current_catalog_css(CSS)
        self.assertNotEqual(rules, CSS, 'RC178 effective cascade missing')
        self.assertIn('grid-template-rows:78px minmax(72px,auto) minmax(0,1fr)!important', rules)
        self.assertIn('grid-template-rows:minmax(130px,auto) minmax(72px,auto) minmax(0,1fr)!important', rules)
        self.assertIn('max-width:min(100%,calc((100dvh - 240px)*16/9))!important', rules)
        self.assertIn('overflow-x:hidden!important;overflow-y:auto!important', CSS)

    def test_broken_fixed_palette_regression_fails_closed(self):
        broken = CSS.split('/* RC178: let the palette row follow its real, bounded wrapped content.', 1)[0]
        self.assertEqual(current_catalog_css(broken), broken)
        self.assertNotIn('grid-template-rows:78px minmax(72px,auto)', broken)
        self.assertIn('grid-template-rows:78px 80px minmax(0,1fr)!important', broken)

    def test_browser_asserts_last_widget_is_reachable_not_legacy_horizontal_scroll(self):
        for needle in ("overflow['overflowY']=='auto'", "overflow['flexWrap']=='wrap'",
                       "overflow['scrollWidth']<=overflow['clientWidth']+3",
                       "last['y']+last['height']<=gb['y']+gb['height']+2"):
            self.assertIn(needle, BROWSER)
        self.assertNotIn('scrollLeft', BROWSER)
        self.assertIn('python3 tools/ci_editor_mock_layout_chromium.py', CI)
        self.assertIn('tools.tests.test_rc178_palette_clipping', CI)


if __name__ == '__main__':
    unittest.main()
