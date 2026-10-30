"""WYSIWYG editor title regression across real Chromium and PostgreSQL E2E."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BROWSER=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()
RICH=(ROOT/'apps/web/src/widget-rich-editor.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()

class ChromiumWidgetTitleEditing(unittest.TestCase):
 def test_real_canvas_title_has_explicit_context_action_and_double_click(self):
  self.assertIn('onDoubleClick={e=>',UI)
  self.assertIn('setEditing(w.id);requestAnimationFrame',UI)
  self.assertIn('>Modifica titolo</button>',UI)
  self.assertIn('<RichWidgetText value={w.label',UI)
  self.assertIn('active={editing===w.id}',UI)
  self.assertIn("ariaLabel={'Titolo '+w.kind}",UI)
  self.assertNotIn('readOnly={editing!==w.id}',UI)
 def test_wysiwyg_finishes_on_enter_without_forcing_a_click(self):
  self.assertIn('contentEditable={active}',RICH)
  self.assertIn('onFinish?.();e.currentTarget.blur()',RICH)
  self.assertNotIn('onBlur={e=>',RICH) # formatting palette must preserve the edit mode
  self.assertIn('onFinish={()=>setEditing(null)}',UI)
  self.assertIn('restoreDomTextRange(el,selection)',RICH)
 def test_postgresql_chromium_asserts_actual_contenteditable_state(self):
  self.assertIn("field=item.locator('.widget-rich-inline').first",BROWSER)
  self.assertIn("await item.click(button='right',position={'x':12,'y':12})",BROWSER)
  self.assertIn("await menu.get_by_role('button',name='Modifica titolo').click()",BROWSER)
  self.assertIn("await expect(field).to_have_attribute('contenteditable','true')",BROWSER)
  self.assertIn("await expect(field).to_have_attribute('contenteditable','false')",BROWSER)
  self.assertIn('await field.fill(title)',BROWSER)
  self.assertIn("await field.press('Enter')",BROWSER)
  self.assertIn('await expect(field).to_have_text(title)',BROWSER)
 def test_real_browser_verifies_concurrent_autosave_and_merge(self):
  self.assertIn("await edit_canvas_widget_title(page,widgets,'Local second edit')",BROWSER)
  self.assertIn("menu=page.get_by_role('group',name='Azioni widget text',exact=True)",BROWSER)
  self.assertIn("assert resolved['page_design']['widgets'][0]['label']=='Local second edit'",BROWSER)
  self.assertIn("await expect(editor.get_by_text('Conflitto di revisione'))",BROWSER)
  self.assertNotIn('force=True',BROWSER)
  self.assertNotIn('dispatch_event(',BROWSER)
 def test_pointer_policy_and_no_html_persistence(self):
  self.assertIn('.widget-rich-editing',CSS)
  self.assertIn('styledSegments(value,marks,field)',RICH)
  self.assertNotIn('dangerouslySetInnerHTML',RICH)
 def test_opt_in_ci_runs_browser_preflight_before_database_browser(self):
  workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('python3 tools/ci_widget_title_menu.py\n          python3 tools/ci_browser_editor_postgres.py',workflow)
 def test_mock_chromium_uses_current_editable_contract(self):
  mock=(ROOT/'tools/ci_widget_title_menu.py').read_text()
  self.assertIn('contenteditable="false"',mock)
  self.assertIn("await menu.get_by_role('button',name='Modifica titolo').click()",mock)
  self.assertIn("await item.dblclick(position={'x':12,'y':12})",mock)
  self.assertIn("await field.press('Enter')",mock)
  self.assertNotIn('force=True',mock)
 def test_production_rich_text_chromium_checks_enter_and_unicode(self):
  script=(ROOT/'tools/ci_browser_rich_text_offline.py').read_text()
  harness=(ROOT/'tools/fixtures/ci_richtext_harness.tsx').read_text()
  self.assertIn('RichWidgetText',harness)
  self.assertIn('onFinish={()=>setActive(false)}',harness)
  self.assertIn("await editor.press('Enter')",script)
  self.assertIn('compositionend',script)
  self.assertIn('for width in (1440,390)',script)
if __name__=='__main__':unittest.main()
