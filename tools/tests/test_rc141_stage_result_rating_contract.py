"""RC141 compile-time contract: stage parity, anonymous aggregates and editable ratings."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
REACTIONS = (ROOT / 'apps/web/src/reaction-choices.tsx').read_text(encoding='utf8')
API = (ROOT / 'apps/api/src/server.ts').read_text(encoding='utf8')
DOMAIN = (ROOT / 'apps/api/src/domain.ts').read_text(encoding='utf8')


class RC141ResultAndRatingContract(unittest.TestCase):
    def test_rating_replaces_one_row_only_while_current_open_page(self):
        self.assertIn('ON CONFLICT(activity_id,participant_id,widget_id) DO UPDATE SET', API)
        self.assertIn('page_ratings.score IS DISTINCT FROM EXCLUDED.score', API)
        self.assertIn("AND status='open'", API)
        self.assertIn("s.status!=='active'", API)
        self.assertIn('pendingRatingVotes.current.has(key)', UI)
        self.assertIn('setRatingVotes(old=>({...old,[key]:String(score)}))', UI)

    def test_result_only_must_be_explicit_persisted_boolean(self):
        self.assertIn('resultsOnly?:boolean', DOMAIN)
        self.assertIn("w.kind==='results-button'&&typeof w.resultsOnly==='boolean'", DOMAIN)
        self.assertIn('checked={w.resultsOnly===true}', UI)
        self.assertIn('!widget.resultsOnly', UI)

    def test_reactions_share_render_and_title_off(self):
        self.assertEqual(UI.count('<ReactionChoices'), 3)
        # RC169 and later render the shared reaction component in all three
        # projection surfaces; editor projection suppresses the duplicated
        # outer heading, while an explicitly shown authored title is retained.
        self.assertIn("['reactions','results-button'].includes(w.kind)?{...w,showTitle:false}:w", UI)
        self.assertEqual(UI.count('<ReactionChoices'), 3)
        self.assertIn('data-show-title={widgetTitleVisible(w)}', UI)
        self.assertIn("w.showTitle!==false&&<strong><WidgetStyledText text={w.label||'Reazioni'}", UI)
        self.assertIn('REHEARSAL_EMOJIS.map(emoji', REACTIONS)
        self.assertIn('data-show-title="false"', (ROOT / 'tools/ci_rc141_widget_parity_chromium.py').read_text())

    def test_results_atomic_label_and_count_and_auto_fit(self):
        self.assertIn('className="linked-result-pair"', UI)
        self.assertIn('className="linked-result-label"', UI)
        self.assertIn('minScale={w.kind===\'results-button\'?.04:.12}', UI)
        self.assertIn('white-space:nowrap!important', CSS)
        self.assertIn('data-fit-mode="scale"', CSS)
        self.assertIn('data-fit-mode="scroll"', CSS)

    def test_checkbox_visual_parity_editor_presenter_and_audience(self):
        self.assertIn("w.answerMode==='multiple'?'checkbox':'radio'", UI)
        self.assertIn("q.answerMode==='multiple'?'checkbox':'radio'", UI)
        self.assertIn('className="widget-answer-option"', UI)
        self.assertIn('.widget-answer-option>input:is([type=checkbox],[type=radio])', CSS)


if __name__ == '__main__':unittest.main()
