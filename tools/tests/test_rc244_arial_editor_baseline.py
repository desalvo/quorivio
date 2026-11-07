"""RC244: prevent inherited application DM Sans leaking into new editor widget text.

The old RC242 Chromium fixture assigned Arial inline on every test widget,
which hid the absence of a default Arial root on the real slide-master canvas.
"""
from __future__ import annotations

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CSS = ROOT / 'apps/web/src/style.css'
CHROMIUM = ROOT / 'tools/ci_rc242_arial_zoom_chromium.py'
THUMBNAILS = ROOT / 'tools/ci_rc224_thumbnail_menu_chromium.py'
WORKFLOW = ROOT / '.github/workflows/ci.yml'


def require_arial_root(css: str, fixture: str) -> None:
    # An explicit root default is required. A rule on *descendants* using
    # `inherit` cannot repair DM Sans inherited by the widget container.
    pattern = (r':is\(\.editor-ux-v2,\.slide-scheme-workspace,\.powerpoint-editor\)'
               r'\s+\.widget-canvas-item\s*\{\s*font-family:Arial,sans-serif;\s*\}')
    assert re.search(pattern, css), 'new widget containers must start with Arial'
    assert '.widget-canvas-item .widget-fit-content{\n font-family:inherit;' in css
    # Never hide a missing default by painting every fixture widget Arial inline.
    assert 'data-widget-kind="{kind}" style="font-family:Arial' not in fixture
    assert 'id="default-widget" style="font-family:Arial' not in fixture
    # User-saved font overrides must stay intact (inline > default stylesheet).
    assert 'font-family:Georgia' in fixture and 'font-family:Verdana' in fixture
    assert 'len(KINDS)*2*4' in fixture


class RC244ArialEditorBaseline(unittest.TestCase):
    def test_actual_canvas_roots_and_unbiased_chromium_fixtures(self):
        require_arial_root(CSS.read_text(), CHROMIUM.read_text())
        menu = THUMBNAILS.read_text()
        self.assertIn('all(\'Arial\' in font for font in stats[\'fonts\'])', menu)
        self.assertIn('320,240', menu)

    def test_negative_regression_rejects_css_root_inheriting_dm_sans(self):
        css = CSS.read_text()
        fixture = CHROMIUM.read_text()
        mutated = css.replace('.widget-canvas-item{\n font-family:Arial,sans-serif;\n}',
                              '.widget-canvas-item{\n font-family:inherit;\n}', 1)
        self.assertNotEqual(mutated, css)
        with self.assertRaises(AssertionError):
            require_arial_root(mutated, fixture)

    def test_negative_regression_rejects_inline_arial_in_test_fixture(self):
        fixture = CHROMIUM.read_text()
        mutated = fixture.replace('data-widget-kind="{kind}"',
                                  'data-widget-kind="{kind}" style="font-family:Arial,sans-serif"')
        self.assertNotEqual(mutated, fixture)
        with self.assertRaises(AssertionError):
            require_arial_root(CSS.read_text(), mutated)

    def test_mandatory_early_and_real_chromium_gates_remain(self):
        workflow = WORKFLOW.read_text()
        self.assertIn('python3 -m unittest tools.tests.test_rc244_arial_editor_baseline -q',workflow)
        self.assertIn('python3 tools/ci_rc224_thumbnail_menu_chromium.py',workflow)
        self.assertIn('python3 tools/ci_rc242_arial_zoom_chromium.py',workflow)
        self.assertIn('./node_modules/.bin/tsc --noEmit -p apps/web/tsconfig.json',workflow)
        self.assertIn('python3 tools/verify_rc_cycle243_inventory.py --historical',workflow)
        self.assertIn('python3 tools/verify_rc_cycle244_inventory.py',workflow)


if __name__ == '__main__':
    unittest.main()
