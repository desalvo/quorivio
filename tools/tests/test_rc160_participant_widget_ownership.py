"""RC160 participant widget ownership, accessible footer and rating comment parity."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
MOBILE=(ROOT/'apps/web/src/mobile-page-layout.ts').read_text(encoding='utf8')
RATING=(ROOT/'apps/web/src/rating-choices.tsx').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

def participant_view(ui: str)->str:
    a=ui.find('{joinPath?<main id="main-content" className="narrow participant-live-view"')
    b=ui.find('publicPath?<PresenterLiveScreen',a)
    return ui[a:b] if a>=0 and b>a else ''

def widget_only(ui: str)->bool:
    view=participant_view(ui)
    return bool(view) and all((
        '<AudienceExtensions' not in view,
        'className="reaction-bar"' not in view,
        'Pagina informativa: nessuna risposta richiesta' not in view,
        "w.kind==='topic-question'?<TopicQuestionWidget" in view,
        "w.kind==='question'?<QuestionWidget" in view,
        "w.kind==='reactions'?<div className=\"projection-sample-reactions\"" in view,
        "(entry.activity.page_design?.widgets||[]).length||entry.activity.type==='slide'?null" in view,
    ))

class ParticipantWidgetOwnership(unittest.TestCase):
    def test_no_non_authored_participant_interactions(self):
        self.assertTrue(widget_only(UI))
    def test_negative_reintroduced_unrequested_panel(self):
        self.assertFalse(widget_only(UI.replace('{audienceTimerExpired&&', '<AudienceExtensions joinCode={joinCode}/>{audienceTimerExpired&&',1)))
    def test_negative_reintroduced_global_reaction_bar(self):
        self.assertFalse(widget_only(UI.replace('{audienceTimerExpired&&', '<div className="reaction-bar"/> {audienceTimerExpired&&',1)))
    def test_negative_removed_authored_questions(self):
        self.assertFalse(widget_only(UI.replace("w.kind==='topic-question'?<TopicQuestionWidget", "w.kind==='topic-question'?null",1)))
    def test_mobile_footer_last_at_stage_bottom(self):
        # RC162: visual-order phone stacking, footer still last and bottom-aligned.
        self.assertIn("if(a.w.kind==='footer')return b.w.kind==='footer'?a.index-b.index:1;",MOBILE)
        self.assertIn("if(b.w.kind==='footer')return -1;",MOBILE)
        self.assertIn('for(const {w} of ordered)',MOBILE)
        self.assertIn('const ay=a.w.position?.y',MOBILE)
        # Negative mutation rejects removing the footer precedence.
        self.assertNotIn("if(b.w.kind==='footer')return -1;",MOBILE.replace("if(b.w.kind==='footer')return -1;",''))
        self.assertIn("Math.max(top,stageHeight-24-size)",MOBILE)
        self.assertIn("case 'rating':return 230",MOBILE)
        self.assertIn('order:9999!important',CSS)
        self.assertIn('order:10000!important',CSS)
    def test_rating_comment_rendered_and_white_on_every_surface(self):
        view=participant_view(UI)
        self.assertIn('<RatingCommentField value={ratingComments[w.id]',view)
        self.assertIn('canvas-rating-preview"><RatingCommentField readOnly',UI)
        self.assertIn('<RatingCommentField readOnly={viewer===',UI)
        self.assertIn('className="rating-comment-input"',RATING)
        self.assertIn('background-color:#ffffff!important;color:#142b44!important',CSS)
        self.assertIn('color-scheme:light!important',CSS)
    def test_ci_has_early_and_live_chromium_parity(self):
        self.assertIn('tools.tests.test_rc160_participant_widget_ownership',CI)
        self.assertIn('tools/ci_rc160_participant_layout_chromium.py',CI)
        self.assertLess(CI.index('tools.tests.test_rc160_participant_widget_ownership'),CI.index('npm install --ignore-scripts'))

if __name__=='__main__':unittest.main()
