"""Page title edits must never invalidate results or leak rehearsal controls to participants."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
E2E=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()

class PageRenamePreviewContract(unittest.TestCase):
 def test_dedicated_authorized_title_only_endpoint(self):
  target=API.split("app.patch('/api/sessions/:id/pages/:aid/title',requireAuth",1)[1].split("app.post('/api/sessions/:id/activities/:aid/invalidate'",1)[0]
  self.assertIn('await owner(req.params.id,auth(req)!)',target)
  self.assertIn("if(live.rows[0].status==='closed')",target)
  self.assertIn("UPDATE activities SET title=$3,revision=revision+1",target)
  self.assertNotIn('page_design=',target)
  self.assertNotIn('options=',target)
  self.assertIn('invalid_page_title',target)
  self.assertIn('await broadcast(s.id)',target)
  self.assertLess(target.index('await owner(req.params.id'),target.index('cx=await db.connect()'))
 def test_rename_accessible_from_thumbnail_and_blank_canvas(self):
  self.assertIn('async function renameCanvasPage(page:Activity)',UI)
  self.assertIn('onRenamePage={renameCurrentCanvasPage}',UI)
  self.assertIn('>Rinomina pagina</button>',UI)
  self.assertIn('void renameCanvasPage(a)',UI)
  self.assertIn('setSnap(old=>old?{...old,activities:old.activities.map(',UI)
 def test_rehearsal_exposes_one_page_with_navigation_only_in_preview_footer(self):
  block=UI.split('function SessionRehearsal(',1)[1].split('const editorWidgetKinds=',1)[0]
  self.assertNotIn('className="rehearsal-pages"',block)
  self.assertIn('!widgets.length&&<h2 className="rehearsal-empty-title">{activity?.page_design?.header||activity?.title}</h2>',block)
  self.assertIn('Successiva →',block)
  self.assertIn('Nessuna risposta di prova viene salvata',block)
  self.assertIn('.rehearsal-stage{display:block;',CSS)
 def test_live_participant_uses_only_server_selected_current_activity(self):
  live=UI.split('entry?.activity?<section className="panel"',1)[1].split('</main>',1)[0]
  self.assertIn('entry.activity.page_design?.widgets',live)
  self.assertIn("!(entry.activity.page_design?.widgets||[]).length",live)
  self.assertNotIn('setPage(',live)
 def test_postgres_chromium_checks_title_and_preserves_design(self):
  self.assertIn('Renamed browser slide',E2E)
  self.assertIn("renamed_activity['design_revision']==3",E2E)
  self.assertIn("renamed_activity['options']==",E2E)
  self.assertIn("renamed_activity['page_design']['widgets'][0]['position']['x']==11",E2E)

if __name__=='__main__':unittest.main()
