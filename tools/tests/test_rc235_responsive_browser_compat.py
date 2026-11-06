"""RC235: RC226 Chromium fixture must honor the accepted RC234 mobile layout.

Protect the historical studio checks without reintroducing horizontal palette
scrolling. This is a source-level preflight; the real-browser checks run later.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD_BROWSER = ROOT / 'tools/ci_rc226_responsive_studio_chromium.py'
NEW_BROWSER = ROOT / 'tools/ci_rc234_palette_chromium.py'
FORMAT_BROWSER = ROOT / 'tools/ci_rc143_format_phone_chromium.py'
EDITOR_BROWSER = ROOT / 'tools/ci_editor_mock_layout_chromium.py'
WORKFLOW = ROOT / '.github/workflows/ci.yml'


def verify_browser_contract(source: str) -> None:
    checks = (
        ('representative palette wrappers', '<span class="editor-icon-wrapper">'),
        ('wrapped palette', "view['paletteWrap']=='wrap'"),
        ('no horizontal overflow', "view['paletteFits']"),
        ('vertical overflow when needed', "view['paletteOverflowY']=='auto'"),
        ('scroll to the actual last tool', ".last.scroll_into_view_if_needed()"),
        ('last tool visible after scrolling', 'assert palette_last_reachable'),
        ('horizontal thumbnail navigation retained', "view['thumbnailsScrollable']"),
    )
    for label, fragment in checks:
        if fragment not in source:
            raise AssertionError('RC226/RC234 compatibility missing ' + label)
    if "view['paletteScrollable']" in source or 'palette.scrollWidth>palette.clientWidth' in source:
        raise AssertionError('RC226 obsolete horizontal palette expectation restored')


def verify_historical_fixtures(format_source: str, editor_source: str) -> None:
    # RC223 formatting switched to tabbed controls; CSS applies the responsive
    # overflow rules only to the real role=tabpanel element.
    if 'class="palette-ribbon-groups" role="tabpanel"' not in format_source:
        raise AssertionError('RC143 formatter must represent the real tabpanel')
    # RC226 moved the phone thumbnail filmstrip above the stage. A desktop-only
    # left-sidebar test must never be applied to that one-column layout.
    for fragment in (
        'if width<=760:',
        "tb['y']+tb['height']<=sb['y']+5",
        "abs(tb['width']-sb['width'])<=5",
        "rb['y']+rb['height']<=tb['y']+5",
        "tb['x']+tb['width']<=sb['x']+5",
        "overflow['flexWrap']=='wrap'",
        "overflow['scrollWidth']<=overflow['clientWidth']+3",
    ):
        if fragment not in editor_source:
            raise AssertionError('RC178 phone/desktop editor layout fixture missing: '+fragment)


class ResponsiveBrowserCompatibility(unittest.TestCase):
    def test_historical_browser_uses_current_mobile_contract(self):
        verify_browser_contract(OLD_BROWSER.read_text(encoding='utf8'))

    def test_regression_mutations_fail_closed(self):
        original = OLD_BROWSER.read_text(encoding='utf8')
        for fragment in (
            '<span class="editor-icon-wrapper">',
            "view['paletteWrap']=='wrap'",
            "view['paletteFits']",
            "view['paletteOverflowY']=='auto'",
            '.last.scroll_into_view_if_needed()',
            'assert palette_last_reachable',
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, original)
                with self.assertRaises(AssertionError):
                    verify_browser_contract(original.replace(fragment, '', 1))
        with self.assertRaises(AssertionError):
            verify_browser_contract(original + "\nview['paletteScrollable']\n")

    def test_historical_formatter_and_editor_use_real_current_structure(self):
        verify_historical_fixtures(FORMAT_BROWSER.read_text(encoding='utf8'),
                                   EDITOR_BROWSER.read_text(encoding='utf8'))

    def test_historical_layout_mutations_fail_closed(self):
        formatter = FORMAT_BROWSER.read_text(encoding='utf8')
        editor = EDITOR_BROWSER.read_text(encoding='utf8')
        with self.assertRaises(AssertionError):
            verify_historical_fixtures(formatter.replace('role="tabpanel"', 'role="group"', 1), editor)
        for marker in ('if width<=760:', "tb['y']+tb['height']<=sb['y']+5",
                       "tb['x']+tb['width']<=sb['x']+5"):
            with self.subTest(marker=marker), self.assertRaises(AssertionError):
                verify_historical_fixtures(formatter, editor.replace(marker, '', 1))

    def test_both_real_browser_acceptance_scripts_remain_mandatory(self):
        workflow = WORKFLOW.read_text(encoding='utf8')
        self.assertIn('python3 tools/ci_rc226_responsive_studio_chromium.py', workflow)
        self.assertIn('python3 tools/ci_rc143_format_phone_chromium.py', workflow)
        self.assertIn('python3 tools/ci_editor_mock_layout_chromium.py', workflow)
        self.assertIn('python3 tools/ci_rc234_palette_chromium.py', workflow)
        self.assertIn('python3 -m unittest tools.tests.test_rc235_responsive_browser_compat -q', workflow)
        self.assertLess(workflow.index('python3 tools/ci_rc226_responsive_studio_chromium.py'),
                        workflow.index('python3 tools/ci_rc234_palette_chromium.py'))
        self.assertTrue(NEW_BROWSER.is_file())
        self.assertIn('last_visible', NEW_BROWSER.read_text(encoding='utf8'))


if __name__ == '__main__':
    unittest.main()
