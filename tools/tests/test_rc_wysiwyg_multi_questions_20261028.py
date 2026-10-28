"""Architecture regressions for WYSIWYG and independently answerable widget questions."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
API = (ROOT/'apps/api/src/server.ts').read_text(encoding='utf-8')
DOMAIN = (ROOT/'apps/api/src/domain.ts').read_text(encoding='utf-8')
SCHEMA = (ROOT/'apps/api/src/schema.sql').read_text(encoding='utf-8')
WEB = (ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
RICH = (ROOT/'apps/web/src/widget-rich-editor.tsx').read_text(encoding='utf-8')
WORKFLOW = (ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')

class RichMultiQuestionRegression(unittest.TestCase):
    def test_plain_text_only_contenteditable_uses_same_segment_renderer(self):
        self.assertIn('contentEditable={active}', RICH)
        self.assertIn('styledSegments(value,marks,field)', RICH)
        self.assertIn("clipboardData.getData('text/plain')", RICH)
        self.assertNotIn('dangerouslySetInnerHTML', RICH)

    def test_editing_selection_and_caret_restore_after_formatting(self):
        self.assertIn('domTextRange(root.current)', RICH)
        self.assertIn('restoreDomTextRange(el,selection)', RICH)
        self.assertIn('onBeforeInput=', RICH)
        self.assertIn('onInput=', RICH)

    def test_question_definition_and_correction_are_bounded(self):
        self.assertIn('validWidgetSubquestions(w.questions,w.kind)', DOMAIN)
        self.assertIn('value.length>5', DOMAIN)
        self.assertIn('q?.options', DOMAIN)
        self.assertIn('questions?:WidgetSubquestion[]', DOMAIN)

    def test_backend_question_identity_does_not_erase_legacy_answers(self):
        self.assertIn("question_id text NOT NULL DEFAULT ''", SCHEMA)
        self.assertIn('widget_answers_one_per_question_revision', SCHEMA)
        self.assertIn('ON CONFLICT(activity_id,participant_id,widget_id,question_id,revision)', API)

    def test_persistence_and_aggregates_scoped_per_question(self):
        self.assertIn('AND question_id=$4 AND revision=$5', API)
        self.assertIn('GROUP BY activity_id,widget_id,question_id,revision,answer_mode', API)
        self.assertIn('AND w.question_id=$4', API)
        self.assertIn('question_id:questionId', API)

    def test_presenter_view_and_audience_have_distinct_question_fields(self):
        self.assertIn('function ProjectedQuestionPart(', WEB)
        self.assertIn('function QuestionWidgetSingle(', WEB)
        self.assertIn('questionId={question.id}', WEB)
        self.assertIn('question_id:questionId', WEB)
        self.assertIn('function WidgetSubquestionEditor(', WEB)

    def test_multi_question_rehearsal_does_not_write_to_live_api(self):
        start=WEB.index('function SessionRehearsal(')
        end=WEB.index('const editorWidgetNames:',start)
        body=WEB[start:end]
        self.assertIn("w.questions||[]", body)
        self.assertIn('responses[key]', body)
        self.assertNotIn("'/api/join/", body)

    def test_public_activity_never_exposes_nested_scoring_keys(self):
        self.assertIn('const {correctOptionId,correctOptionIds,...publicQuestion}=question', DOMAIN)
        self.assertIn('const {correctOptionId,correctOptionIds,...safe}=widget', DOMAIN)
        self.assertIn('publicActivity(published)', API)

    def test_new_cross_environment_e2e_is_opt_in_and_private(self):
        self.assertIn('tools/ci_browser_rich_text_offline.py', WORKFLOW)
        self.assertIn('tools/ci_independent_widget_questions_postgres.py', WORKFLOW)
        self.assertIn("QUORIVIO_CI_MULTI_QUESTION_TEST: '1'", WORKFLOW)
        self.assertIn('disposable loopback', (ROOT/'tools/ci_independent_widget_questions_postgres.py').read_text())

if __name__=='__main__':
    unittest.main()
