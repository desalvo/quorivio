"""Guard against CI 40513571247: canvas accessible rows occluding Save."""
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
        self.assertIn('.editor-ux-v2 .editor-bottom-controls{flex:0 0 auto;display:flex;', CSS)
        self.assertIn('.editor-ux-v2 .editor-secondary-workflow{flex:0 0 auto;width:100%;', CSS)

    def test_preflight_is_real_chromium_and_uses_same_save_locator_as_pg(self):
        self.assertIn('from ci_editor_context_tools import editor_save_button', BROWSER)
        self.assertIn('editor_save_button(page)', POSTGRES)
        self.assertIn('editor_save_button(page)', BROWSER)
        self.assertIn('document.elementFromPoint', BROWSER)
        self.assertIn('await save.click()', BROWSER)
        self.assertIn('await save.tap()', BROWSER)
        self.assertIn('Porta in primo piano Third', BROWSER)
        self.assertNotIn('force=True', BROWSER)
        self.assertNotIn('dispatch_event', BROWSER)

    def test_ci_checks_layout_before_other_chromium_flows(self):
        self.assertIn('python3 tools/ci_editor_save_flow_chromium.py', CI)
        self.assertLess(CI.index('python3 tools/ci_editor_save_flow_chromium.py'), CI.index('python3 tools/ci_browser_editor.py'))
        self.assertLess(CI.index('python3 tools/ci_editor_save_flow_chromium.py'), CI.index('python3 tools/ci_browser_editor_postgres.py'))


if __name__ == '__main__':
    unittest.main()
