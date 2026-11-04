"""RC180: stage contextual controls and insertion rail must coexist.

Run 41913987787 proved the RC179 stage-wide z-index workaround blocked
"Linee" after "Duplica selezione" became accessible. Require non-overlapping
flow geometry and genuine Playwright pointer hit-testing before full editor E2E.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
BROWSER = (ROOT / 'tools/ci_rc180_editor_palette_context_coexist_chromium.py').read_text(encoding='utf8')


class ContextRailCoexistence(unittest.TestCase):
    def test_context_panels_dock_inside_stage_not_above_rail(self):
        self.assertIn('/* RC180', CSS)
        patch = CSS.split('/* RC180', 1)[1]
        stage = re.search(r'\.editor-stage:has\(\.canvas-editor-group\[data-tools-open="true"\]\)\s*\{([^}]+)\}', patch)
        self.assertIsNotNone(stage)
        self.assertIn('z-index:1!important', stage.group(1))
        self.assertIn('align-items:stretch!important', stage.group(1))
        self.assertIn('position:relative!important', patch)
        self.assertIn('inset:auto!important', patch)
        self.assertIn('top:auto!important', patch)
        self.assertIn('max-height:min(126px,23dvh)!important', patch)

    def test_new_native_chromium_gate_runs_before_authenticated_editor(self):
        browser = 'python3 tools/ci_rc180_editor_palette_context_coexist_chromium.py'
        full = 'python3 tools/ci_browser_editor.py'
        self.assertIn(browser, WORKFLOW)
        self.assertIn('tools.tests.test_rc180_editor_rail_context_docking', WORKFLOW)
        self.assertLess(WORKFLOW.index(browser), WORKFLOW.index(full))
        self.assertIn('document.elementFromPoint(x,y)', BROWSER)
        self.assertIn('await control.click(timeout=3000)', BROWSER)
        self.assertIn("('line', line)", BROWSER)
        self.assertIn("('duplicate', duplicate)", BROWSER)
        self.assertIn("('align', align)", BROWSER)
        self.assertNotIn('force=True', BROWSER)
        self.assertNotIn('dispatch_event(', BROWSER)

    def test_rc179_was_making_only_one_side_of_rail_clickable(self):
        earlier = CSS.split('/* RC180', 1)[0]
        self.assertRegex(earlier, r'\.editor-stage:has\(\.canvas-editor-group\[data-tools-open="true"\]\)')
        self.assertIn('z-index:70!important', earlier)
        self.assertNotIn('inset:auto!important', earlier.split('/* RC179: the wrapped insertion palette', 1)[-1])


if __name__ == '__main__':
    unittest.main()
