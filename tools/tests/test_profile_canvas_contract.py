import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class ProfileCanvasContract(unittest.TestCase):
 def test_profile_upload_protected_and_scanned(self):
  code=(ROOT/'apps/api/src/server.ts').read_text()
  self.assertIn("app.post('/api/auth/profile/photo',requireAuth",code)
  self.assertIn('scanUploadedFile(received.destination)',code)
  self.assertIn("app.delete('/api/auth/profile/photo',requireAuth",code)
  self.assertIn("5*1024*1024",code)
 def test_no_external_profile_photo_url_editor(self):
  code=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertNotIn('Foto profilo (URL HTTPS)',code)
  self.assertIn('type="file" accept="image/png,image/jpeg,image/webp"',code)
 def test_toolbox_drag_drop_and_alert_closure(self):
  code=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn('onDragStart={e=>e.dataTransfer.setData',code)
  self.assertIn('onDrop={e=>{const kind=',code)
  self.assertIn('e.stopPropagation();setNotice',code)
