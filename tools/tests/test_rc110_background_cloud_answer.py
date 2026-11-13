"""RC110 UI contracts: background upload errors visible; response size and cloud colors bounded."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[2]
M=(R/'apps/web/src/main.tsx').read_text()
API=(R/'apps/api/src/server.ts').read_text()
DOMAIN=(R/'apps/api/src/domain.ts').read_text()
CSS=(R/'apps/web/src/style.css').read_text()



def mobile_background_routing_contract(source: str) -> bool:
 """Validate independently selected/uploaded canvas backgrounds.

 This intentionally checks both the desktop fallback and the phone branch;
 accepting the older unconditional desktop binding would be a regression.
 """
 import re
 stage = source.split('data-editor-device={canvasDevice}', 1)
 if len(stage) != 2 or '<WidgetCanvas key=' not in stage[1]:
  return False
 canvas = stage[1].split('<WidgetCanvas key=', 1)[1].split('/>', 1)[0]
 asset_route = ("backgroundAssetId={canvasDevice==='phone'?mobileLayoutDraft.backgroundAssetId||'':slideBackground({backgroundAssetId:questionBackgroundAsset||undefined,backgroundUrl:questionBackground||undefined},snap.session.theme).assetId||''}" in canvas)
 upload_route = re.search(
  r"onBackgroundUpload=\{file\s*=>\s*uploadBackground\(file,\s*false,\s*canvasDevice\s*===\s*'phone'\)\}",
  canvas,
 )
 selection_route = ("selectLibraryBackground(id,false,true)" in canvas and
                    "selectLibraryBackground(id,false)" in canvas)
 mobile_section = source.split('async function uploadBackground(',1)[-1].split('async function deleteAsset(',1)[0]
 mobile_write = ('if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}' in mobile_section)
 desktop_write = ("else{setQuestionBackgroundAsset(applied.id);setQuestionBackground('')}" in mobile_section)
 return bool(asset_route and upload_route and selection_route and mobile_write and desktop_write)

class BackgroundUploadAndFormatting(unittest.TestCase):
 def test_background_upload_only_dismisses_after_success(self):
  self.assertIn('onBackgroundUpload(file).then(applied=>{if(applied)',M)
  self.assertIn("setBackgroundUploadStatus('Caricamento non riuscito:",M)
  self.assertIn('setBackgroundUploading(true)',M)
  self.assertIn('setBackgroundMenu(true);setBackgroundUploading(true)',M)
  self.assertIn('role="status" aria-live="polite"',M)
  self.assertIn("library==='backgrounds'?backgroundUploadError(response.status,code)",M)
  self.assertIn('catch(e){notify(e);throw e}finally{setAssetBusy(false)}',M)
  self.assertIn('return true;',M)
 def test_background_upload_and_use_server_response_contract(self):
  self.assertIn("app.post('/api/sessions/:id/backgrounds'",API)
  self.assertIn("res.status(201).json(applied)",API)
  self.assertIn("app.get('/api/sessions/:id/backgrounds'",API)
  self.assertIn("'image/jpeg'",API)
  # RC149: the desktop background remains the fallback ONLY for the
  # desktop canvas. Phone mode must use an independent asset, defaulting
  # to no image; its upload must not call the desktop route.
  self.assertTrue(mobile_background_routing_contract(M))
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
  self.assertIn("const data=sortedResultBars(sourceRows,widget.resultSortOrder??source.resultSortOrder)",M)
  self.assertIn("const displayRows=visibleResultBars(sourceRows,widget.resultSortOrder??source.resultSortOrder,widget.resultTopCount??source.resultTopCount)",M)
  self.assertIn("chart==='cloud'",M)
  self.assertIn('rankCloudItems(words,w=>w.count,w=>w.word)',M)
  self.assertIn('.result-cloud-word',CSS)
if __name__=='__main__':unittest.main()
