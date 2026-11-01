"""Regression guards for the user-owned and collaborator-copied background workflow."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[2]
API = (ROOT/'apps/api/src/server.ts').read_text()
SCHEMA = (ROOT/'apps/api/src/schema.sql').read_text()
WEB = (ROOT/'apps/web/src/main.tsx').read_text()
STYLE = (ROOT/'apps/web/src/style.css').read_text()

class PresenterBackgroundLibraryCycle39(unittest.TestCase):
 def test_library_is_user_owned_and_durable(self):
  self.assertIn('CREATE TABLE IF NOT EXISTS presenter_backgrounds',SCHEMA)
  self.assertIn('owner_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE',SCHEMA)
  self.assertIn("path.join(assetRoot,'background-library')",API)
  self.assertIn("app.post('/api/sessions/:id/backgrounds'",API)
  self.assertIn('await scanUploadedFile(received.destination)',API)
 def test_collaborator_copy_before_application(self):
  self.assertIn('me.session_id=shared.id AND me.user_id=$2',API)
  self.assertIn('other.session_id=shared.id AND other.user_id=b.owner_id',API)
  self.assertIn('const libraryId=borrowed?randomUUID():b.id;',API)
  self.assertIn('if(borrowed)await copyFile(source,libraryTarget)',API)
  self.assertIn('await copyFile(source,sessionTarget)',API)
  self.assertIn('INSERT INTO presenter_backgrounds',API)
 def test_canvas_background_really_renders_and_upload_selects_library(self):
  self.assertIn('--editor-page-background',WEB)
  self.assertIn('background-image:var(--editor-page-background,none)!important',STYLE)
  self.assertIn('setQuestionBackgroundAsset(applied.id)',WEB)
  self.assertIn('setBackgrounds(library)',WEB)
  self.assertIn('assets={assets} backgrounds={backgrounds}', WEB)
  self.assertIn('if(selected){void refreshAssets()}',WEB)
  self.assertNotIn('Nessuno sfondo caricato',WEB)
 def test_current_public_page_media_only_and_deletion_safe(self):
  self.assertIn("app.get('/api/join/:code/activities/:aid/media/:assetId'",API)
  self.assertIn("s.current_activity_id!==req.params.aid",API)
  self.assertIn('asset_in_use_by_background',API)
  self.assertIn('ci_background_library_postgres.py', (ROOT/'.github/workflows/ci.yml').read_text())
  self.assertIn('/api/join/${encodeURIComponent(joinCode)}/activities/${entry.activity.id}/media/',WEB)
 def test_visualization_is_on_source_and_cloud_is_animated(self):
  self.assertIn('effectiveResultView(widget,widgets)',WEB)
  self.assertNotIn('aria-label="Grafico dei risultati"',WEB)
  self.assertIn('quorivio-word-cloud-float',STYLE)
  self.assertIn('@media(prefers-reduced-motion:reduce)',STYLE)

if __name__=='__main__':unittest.main()
