"""RC218: real PostgreSQL Chromium rename must follow the RC206 thumbnail labels.

The preflight deliberately covers the *real browser script* and the editor's
selection-aware menu source. This prevents a stale exact-name selector from
wasting an expensive Chromium/PostgreSQL run.
"""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = 'tools/ci_browser_editor_postgres.py'
APP_PATH = 'apps/web/src/main.tsx'
WF_PATH = '.github/workflows/ci.yml'
SCRIPT = (ROOT / SCRIPT_PATH).read_text(encoding='utf8')
APP = (ROOT / APP_PATH).read_text(encoding='utf8')
WORKFLOW = (ROOT / WF_PATH).read_text(encoding='utf8')


# Strictly limit the page action name, not the unrelated "Rinomina pagina"
# button in the canvas background context menu. Also accept multi-selection.
RENAME_PATTERN = r"^Rinomina (?:pagina|pagine selezionate) \(R\)$"


def verify_contract(script: str, app: str, workflow: str) -> None:
    ast.parse(script, filename=SCRIPT_PATH)
    required_browser = (
        "name='Menu pagina 1: crea, duplica, elimina, sposta'",
        "actions=page.get_by_role('group',name='Azioni pagina 1',exact=True)",
        "await expect(actions).to_be_visible()",
        "rename=actions.get_by_role('button',name=re.compile(r'" + RENAME_PATTERN + "'))",
        "await expect(rename).to_have_count(1)",
        "await rename.click()",
        "dialog.accept('Renamed browser slide')",
        "assert renamed_activity['title']=='Renamed browser slide'",
        "assert renamed_activity['design_revision']==3",
        "assert renamed_activity['options']==[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]",
        "assert renamed_activity['page_design']['widgets'][0]['position']['x']==11",
    )
    for token in required_browser:
        if token not in script:
            raise AssertionError('real Chromium rename contract missing: ' + token)
    if "get_by_role('button',name='Rinomina pagina',exact=True)" in script:
        raise AssertionError('obsolete exact-match selector in the real browser')
    required_ui = (
        "role=\"group\" aria-label={`Azioni pagina ${i+1}`}",
        "Rinomina {selectedPageIds.length>1?'pagine selezionate':'pagina'} (R)",
        "void renameSelectedPages(a.id)",
        "setSelectedPageIds(current=>current.includes(id)?current:[id])",
        "if(page)await renameCanvasPage(page)",
    )
    for token in required_ui:
        if token not in app:
            raise AssertionError('editor thumbnail menu contract missing: ' + token)
    if ("tools.tests.test_rc218_browser_postgres_thumbnail_rename" not in workflow or
        "python3 tools/ci_browser_editor_postgres.py" not in workflow):
        raise AssertionError('early preflight or real PostgreSQL Chromium acceptance missing')
    if workflow.index('tools.tests.test_rc218_browser_postgres_thumbnail_rename') > workflow.index('npm install --ignore-scripts'):
        raise AssertionError('preflight must occur before npm/PostgreSQL acceptance')


class RC218RealEditorThumbnailRename(unittest.TestCase):
    def test_current_real_browser_selector_and_title_only_persistence(self):
        verify_contract(SCRIPT, APP, WORKFLOW)

    def test_accessible_name_patterns_accept_single_and_group_labels(self):
        import re
        pattern = re.compile(RENAME_PATTERN)
        for good in ('Rinomina pagina (R)', 'Rinomina pagine selezionate (R)'):
            self.assertIsNotNone(pattern.fullmatch(good))
        for wrong in ('Rinomina pagina', 'Rinomina pagine', 'Elimina pagina (Backspace)',
                      'Rinomina pagina (D)', 'Rinomina pagine selezionate (Backspace)'):
            self.assertIsNone(pattern.fullmatch(wrong))

    def test_negative_mutations_reject_wrong_menu_and_unverified_persistence(self):
        for old, new in (
            ("actions=page.get_by_role('group',name='Azioni pagina 1',exact=True)",
             "actions=page.get_by_role('group',name='Menu contestuale sfondo canvas',exact=True)"),
            ("await expect(rename).to_have_count(1)", "await expect(rename).to_have_count(0)"),
            ("await rename.click()", "await page.keyboard.press('Escape')"),
            ("assert renamed_activity['title']=='Renamed browser slide'", "assert renamed_activity is not None"),
        ):
            self.assertIn(old, SCRIPT)
            with self.subTest(old=old), self.assertRaises(AssertionError):
                verify_contract(SCRIPT.replace(old, new, 1), APP, WORKFLOW)
        with self.assertRaises(AssertionError):
            verify_contract(SCRIPT, APP.replace('void renameSelectedPages(a.id)', 'void 0', 1), WORKFLOW)
        with self.assertRaises(AssertionError):
            verify_contract(SCRIPT, APP, WORKFLOW.replace('tools.tests.test_rc218_browser_postgres_thumbnail_rename', 'deleted', 1))


if __name__ == '__main__':
    unittest.main()
