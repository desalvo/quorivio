import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class MultimediaWidgetContracts(unittest.TestCase):
 def test_asset_ownership_and_mime_enforced(self):
  src=(ROOT/'apps/api/src/server.ts').read_text()
  self.assertIn('invalid_widget_asset',src)
  self.assertIn('participant_id IS NULL',src)
  self.assertIn("w.kind==='pdf'?['application/pdf']",src)
 def test_public_media_bound_to_live_page(self):
  src=(ROOT/'apps/api/src/server.ts').read_text()
  route=src.split("app.get('/api/join/:code/activities/:aid/media/:assetId'",1)[1].split("app.get('/api/join/:code/slides",1)[0]
  self.assertIn('s.current_activity_id!==req.params.aid',route)
  self.assertIn("'application/pdf'",route)
 def test_editor_exposes_logo_and_pdf(self):
  src=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn("'image','video','logo','pdf','topic-question'",src)
  self.assertIn("w.kind==='pdf'?'application/pdf'",src)
  self.assertIn('Apri documento PDF',src)
if __name__=='__main__':unittest.main()
