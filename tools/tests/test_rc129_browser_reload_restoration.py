"""RC129 regression: Chromium must test persisted editor restoration after reload."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf-8')
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
STATE=(ROOT/'apps/web/src/workspace-recovery.ts').read_text(encoding='utf-8')

class BrowserWorkspaceReload(unittest.TestCase):
 def test_reload_observes_editor_without_reopening_background_sidebar(self):
  post=SCRIPT.split("await page.reload(wait_until='domcontentloaded')",1)[1]
  before_export=post.split("# Import/export live only on the relevant thumbnail",1)[0]
  self.assertIn('await await_frontend_mount(page,errors)',before_export)
  self.assertIn("editor=page.get_by_role('region',name='Editor grafico delle pagine')",before_export)
  self.assertIn('await expect(editor).to_be_visible(timeout=30000)',before_export)
  self.assertIn("await expect(editor.locator('.widget-canvas-item')).to_have_count(4)",before_export)
  self.assertNotIn("get_by_role('button',name='Apri sessione')",before_export)
  self.assertNotIn("get_by_role('button',name='✎ Modifica le pagine')",before_export)
  self.assertNotIn('force=True',before_export)

 def test_restoration_checks_saved_session_page_and_current_thumbnail(self):
  self.assertIn("recovered.get('sessionId')==SESSION",SCRIPT)
  self.assertIn("recovered.get('pageId')==ACTIVITY",SCRIPT)
  self.assertIn(".page-editor-thumb-row.is-active .page-editor-thumb",SCRIPT)
  self.assertIn("to_have_attribute('aria-current','page')",SCRIPT)

 def test_state_is_tab_local_authenticated_and_persistent_but_not_private(self):
  self.assertIn('sessionStorage.setItem',STATE)
  self.assertNotIn('localStorage.setItem',STATE)
  self.assertIn("const [selected,setSelected]=useState<string>(()=>readWorkspaceLocation().sessionId)",UI)
  self.assertIn('if(me===undefined||!me)return;writeWorkspaceLocation',UI)
  self.assertIn('if(!me||!selected||!snap||snap.session.id!==selected',UI)
  # RC208: a failed transient snapshot stays retryable; only permanently revoked/removed
  # sessions clear the tab-local route. This must never clear the auth cookie.
  self.assertIn("outcome==='unavailable'",UI)
  self.assertIn("writeWorkspaceLocation({sessionId:'',section:'workspace'",UI)
  self.assertIn("setSessionLoadState('retry')",UI)

if __name__=='__main__': unittest.main()
