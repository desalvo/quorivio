"""Chromium 40385480205: contextual controls must be reopened before use.

The actual editor hides selection controls whenever the canvas context menu is
closed. The integration suite must use the same user-visible entry point and
must not rely on a toolbar remaining open across undo, selection or paste.
"""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[2]
BROWSER = (ROOT / 'tools/ci_browser_editor.py').read_text(encoding='utf-8')
POSTGRES = (ROOT / 'tools/ci_browser_editor_postgres.py').read_text(encoding='utf-8')
HELPER = (ROOT / 'tools/ci_editor_context_tools.py').read_text(encoding='utf-8')
WEB = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf-8')
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf-8')


class ContextualChromiumGate(unittest.TestCase):
    def test_canvas_tools_are_contextual_in_actual_app(self):
        self.assertIn('data-tools-open={backgroundMenu}', WEB)
        self.assertIn('setBackgroundMenu(v=>!v)', WEB)
        self.assertIn('.editor-ux-v2 .canvas-editor-tools{display:none!important}', CSS)
        self.assertIn('.editor-ux-v2 .canvas-editor-group[data-tools-open=true]>.canvas-editor-tools', CSS)

    def test_browser_opens_real_context_before_hidden_commands(self):
        parsed = ast.parse(HELPER)
        fns = {n.name: n for n in parsed.body if isinstance(n, ast.AsyncFunctionDef)}
        self.assertIn('ensure_canvas_tools_open', fns)
        self.assertIn('click_canvas_tool', fns)
        ensure = ast.get_source_segment(HELPER, fns['ensure_canvas_tools_open'])
        click = ast.get_source_segment(HELPER, fns['click_canvas_tool'])
        self.assertIn('if not await group.is_visible()', ensure)
        self.assertIn("name='Apri menu contestuale canvas, sfondi e proprietà pagina'", ensure)
        self.assertIn('await trigger.click()', ensure)
        self.assertIn('await expect(group).to_be_visible()', ensure)
        self.assertIn('await ensure_canvas_tools_open(page)', click)
        self.assertIn('await expect(control).to_be_visible()', click)
        self.assertIn('await expect(control).to_be_enabled()', click)
        self.assertIn('await control.click()', click)
        self.assertNotIn('force=True', click + ensure)

    def test_all_selection_actions_reenter_context_on_desktop_and_touch(self):
        for label in ('Sinistra', 'Copia selezione', 'Incolla selezione',
                      'Porta selezione davanti', 'Sposta selezione a destra',
                      'Duplica selezione', 'Elimina selezione'):
            self.assertIn(f"await click_canvas_tool(page,'{label}')", BROWSER)
        self.assertIn("await click_canvas_tool(mobile,'Sposta selezione a sinistra')", BROWSER)
        self.assertNotIn("page.get_by_role('button',name='Porta selezione davanti').click()", BROWSER)
        self.assertIn('await expect(selection).to_be_hidden()', BROWSER)
        self.assertIn('await ensure_canvas_tools_open(page)', BROWSER)
        self.assertIn('await ensure_canvas_tools_open(mobile)', BROWSER)
        self.assertIn('from ci_editor_context_tools import ensure_canvas_tools_open, click_canvas_tool', BROWSER)
        self.assertIn('from ci_editor_context_tools import ensure_canvas_tools_open, click_canvas_tool, close_canvas_tools', POSTGRES)
        self.assertGreaterEqual(POSTGRES.count('await close_canvas_tools(page)'), 2)
        self.assertGreaterEqual(POSTGRES.count("await click_canvas_tool(page,'Sposta selezione a destra')"), 2)
        self.assertNotIn("page.get_by_role('button',name='Sposta selezione a destra').click()", POSTGRES)

    def test_clipboard_actions_reuse_sibling_contextual_controls(self):
        # The align group does not contain clipboard tools; they are siblings.
        fns = {n.name: n for n in ast.parse(HELPER).body if isinstance(n, ast.AsyncFunctionDef)}
        click = ast.get_source_segment(HELPER, fns['click_canvas_tool'])
        self.assertIn("control=page.get_by_role('button',name=name,exact=True)", click)
        self.assertNotIn("control=group.get_by_role", click)


if __name__ == '__main__':
    unittest.main()
