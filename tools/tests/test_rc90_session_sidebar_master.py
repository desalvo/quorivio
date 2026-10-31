"""RC90 contract: session actions and editor-style master schema."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
MASTER=(ROOT/'apps/web/src/master-widget-utils.ts').read_text()

class SessionSidebarAndMaster(unittest.TestCase):
 def test_sidebar_actions_are_live_and_bound_to_current_session(self):
  for label in ('Azioni della sessione corrente','Chiudi sessione','Duplica sessione','Rinomina sessione','Elimina sessione','Torna alle sessioni'):
   self.assertIn(label,UI)
  for method in ('closeSidebarSession','duplicateSelected','renameSidebarSession','deleteSession'):
   self.assertIn(method,UI)
  self.assertIn("window.confirm('Terminare definitivamente",UI)
  self.assertIn('Eliminare definitivamente la sessione e tutte le risposte?',UI)
  self.assertIn("selectedSessionRole==='owner'",UI)
  self.assertIn('result.session.access_role',(ROOT/'apps/api/src/server.ts').read_text())
 def test_title_and_date_are_persisted_through_authorized_api(self):
  self.assertIn("/sessions/${selected}/metadata`,'PATCH'",UI)
  self.assertIn("{title,reference_date}",UI)
  self.assertIn("snap.session.status==='closed'",UI)
 def test_presenter_screen_label_is_correct(self):
  self.assertIn('<h3>Schermo presentatore</h3>',UI)
  self.assertNotIn('<h3>Anteprima presentatore</h3>',UI)
 def test_dedicated_global_schema_uses_the_real_canvas(self):
  self.assertIn('Editor degli schemi PowerPoint',UI)
  self.assertIn('widgets={schemaWidgets}',UI)
  self.assertIn("`/sessions/${selected}/design`,'PATCH'",UI)
  self.assertIn('masterWidgetTemplate',UI)
  self.assertIn('resolveSlideMasterWidgets',UI)
  self.assertIn("master.widgets!==undefined",DOMAIN)
  self.assertIn('validPageDesign({widgets})',DOMAIN)
  self.assertNotIn('legacy-page-admin',UI)
  self.assertNotIn('Modifica dati legacy',UI)
  self.assertIn("if(!window.confirm('Applicare Titolo e Footer",UI)
  self.assertIn('inherited-',MASTER)
 def test_footer_is_visible_with_ten_pixel_number_inset(self):
  self.assertIn('position:{x:0,y:87,width:100,height:13,rotation:0}',(ROOT/'apps/web/src/slide-master.ts').read_text())
  self.assertIn('right:10px!important;bottom:10px!important',CSS)

if __name__=='__main__':unittest.main()
