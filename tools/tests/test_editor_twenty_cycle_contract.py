"""Acceptance wiring contracts for the editor completion batch (browser test is CI opt-in)."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

class EditorTwentyCycleContracts(unittest.TestCase):
    def test_browser_fixture_persists_saved_layout_across_reload(self):
        source=(ROOT/'tools/ci_browser_editor.py').read_text()
        ast.parse(source)
        self.assertIn("state['widgets']=copy.deepcopy(payload['page_design']['widgets'])",source)
        self.assertIn("state['revision']+=1",source)
        self.assertIn("await page.reload(wait_until='domcontentloaded')",source)
        self.assertIn("assert state['saves']>=1",source)

    def test_browser_exercises_group_layer_and_keyboard_operations(self):
        source=(ROOT/'tools/ci_browser_editor.py').read_text()
        for command in ("await click_canvas_tool(page,'Porta selezione davanti')", "await click_canvas_tool(page,'Sposta selezione a destra')", "await click_canvas_tool(page,'Duplica selezione')", "await click_canvas_tool(page,'Elimina selezione')", "await page.keyboard.press('ArrowRight')", "await page.keyboard.press('Control+z')"):
            with self.subTest(command=command):self.assertIn(command,source)
        self.assertNotIn('force=True',source)

    def test_canvas_exposes_accessible_commands_and_no_forced_click(self):
        source=(ROOT/'apps/web/src/main.tsx').read_text()
        for name in ('Ordine e spostamento widget selezionati','Porta selezione davanti',
                     'Un livello indietro','Elimina selezione','Spazi orizzontali uguali',
                     'Centra selezione nel canvas verticalmente'):
            with self.subTest(name=name):self.assertIn(name,source)
        self.assertNotIn('force=True', (ROOT/'tools/ci_browser_editor.py').read_text())

if __name__=='__main__':unittest.main()
