"""RC237: the rename action locator cannot be satisfied by export_actions.

Run this before dependency installation. It reproduces the GitHub 42256926397
false positive and keeps the original RC218 negative mutations effective.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from tools.tests.test_rc218_browser_postgres_thumbnail_rename import (
    APP, ROOT, SCRIPT, WORKFLOW, verify_contract,
)


class RC237RenameScopeGuard(unittest.TestCase):
    def test_positive_rename_and_export_remain_independent(self):
        self.assertIn("actions=page.get_by_role('group',name='Azioni pagina 1',exact=True)", SCRIPT)
        self.assertIn("export_actions=page.get_by_role('group',name='Azioni pagina 1',exact=True)", SCRIPT)
        verify_contract(SCRIPT, APP, WORKFLOW)

    def test_export_actions_substring_cannot_mask_missing_rename_scope(self):
        original = "actions=page.get_by_role('group',name='Azioni pagina 1',exact=True)"
        mutated = SCRIPT.replace(original,
            "actions=page.get_by_role('group',name='Menu contestuale sfondo canvas',exact=True)", 1)
        self.assertNotEqual(mutated, SCRIPT)
        # The precise CI failure: the old substring lookup still finds this
        # token as a suffix in `export_actions=...` despite mutation.
        self.assertIn(original, mutated)
        with self.assertRaisesRegex(AssertionError, 'scoped rename action group'):
            verify_contract(mutated, APP, WORKFLOW)

    def test_duplicate_rename_group_or_relabelled_export_not_accepted(self):
        # Reject a missing rename assignment even if *multiple* export paths
        # use a visually identical accessibility group.
        name = "actions=page.get_by_role('group',name='Azioni pagina 1',exact=True)"
        missing = SCRIPT.replace(name, "actions=page.get_by_role('group',name='Other actions',exact=True)", 1)
        missing += '\nexport_actions=page.get_by_role(\'group\',name=\'Azioni pagina 1\',exact=True)\n'
        with self.assertRaisesRegex(AssertionError, 'scoped rename action group'):
            verify_contract(missing, APP, WORKFLOW)

    def test_original_persistence_and_ci_guards_still_fail_closed(self):
        mutations = (
            (SCRIPT.replace("await rename.click()", "await page.keyboard.press('Escape')", 1), APP, WORKFLOW),
            (SCRIPT.replace("assert renamed_activity['title']=='Renamed browser slide'", "assert renamed_activity is not None", 1), APP, WORKFLOW),
            (SCRIPT, APP.replace('void renameSelectedPages(a.id)', 'void 0', 1), WORKFLOW),
        )
        for source, app, workflow in mutations:
            with self.subTest(source_changed=source != SCRIPT, app_changed=app != APP):
                with self.assertRaises(AssertionError):
                    verify_contract(source, app, workflow)

    def test_preflight_command_runs_before_npm(self):
        command = 'python3 -m unittest tools.tests.test_rc237_rename_scope_guard -q'
        self.assertIn(command, WORKFLOW)
        self.assertLess(WORKFLOW.index(command), WORKFLOW.index('npm ci --ignore-scripts'))
        self.assertIn('python3 -m unittest tools.tests.test_rc218_browser_postgres_thumbnail_rename -q', WORKFLOW)
        self.assertIn('python3 tools/ci_browser_editor_postgres.py', WORKFLOW)


if __name__ == '__main__':
    unittest.main()
