"""Regression for the opt-in real PostgreSQL Chromium widget-title editor."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BROWSER=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()

class ChromiumReadOnlyWidgetTitle(unittest.TestCase):
 def test_real_canvas_requires_explicit_title_editing(self):
  self.assertIn('readOnly={editing!==w.id}',UI)
  self.assertIn('onDoubleClick={e=>{setEditing(w.id)',UI)
  self.assertIn('input[readonly]{pointer-events:none', (ROOT/'apps/web/src/style.css').read_text())
  self.assertIn('>Modifica titolo</button>',UI)
  self.assertIn("if(e.key==='Enter'){e.currentTarget.blur();setEditing(null)}",UI)
 def test_helper_enters_edit_mode_via_real_accessible_context_menu(self):
  self.assertIn("field=item.get_by_role('textbox',name='Titolo text')",BROWSER)
  self.assertIn("trigger=item.get_by_role('button',name='Menu contestuale text')",BROWSER)
  self.assertIn('await trigger.click()',BROWSER)
  self.assertIn("menu=item.get_by_role('group',name='Azioni widget text')",BROWSER)
  self.assertIn("await menu.get_by_role('button',name='Modifica titolo').click()",BROWSER)
  self.assertIn('await expect(field).to_be_editable()',BROWSER)
  self.assertNotIn('await field.dblclick()',BROWSER)
 def test_helper_commits_and_checks_read_only_restoration(self):
  self.assertIn("await field.press('Enter')",BROWSER)
  self.assertIn('await expect(field).to_have_value(title)',BROWSER)
  self.assertEqual(BROWSER.count('await expect(field).not_to_be_editable()'),2)
 def test_all_four_scenarios_use_edit_helper(self):
  for label in ('Local second edit','Local final edit','Restored from local JSON','Discarded temporary local edit'):
   with self.subTest(label=label):
    self.assertIn(f"await edit_canvas_widget_title(canvas,'{label}')",BROWSER)
    self.assertNotIn(f".fill('{label}')",BROWSER)
  self.assertEqual(BROWSER.count('await edit_canvas_widget_title(canvas,'),4)
 def test_menu_button_stops_drag_pointer_propagation(self):
  self.assertIn('className="canvas-menu-trigger"',UI)
  self.assertIn('onPointerDown={e=>e.stopPropagation()}',UI)
  self.assertIn('setEditing(w.id);setContextWidget(null)',UI)
  self.assertIn('await expect(menu).to_have_count(0)',BROWSER)
 def test_isolated_chromium_reproduces_pointer_intercept_and_menu_success(self):
  smoke=(ROOT/'tools/ci_widget_title_menu.py').read_text()
  self.assertIn('pointer-events:none',smoke)
  self.assertIn('await field.dblclick(timeout=750)',smoke)
  self.assertIn('except PlaywrightTimeout:',smoke)
  self.assertIn("await menu.get_by_role('button',name='Modifica titolo').click()",smoke)
  self.assertIn("await expect(field).not_to_be_editable()",smoke)
 def test_opt_in_ci_runs_isolated_chromium_hit_target_before_database_browser(self):
  workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('python3 tools/ci_widget_title_menu.py\n          python3 tools/ci_browser_editor_postgres.py',workflow)
 def test_no_bypass_of_readonly_or_forced_actions(self):
  self.assertNotIn('removeAttribute(',BROWSER)
  self.assertNotIn('force=True',BROWSER)
  self.assertNotIn('dispatch_event(',BROWSER)
  self.assertNotIn('await field.dblclick()',BROWSER)
  self.assertNotIn('evaluate("element => element.readOnly',BROWSER)

if __name__=='__main__':unittest.main()
