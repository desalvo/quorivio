"""RC134 guards: author-sized answer controls must render on real projection."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MAIN = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')


class PresenterAnswerParity(unittest.TestCase):
    def test_real_projection_has_readonly_textfield_and_disabled_submit(self):
        start = MAIN.index('function ProjectedQuestionPart(')
        end = MAIN.index('function SlideCanvasNumber(', start)
        body = MAIN[start:end]
        self.assertIn('data-readonly-preview="true"', body)
        self.assertIn('style={answerInputStyle(widget.style)} readOnly disabled tabIndex={-1}', body)
        self.assertIn('style={answerSubmitStyle(widget.style)}>Invia risposta</button>', body)
        self.assertIn('style={answerOptionStyle(widget.style)}', body)
        self.assertIn('type={mode===\'multiple\'?\'checkbox\':\'radio\'} disabled tabIndex={-1}', body)
        self.assertNotIn('Risposta testuale', body)
        self.assertNotIn('onClick=', body)
        self.assertNotIn('onChange=', body)

    def test_topic_question_projection_and_rehearsal_share_readonly_controls(self):
        self.assertIn('data-readonly-preview="true"><strong><WidgetStyledText text={widget.label', MAIN)
        self.assertIn('style={answerSubmitStyle(widget.style)}>Invia domanda</button>', MAIN)
        self.assertIn('kind===\'topic-question\'&&viewer===\'presenter\'?<ProjectionWidgetContent', MAIN)
        self.assertNotIn('rehearsal-presenter-answer-box" aria-label="Casella domanda libera vista presentatore', MAIN)
        self.assertNotIn('Le domande compariranno qui', MAIN)

    def test_authored_fonts_responses_and_button_parity(self):
        self.assertIn('.projection-interactive-widget>strong{font-size:inherit', CSS)
        self.assertIn('.projection-readonly-submit{flex:none', CSS)
        self.assertIn('opacity:.75;pointer-events:none', CSS)
        self.assertIn('.widget-answer-option>input{flex:none', CSS)

    def test_early_and_browser_ci_and_publication_gates(self):
        self.assertIn('tools.tests.test_rc134_presenter_answer_parity', WORKFLOW)
        self.assertIn('tools/ci_rc134_projection_answer_chromium.py', WORKFLOW)
        self.assertIn('needs.rc-campaign-conclusion.result', WORKFLOW)
        self.assertIn('!inputs.rc_acceptance_suite', WORKFLOW)


if __name__ == '__main__':
    unittest.main()
