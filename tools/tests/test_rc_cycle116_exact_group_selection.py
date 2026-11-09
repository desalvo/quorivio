"""RC116 Chromium group-duplication selection contract (run 41328071305)."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
BROWSER=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def safe_selection(source: str) -> bool:
    return all(value in source for value in (
        'async def select_exact_widget_pair(page):',
        "await checkbox.set_checked(label in wanted)",
        "wanted={'First','Second'}",
        "set(selected_ids)=={'widget-a','widget-b'}",
        'len(checked_rows)==2',
        "await expect(page.locator('.widget-canvas-item[data-selected=\"true\"]')).to_have_count(2)",
    )) and 'await checks.nth(0).check();await checks.nth(1).check()' not in source

class GroupSelectionAcceptance(unittest.TestCase):
    def test_exact_pair_is_verified_in_both_accessibility_and_canvas(self):
        self.assertTrue(safe_selection(BROWSER))
    def test_exact_selection_is_reused_for_group_actions(self):
        self.assertEqual(BROWSER.count('await select_exact_widget_pair(page)'),3)
        self.assertIn("await click_canvas_tool(page,'Duplica selezione')",BROWSER)
        self.assertIn("await click_canvas_tool(page,'Elimina selezione')",BROWSER)
    def test_does_not_weaken_real_browser_expectations(self):
        self.assertIn("to_have_count(5)",BROWSER)
        self.assertIn("to_have_count(1)",BROWSER)
        self.assertIn("deletion_confirmations==[('confirm','Eliminare 2 widget selezionati?')]",BROWSER)
        self.assertIn("dialog.dismiss()",BROWSER)
    def test_negative_mutations(self):
        self.assertFalse(safe_selection(BROWSER.replace('await checkbox.set_checked(label in wanted)','await checkbox.check()',1)))
        self.assertFalse(safe_selection(BROWSER.replace('len(checked_rows)==2','len(checked_rows)>=2',1)))
        self.assertFalse(safe_selection(BROWSER.replace("set(selected_ids)=={'widget-a','widget-b'}","len(selected_ids)>=2",1)))
    def test_mandatory_browser_gate_and_preflight(self):
        self.assertIn('test_rc_cycle116_exact_group_selection',WORKFLOW)
        self.assertLess(WORKFLOW.index('test_rc_cycle116_exact_group_selection'),WORKFLOW.index('npm ci --ignore-scripts'))
        self.assertIn('python3 tools/ci_browser_editor.py',WORKFLOW)
        self.assertIn('python3 tools/verify_rc_cycle116_inventory.py',WORKFLOW)

if __name__=='__main__':unittest.main()
