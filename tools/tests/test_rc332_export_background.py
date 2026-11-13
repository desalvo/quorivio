from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
class RC332Export(unittest.TestCase):
 def test_worker_renders_native_backgrounds_and_gradients(self):
  source=(ROOT/'tools/pptx_portable.py').read_text()
  for tag in ('backgroundAssetId', 'importedImageFit', 'master_background', "OxmlElement('a:gradFill')", "widget.get('kind') in ('shape','line')"):
   self.assertIn(tag,source)
 def test_api_stages_background_images_and_offers_pdf(self):
  server=(ROOT/'apps/api/src/server.ts').read_text()
  web=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn('masterBackground',server)
  self.assertIn('backgroundAssetId',server)
  # RC335 exposes two different views in each downloadable format.
  for label in ('PDF presentatore','PDF partecipante','PPTX presentatore','PPTX partecipante'):
   self.assertIn(label,web)
  for fmt in ('pdf','pptx'):
   for view in ('presenter','participant'):
    self.assertIn(f"/export.{fmt}?view={view}",web)
if __name__=='__main__':unittest.main()
