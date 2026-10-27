"""Regression guard for closed-session copies and richer presentation widget behavior."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()
M=(ROOT/'apps/api/src/portable-bundle.ts').read_text()
class ClosedSessionDuplication(unittest.TestCase):
 def test_authorized_copy_is_not_blocked_when_source_closed(self):
  handler=API.split("app.post('/api/sessions/:id/duplicate'",1)[1].split("app.get('/api/sessions/:id/presenters'",1)[0]
  self.assertIn('await owner(req.params.id,auth(req)!)',handler)
  self.assertNotIn("s.status==='closed'",handler)
  self.assertIn('createFromPortable',handler)
  self.assertIn("status:'draft'",handler)
  self.assertIn("data_copied:false",handler)
 def test_closed_and_collaborator_copy_available_in_directory(self):
  self.assertIn('duplicateSessionFrom(s.id)',UI)
  self.assertIn("s.status==='closed'",UI)
  self.assertIn('risposte, voti, statistiche',UI)
 def test_no_participant_records_or_credential_reuse(self):
  definition=API.split('async function portableSession(',1)[1].split('function validPortable',1)[0]
  self.assertNotIn('FROM responses',definition)
  self.assertNotIn('FROM participants',definition)
  self.assertNotIn('join_secret',definition)
  self.assertIn('randomBytes(20)',API)
 def test_per_widget_image_assets_are_remapped(self):
  self.assertIn('fillImageAssetId',M)
  self.assertIn('fillImageAssetId',API)
 def test_destructive_actions_require_confirmation(self):
  self.assertGreaterEqual(UI.count('window.confirm('),5)
  self.assertIn('Eliminare questo widget dal canvas?',UI)
  self.assertIn("onClick={()=>{if(!window.confirm('Eliminare questo widget dal canvas?'))return;setPageWidgets(old=>old.filter(z=>z.id!==w.id))}",UI)
 def test_rich_editor_has_magnetic_and_formatting_ui(self):
  for needle in ['freeWidgetPosition','magneticSnapWidget','rejectWidgetCollisions','widget-selection-palette','Forma del widget','Tipo riempimento','Trasparenza riempimento']:
   self.assertIn(needle,UI)
if __name__=='__main__':unittest.main()
