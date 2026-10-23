"""Focused contracts for the three RC editor delivery areas."""
import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class RCMediaEditor(unittest.TestCase):
 def test_uploaded_widget_types_require_asset_reference(self):
  domain=(ROOT/'apps/api/src/domain.ts').read_text()
  self.assertIn("'image','video','logo','pdf'].includes(w.kind)",domain)
  self.assertIn('uuidRegex.test(w.assetId)',domain)
 def test_media_read_requires_current_published_page(self):
  api=(ROOT/'apps/api/src/server.ts').read_text()
  route=api.split("app.get('/api/join/:code/activities/:aid/media/:assetId'",1)[1].split("app.get('/api/join/:code/slides",1)[0]
  self.assertIn('s.current_activity_id!==req.params.aid',route)
  self.assertIn('status=\u00243',route)
  self.assertIn('w.assetId===req.params.assetId',route)
  self.assertIn('no-store',route)
 def test_attached_asset_cannot_be_deleted(self):
  api=(ROOT/'apps/api/src/server.ts').read_text()
  self.assertIn('asset_in_use_by_widget',api)
 def test_editor_filmstrip_and_preview(self):
  web=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn('Anteprime delle pagine',web)
  self.assertIn('beginPageDesign(a)',web)
  self.assertIn('File multimediale caricato',web)
  self.assertIn('Ricomincia prova',web)
 def test_binary_toggle_accessibility(self):
  web=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertGreaterEqual(web.count('className="binary-toggle" aria-pressed='),2)
