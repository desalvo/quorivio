"""Guard the disabled-Deselect Chromium regression and CI diagnostic wiring."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

class ChromiumSelectionAcceptanceContract(unittest.TestCase):
    def test_browser_script_compiles_and_checks_undo_selection_lifecycle(self):
        source=(ROOT/'tools/ci_browser_editor.py').read_text()
        self.assertIn("get_by_role('checkbox',name='Seleziona')",source)
        self.assertIn('await checks.nth(0).check()',source)
        self.assertIn('await checks.nth(1).check()',source)
        self.assertIn("await click_canvas_tool(page,'Porta selezione davanti')",source)
        self.assertIn("await click_canvas_tool(page,'Elimina selezione')",source)
        self.assertIn("await page.keyboard.press('Control+z')",source)
        self.assertNotIn('force=True',source)

    def test_failure_artifact_is_uploaded_without_exposing_production_state(self):
        source=(ROOT/'tools/ci_browser_editor.py').read_text()
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('editor-autosave-failure.png',source)
        self.assertIn('actions/upload-artifact@v4',workflow)
        self.assertIn('if: failure() && github.event_name',workflow)
        self.assertIn('if-no-files-found: ignore',workflow)

if __name__=='__main__':unittest.main()
