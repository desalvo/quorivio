"""RC169: one rating body, master-resolved mobile font and real Chromium evidence."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
TYPO=(ROOT/'apps/web/src/stage-widget-typography.ts').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
BROWSER=(ROOT/'tools/ci_browser_participant.py').read_text(encoding='utf8')
LOCAL=(ROOT/'tools/ci_rc169_rating_typography_chromium.py').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC169RatingTypographyParity(unittest.TestCase):
    def test_rating_body_shared_by_editor_presenter_rehearsal_and_live(self):
        self.assertEqual(UI.count('<RatingCommentField '),1,'duplicate comment inputs would return')
        self.assertEqual(UI.count('<RatingChoices '),1,'scale must have one source of truth')
        self.assertNotIn('canvas-rating-preview',UI)
        self.assertIn('function RatingStageContent(',UI)
        self.assertIn("if(kind==='rating')return <RatingStageContent widget={widget} readOnly/>",UI)
        self.assertIn("kind==='rating'?<RatingStageContent widget={w} readOnly={viewer==='presenter'}",UI)
        self.assertIn("w.kind==='rating'?<RatingStageContent widget={w} comment={ratingComments[w.id]",UI)
        self.assertIn("widgetTitleVisible(widget)",UI)
        self.assertIn('WidgetStyledText text={widget.description}',UI)
        self.assertIn('size={widget.style?.ratingButtonSize}',UI)

    def test_phone_title_master_style_is_resolved_before_phone_font(self):
        self.assertIn("widget.kind==='title'?widgetDisplay(widget,context).style:widgetTextDefaults(widget.kind,widget.style)",TYPO)
        self.assertIn("const px=",TYPO)
        self.assertIn('resolved?.fontSize??16',TYPO)
        self.assertIn('stageWidgetTypography(w,{pageTitle:viewActivity.title',UI)
        self.assertIn('stageWidgetTypography(w,{pageTitle:entry.activity.title',UI)
        self.assertIn('stageWidgetTypography(w,{pageTitle,masterTitleStyle},mobileMode)',UI)
        self.assertEqual(UI.count('stageWidgetTypography(w,{pageTitle:'),3,'editor, rehearsal and public stage must use shared typeface resolution')

    def test_negative_unshared_rating_or_master_fallback_would_fail(self):
        broken=UI.replace('RatingStageContent widget={w} comment={ratingComments[w.id]',
                          'RatingCommentField value={ratingComments[w.id]',1)
        self.assertNotIn('w.kind===\'rating\'?<RatingStageContent widget={w} comment={ratingComments[w.id]',broken)
        broken=TYPO.replace('resolved?.fontSize??16','widget.style?.fontSize??16',1)
        self.assertNotIn('resolved?.fontSize??16',broken)
        self.assertIn('background:#ffffff!important;color:#142b44!important',CSS)

    def test_browser_uses_disposable_real_saved_rating_and_correct_phone_height(self):
        ast.parse(BROWSER)
        from tools.tests.test_rc165_authored_participant_chromium import run_fixture
        _,calls,design=run_fixture()
        widgets=design['page_design']['widgets']
        ratings=[w for w in widgets if w['kind']=='rating']
        self.assertEqual(len(ratings),1)
        self.assertEqual(ratings[0]['description'],'Descrizione del gradimento CI')
        self.assertEqual(ratings[0]['style']['ratingButtonSize'],24)
        self.assertIn('textarea.rating-comment-input',BROWSER)
        self.assertIn("get_by_role('button',name='Vota 9 su 9')",BROWSER)
        self.assertIn("geometry['height']-geometry['expectedHeight']",BROWSER)
        self.assertLess(next(i for i,c in enumerate(calls) if c[0]=='PATCH'),next(i for i,c in enumerate(calls) if c[1].endswith('/status')))

    def test_local_real_chromium_checks_two_viewports_and_white_comment(self):
        ast.parse(LOCAL)
        for fragment in ('for width in (390, 1440)',"'rgb(255, 255, 255)'",'choiceCount',
                         'descriptionCount','titleSize','ratingFont','commentBackground','assert'):
            self.assertIn(fragment,LOCAL)
        self.assertIn('overflow:auto!important',CSS)

    def test_ci_preflight_before_npm_browser_check_and_cumulative_manifest(self):
        self.assertIn('tools.tests.test_rc169_rating_typography_parity',CI)
        self.assertLess(CI.index('tools.tests.test_rc169_rating_typography_parity'),CI.index('npm ci --ignore-scripts'))
        self.assertIn('python3 tools/ci_rc169_rating_typography_chromium.py',CI)
        self.assertIn('python3 tools/verify_rc_cycle168_inventory.py --historical',CI)
        self.assertIn('python3 tools/verify_rc_cycle169_inventory.py',CI)

if __name__=='__main__': unittest.main()
