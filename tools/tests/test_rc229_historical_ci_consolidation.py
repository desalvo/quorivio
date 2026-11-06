"""RC229 consolidated pre-npm compatibility and actionable background errors."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()

class RC229HistoricalCIConsolidation(unittest.TestCase):
 def test_named_background_upload_uses_safe_mapped_server_message(self):
  section=UI.split('async function uploadNamedFile(',1)[1].split('async function uploadAsset(',1)[0]
  self.assertIn("const code=typeof detail?.error==='string'?detail.error:''",section)
  self.assertIn("library==='backgrounds'?backgroundUploadError(response.status,code)",section)
  self.assertIn('if(!response.ok)',section)
  self.assertIn('response=await send(true)',section)
  self.assertIn("if(!window.confirm(`Esiste già un file",section)
 def test_failed_upload_does_not_dismiss_background_dialog(self):
  self.assertIn('onBackgroundUpload(file).then(applied=>{if(applied)',UI)
  self.assertIn(".catch(error=>{setBackgroundUploadStatus('Caricamento non riuscito:",UI)
  upload=UI.split('async function uploadBackground(',1)[1].split('async function uploadSchemaBackground(',1)[0]
  self.assertIn('catch(e){notify(e);throw e}',upload)
 def test_qr_link_is_accessible_and_safe(self):
  self.assertIn('widget.showQrUrl!==false&&<a className="participant-qr-url"',UI)
  self.assertIn('href={url}',UI)
  self.assertIn('rel="noopener noreferrer"',UI)
 def test_new_ci_stage_is_early_and_keeps_rc225_regression(self):
  self.assertIn('RC229 consolidated legacy UI and converter preflight before npm',CI)
  self.assertLess(CI.index('RC229 consolidated legacy UI'),CI.index('RC225 asset filenames'))
  self.assertIn('RC228 historical modal-gallery CI contract',CI)
