"""RC234: browser and style guard for the RC233 narrow editor overflow."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSS = ROOT / 'apps/web/src/style.css'
WORKFLOW = ROOT / '.github/workflows/ci.yml'
BROWSER = ROOT / 'tools/ci_rc234_palette_chromium.py'


def assert_mobile_palette_wrapped(css: str) -> None:
    marker = '/* RC234: preserve the RC171 wrapped, vertically scrollable widget palette'
    start = css.find(marker)
    if start < 0:
        raise AssertionError('RC234 mobile widget palette override missing')
    mobile = css[start:css.find('body .editor-ux-v2 .page-editor-sidebar', start)]
    rules = re.search(r'body \.editor-ux-v2 \.editor-widget-grid\s*\{([^}]+)\}', mobile)
    if not rules:
        raise AssertionError('RC234 narrow palette selector missing')
    props = rules.group(1)
    for prop, value in (
        ('flex-wrap', 'wrap'),
        ('overflow-x', 'hidden'),
        ('overflow-y', 'auto'),
        ('height', 'auto'),
    ):
        if not re.search(rf'\b{prop}:\s*{value}\s*!important', props):
            raise AssertionError(f'RC234 mobile widget palette must set {prop}: {value}')
    if 'max-height:min(30dvh,198px)!important' not in props:
        raise AssertionError('RC234 mobile widget palette height must be bounded')


class RC234PaletteResponsive(unittest.TestCase):
    def test_css_cannot_regress_to_unbounded_horizontal_strip(self):
        assert_mobile_palette_wrapped(CSS.read_text(encoding='utf8'))

    def test_no_wrap_and_horizontal_scroll_regressions_are_rejected(self):
        base = CSS.read_text(encoding='utf8')
        for original, mutated in (
            ('flex-wrap:wrap!important', 'flex-wrap:nowrap!important'),
            ('overflow-x:hidden!important', 'overflow-x:auto!important'),
            ('overflow-y:auto!important', 'overflow-y:hidden!important'),
        ):
            with self.subTest(original=original):
                marker = base.index('/* RC234: preserve')
                prefix, fragment = base[:marker], base[marker:]
                self.assertIn(original, fragment)
                with self.assertRaises(AssertionError):
                    assert_mobile_palette_wrapped(prefix + fragment.replace(original, mutated, 1))

    def test_browser_gate_is_mandatory_after_existing_rc171_acceptance(self):
        workflow = WORKFLOW.read_text(encoding='utf8')
        self.assertIn('python3 tools/ci_rc171_editor_palette_chromium.py', workflow)
        self.assertIn('python3 tools/ci_rc234_palette_chromium.py', workflow)
        self.assertLess(workflow.index('python3 tools/ci_rc171_editor_palette_chromium.py'),
                        workflow.index('python3 tools/ci_rc234_palette_chromium.py'))
        source = BROWSER.read_text(encoding='utf8')
        for width in ('320', '390', '620', '760', '761', '960', '1440'):
            self.assertIn(width, source)
        self.assertIn("last_visible", source)


if __name__ == '__main__':
    unittest.main()
