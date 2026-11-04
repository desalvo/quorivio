"""RC144: offline safety/compatibility contracts for phone layout and rating scale."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def source(name):return (ROOT/name).read_text(encoding='utf8')
class MobileRatingContracts(unittest.TestCase):
 def test_rate_scale_is_restricted_at_api_and_db(self):
  self.assertIn('score>9',source('apps/api/src/server.ts'))
  self.assertIn('page_ratings_score_zero_to_nine CHECK(score BETWEEN 0 AND 9) NOT VALID',source('apps/api/src/schema.sql'))
  self.assertIn('RATING_MAX=9',source('apps/web/src/rating-range.ts'))
 def test_mobile_assets_are_authorized_to_a_session(self):
  api=source('apps/api/src/server.ts')
  self.assertIn('page_design?.mobile?.backgroundAssetId===req.params.assetId',api)
  self.assertIn("page_design->'mobile'->>'backgroundAssetId'=$2",api)
  self.assertIn('for(const design of [req.body.page_design,req.body.result_design,req.body.page_design.mobile||{}])',api)
 def test_mobile_geometry_is_not_desktop_geometry(self):
  ui=source('apps/web/src/main.tsx')
  self.assertIn('data-editor-device={canvasDevice}',ui)
  self.assertIn('mobilePageWidgets(pageWidgets,mobileLayoutDraft)',ui)
  self.assertIn('position:original.position',ui)
  self.assertIn('audiencePortrait?audiencePhoneLayout.widgets:audienceVisibleWidgets',ui)
  self.assertIn('height:audiencePhoneLayout.height',ui)
  self.assertIn('mobile?{backgroundImage:activity?.page_design?.mobile?.backgroundAssetId?',ui)
 def test_phone_controls_do_not_downscale_fonts(self):
  ui=source('apps/web/src/main.tsx');css=source('apps/web/src/style.css')
  self.assertIn('allowScale={!mobile&&',ui)
  self.assertIn('allowScale={!mobileMode&&',ui)
  self.assertIn('min-height:min-content!important;',css)
  self.assertIn('width:390px!important;height:100%!important;',css)
 def test_collaboration_and_restore_keep_mobile_draft(self):
  self.assertIn('validMobilePageLayout',source('apps/web/src/page-draft-recovery.ts'))
  self.assertIn("const mobile=value('/mobile'",source('apps/web/src/page-merge.ts'))
  self.assertIn('pruneMobilePageLayout(mobileLayoutDraft,pageWidgets)',source('apps/web/src/main.tsx'))
 def test_release_gate_stays_closed(self):
  doc=source('docs/RC_CYCLE144_INDEPENDENT_PHONE_RATING_FONT.en.md')
  for marker in ('85.25%','rc_strict=false','publish_image=false','publish_latest=false'):
   self.assertIn(marker,doc)
if __name__=='__main__':unittest.main()
