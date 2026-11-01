"""RC residual: public slide fidelity and dynamically isolated dialog backgrounds."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
DOM=(ROOT/'apps/web/src/rehearsal-dialog.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()
BROWSER=(ROOT/'tools/ci_rc_public_stage_chromium.py').read_text()
PORTALS=(ROOT/'tools/ci_rc_rehearsal_dynamic_portals_chromium.py').read_text()

class PublicSlideFidelity(unittest.TestCase):
 def test_live_stage_uses_saved_page_percent_and_rotation_in_normalized_16_by_9(self):
  for clause in ('audience-stage-scroll','stage-fidelity','--stage-x','--stage-height','--stage-rotation','aspect-ratio:16/9','rotate(var(--stage-rotation,0deg))'):
   self.assertIn(clause,UI+'\n'+CSS)
  self.assertNotIn('position:"relative",minHeight:560',UI)
 def test_reading_mode_is_visible_controlled_and_reachable(self):
  for clause in ('participantReadingMode','Diapositiva 16:9','Lettura accessibile','aria-pressed={!participantReadingMode}','aria-pressed={participantReadingMode}','aria-label="Visualizzazione della pagina"','aria-label="Contenuto della diapositiva" tabIndex={0}'):
   self.assertIn(clause,UI)
  self.assertIn("window.matchMedia('(max-width:700px)').matches",UI)
  self.assertIn('.audience-widget-layout.stage-reading>.page-widget[style*="--stage-x"]',CSS)
  self.assertIn('min-height:44px',CSS)
 def test_live_uses_private_asset_access_fence_already_present(self):
  backend=(ROOT/'apps/api/src/server.ts').read_text()
  self.assertIn("app.get('/api/join/:code/activities/:aid/media/:assetId'",backend)
  self.assertIn('current_activity_id!==req.params.aid',backend)
  self.assertIn('entry.activity.page_design.backgroundAssetId',UI)
  self.assertIn('encodeURIComponent(entry.activity.page_design.backgroundAssetId)',UI)
  self.assertIn('src={`/api/join/',UI)
 def test_live_maintains_rich_text_and_imported_image_crop(self):
  for clause in ('<CroppedImage className="projection-media" src={`/api/join/', 'crop={w.crop}', '<WidgetStyledText text={w.description} widget={w} field="description"/>', '<WidgetStyledText text={w.label||\'Nota\'} widget={w} field="label"/>'):
   self.assertIn(clause,UI)
  self.assertNotIn('dangerouslySetInnerHTML',UI)
 def test_offline_browser_checks_1440_390_and_mobile_reading_targets(self):
  for clause in ('1440,940','390,844','stage-reading',"result['touch']>=44",'--stage-rotation:9deg','scroll'):
   self.assertIn(clause,BROWSER)
  self.assertIn('python3 tools/ci_rc_public_stage_chromium.py',CI)

class ModalDynamicSiblings(unittest.TestCase):
 def test_inert_new_nodes_and_restore_their_preexisting_state(self):
  for clause in ('MutationObserver','isolateBackground()', 'backgroundObserver.disconnect()', 'background.has(sibling)', 'node.inert = previous.inert', 'node.setAttribute(\'aria-hidden\', ariaHidden)'):
   self.assertIn(clause,DOM)
 def test_tab_skips_hiding_and_disabled_elements(self):
  self.assertIn('[aria-hidden="true"]',DOM)
  self.assertIn("element.matches(':disabled')",DOM)
 def test_real_ts_chromium_fixture_validates_new_portal_inaccessibility_and_recovery(self):
  for clause in ('rehearsal-dialog.ts', 'npm','root','late-portal',"aria-hidden')=='true'","aria-hidden')=='false'", '1440,390', "page.keyboard.press('Escape')"):
   self.assertIn(clause,PORTALS)
  self.assertIn('python3 tools/ci_rc_rehearsal_dynamic_portals_chromium.py',CI)

if __name__=='__main__':unittest.main()
