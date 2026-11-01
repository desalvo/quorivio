"""Static regressions preventing ambiguous Chromium Save selectors."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'tools'

class EditorSaveLocatorStrict(unittest.TestCase):
    def test_helper_uses_explicit_exact_accessible_name_and_editor_scope(self):
        source=(TOOLS/'ci_editor_context_tools.py').read_text()
        self.assertIn('async def wait_for_editor_sync(page',source)
        self.assertIn("'Salvato automaticamente'",source)
        self.assertNotIn('def editor_save_button(',source)
        self.assertNotIn('.click(force=True)',source)

    def test_both_browser_acceptance_flows_use_same_exact_save_locator(self):
        for name in ('ci_browser_editor.py','ci_browser_editor_postgres.py'):
            with self.subTest(name=name):
                source=(TOOLS/name).read_text()
                ast.parse(source)
                self.assertNotIn('editor_save_button(page)',source)
                self.assertNotIn("get_by_role('button',name='Salva layout')",source)
                self.assertIn('autosave' if name=='ci_browser_editor.py' else 'await_revision',source.lower())

    def test_real_browser_preflight_checks_collision_and_touch(self):
        source=(TOOLS/'ci_editor_save_locator_chromium.py').read_text(encoding='utf-8')
        ast.parse(source)
        for expected in ('await verify(browser,touch=True)','await verify(browser,touch=False)',
                         "get_by_role('status')", "Salva ora"):
            self.assertIn(expected,source)

    def test_opt_in_ci_runs_collision_preflight_before_editor(self):
        source=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('python3 tools/ci_editor_save_locator_chromium.py',source)
        self.assertLess(source.index('python3 tools/ci_editor_save_locator_chromium.py'),
                        source.index('python3 tools/ci_browser_editor.py'))

if __name__=='__main__':unittest.main()
