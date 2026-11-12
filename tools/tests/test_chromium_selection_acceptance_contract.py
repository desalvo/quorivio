"""Guard the disabled-Deselect Chromium regression and CI diagnostic wiring."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

class ChromiumSelectionAcceptanceContract(unittest.TestCase):
    def test_browser_script_compiles_and_checks_undo_selection_lifecycle(self):
        source=(ROOT/'tools/ci_browser_editor.py').read_text()
        self.assertIn("get_by_role('checkbox',name='Seleziona')",source)
        # RC116 uses a strict accessible selection helper, not two legacy check() calls.
        self.assertIn('await select_exact_widget_pair(page)',source)
        self.assertIn('await checkbox.set_checked(label in wanted)',source)
        self.assertIn('len(checked_rows)==2',source)
        self.assertIn("set(selected_ids)=={'widget-a','widget-b'}",source)
        self.assertIn("to_have_count(2)",source)
        self.assertIn("to_have_count(5)",source)
        self.assertIn("to_have_count(3)",source)
        self.assertIn("await click_canvas_tool(page,'Porta selezione davanti')",source)
        self.assertIn("await click_canvas_tool(page,'Elimina selezione')",source)
        self.assertIn("await page.keyboard.press('Control+z')",source)
        self.assertNotIn('force=True',source)

    def test_failure_artifact_is_uploaded_without_exposing_production_state(self):
        source=(ROOT/'tools/ci_browser_editor.py').read_text()
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('editor-autosave-failure.png',source)
        self.assertRegex(workflow, r'actions/upload-artifact@v(?:4|7)\b')
        self.assertIn('if: failure() && github.event_name',workflow)
        self.assertIn('if-no-files-found: ignore',workflow)

if __name__=='__main__':unittest.main()
