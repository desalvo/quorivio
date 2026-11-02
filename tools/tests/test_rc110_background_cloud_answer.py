"""RC110 UI contracts: background upload errors visible; response size and cloud colors bounded."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[2]
M=(R/'apps/web/src/main.tsx').read_text()
API=(R/'apps/api/src/server.ts').read_text()
DOMAIN=(R/'apps/api/src/domain.ts').read_text()
CSS=(R/'apps/web/src/style.css').read_text()

class BackgroundUploadAndFormatting(unittest.TestCase):
 def test_background_upload_only_dismisses_after_success(self):
  self.assertIn('onBackgroundUpload(file).then(applied=>{if(applied)',M)
  self.assertIn("setBackgroundUploadStatus('Caricamento non riuscito:",M)
  self.assertIn('setBackgroundUploading(true)',M)
  self.assertIn('setBackgroundMenu(true);setBackgroundUploading(true)',M)
  self.assertIn('role="status" aria-live="polite"',M)
  self.assertIn('backgroundUploadError(r.status,code)',M)
  self.assertIn('catch(e){notify(e);throw e}finally{setAssetBusy(false)}',M)
  self.assertIn('return true;',M)
 def test_background_upload_and_use_server_response_contract(self):
  self.assertIn("app.post('/api/sessions/:id/backgrounds'",API)
  self.assertIn("res.status(201).json(applied)",API)
  self.assertIn("app.get('/api/sessions/:id/backgrounds'",API)
  self.assertIn("'image/jpeg'",API)
  self.assertIn('backgroundAssetId={questionBackgroundAsset}',M)
  self.assertIn('onBackgroundUpload={file=>uploadBackground(file,false)}',M)
  self.assertIn('backgroundSize:"cover"',M)
 def test_field_size_persisted_validated_and_rendered(self):
  for name in ['answerFieldWidth','answerFieldHeight']:
   self.assertIn(name,DOMAIN)
   self.assertIn(name,M)
  self.assertIn('Larghezza casella risposta libera (%)',M)
  self.assertIn('Altezza casella risposta libera (px)',M)
  self.assertIn('answerInputStyle(marks.style)',M)
  self.assertIn('answerInputStyle(w.style)',M)
 def test_cloud_colors_displayed_across_views(self):
  self.assertGreaterEqual(M.count('cloudRankColor('),3)
  self.assertIn('rankCloudItems(Object.entries(rev.options)',M)
  self.assertIn("chart==='cloud'?rankCloudItems(data",M)
  self.assertIn('rankCloudItems(words,w=>w.count,w=>w.word)',M)
  self.assertIn('.result-cloud-word',CSS)
if __name__=='__main__':unittest.main()
