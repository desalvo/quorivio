"""Guard against canvas rows intercepting the sole Exit action in autosave-only editor."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf-8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
BROWSER = (ROOT / 'tools/ci_editor_save_flow_chromium.py').read_text(encoding='utf-8')
POSTGRES = (ROOT / 'tools/ci_browser_editor_postgres.py').read_text(encoding='utf-8')


class CanvasSaveFlow(unittest.TestCase):
    def test_canvas_can_scroll_with_expanded_accessibility_controls(self):
        self.assertIn('.editor-ux-v2 .editor-canvas-slot{position:relative;display:grid;place-items:center;flex:0 0 auto;', CSS)
        self.assertIn('.editor-ux-v2 .editor-stage{display:flex;flex-direction:column;', CSS)
        self.assertIn('overflow:auto;scrollbar-color:', CSS)

    def test_bottom_and_secondary_save_controls_cannot_shrink_under_canvas(self):
        self.assertIn('.editor-ux-v2 .editor-bottom-controls{display:none!important}', CSS)
        self.assertIn('.editor-ux-v2 .editor-mock-header{', CSS)

    def test_preflight_is_real_chromium_and_uses_same_save_locator_as_pg(self):
        self.assertIn('python3 tools/ci_editor_save_locator_chromium.py',CI)
        self.assertIn('Expanded canvas accessibility controls intercept the Exit button',BROWSER)
        self.assertIn('async def await_revision(',POSTGRES)
        self.assertIn('await await_revision(context,sid,aid,3)',POSTGRES)
        self.assertIn('setPageSavePending(true)',(ROOT/'apps/web/src/main.tsx').read_text())

    def test_ci_checks_layout_before_other_chromium_flows(self):
        self.assertIn('python3 tools/ci_editor_save_flow_chromium.py', CI)
        self.assertLess(CI.index('python3 tools/ci_editor_save_flow_chromium.py'), CI.index('python3 tools/ci_browser_editor.py'))
        self.assertLess(CI.index('python3 tools/ci_editor_save_flow_chromium.py'), CI.index('python3 tools/ci_browser_editor_postgres.py'))


if __name__ == '__main__':
    unittest.main()
