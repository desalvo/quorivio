"""Regression for run 40392423273: nested layer controls stayed CSS-hidden."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
WEB=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
BROWSER=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf-8')
HELPER=(ROOT/'tools/ci_editor_context_tools.py').read_text(encoding='utf-8')
SMOKE=(ROOT/'tools/ci_nested_context_css_chromium.py').read_text(encoding='utf-8')

class NestedCanvasContextRegression(unittest.TestCase):
    def test_editor_layer_controls_are_nested(self):
        self.assertIn('aria-label="Allineamento widget selezionati"',WEB)
        self.assertIn('aria-label="Ordine e spostamento widget selezionati"',WEB)
        self.assertIn('Porta selezione davanti',WEB)

    def test_context_remains_hidden_until_open(self):
        self.assertIn('.editor-ux-v2 .canvas-editor-tools{display:none!important}',CSS)
        self.assertRegex(CSS,r'\.editor-ux-v2 \.canvas-editor-group\[data-tools-open=true\]>.canvas-editor-tools\{display:flex!important')

    def test_nested_controls_display_only_inside_open_context(self):
        # CSS selector must be more specific than display:none!important, and
        # its scope must require an open canvas menu.
        self.assertRegex(CSS,r'\.editor-ux-v2 \.canvas-editor-group\[data-tools-open=true\]>.canvas-editor-tools \.canvas-editor-tools\{display:flex!important')
        self.assertNotIn('.editor-ux-v2 .canvas-editor-tools .canvas-editor-tools{display:flex!important',CSS)

    def test_actual_chromium_asserts_nested_group_before_actions(self):
        self.assertIn("layer_group=page.get_by_role('group',name='Ordine e spostamento widget selezionati')",BROWSER)
        self.assertIn('await expect(layer_group).to_be_visible()',BROWSER)
        self.assertIn("await expect(group.get_by_role('group',name='Ordine e spostamento widget selezionati')).to_be_visible()",HELPER)
        self.assertNotIn('force=True',HELPER)

    def test_independent_browser_css_smoke_includes_mouse_and_touch(self):
        self.assertIn("await verify(browser,width=1440,height=1000,touch=False)",SMOKE)
        self.assertIn("await verify(browser,width=390,height=844,touch=True)",SMOKE)
        self.assertIn("await expect(front).to_be_hidden()",SMOKE)
        self.assertIn("await expect(front).to_be_visible()",SMOKE)
        self.assertIn('front.click()',SMOKE)
        self.assertIn('front.tap()',SMOKE)

if __name__=='__main__':unittest.main()
