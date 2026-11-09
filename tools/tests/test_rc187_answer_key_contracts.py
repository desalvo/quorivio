"""RC187 fail-closed preflight: optional answer-key lifecycle and privacy."""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()
KEY=(ROOT/'apps/api/src/widget-answer-key.ts').read_text()
SERVER=(ROOT/'apps/api/src/server.ts').read_text()
REVISIONS=(ROOT/'apps/api/src/widget-revisions.ts').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()
STYLE=(ROOT/'apps/web/src/style.css').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()
class RC187AnswerKeyContracts(unittest.TestCase):
 def test_field_is_explicit_opt_in_and_validated(self):
  self.assertIn('answerKeyEnabled?:boolean',DOMAIN)
  self.assertIn("w.answerKeyEnabled===undefined",DOMAIN)
  self.assertIn("v.answerKeyEnabled===true",DOMAIN)
  self.assertIn("new Set(v.correctOptionIds)",DOMAIN)
 def test_key_is_never_in_public_projection(self):
  self.assertIn('const {correctOptionId,correctOptionIds,...safe}=widget',DOMAIN)
  self.assertIn('const {correctOptionId,correctOptionIds,...publicQuestion}=question',DOMAIN)
  self.assertIn('publicPageDesign(visible.result_design)',DOMAIN)
  self.assertIn('theme:publicTheme(s.theme)',SERVER)
  self.assertNotIn('gradeChoiceAnswer(',DOMAIN)
 def test_server_feedback_cannot_be_read_before_submit(self):
  route=SERVER.split("app.post('/api/join/:code/activities/:aid/widgets/:wid/respond'",1)[1].split("app.get('/api/sessions/:id/widget-answers'",1)[0]
  self.assertIn('gradeChoiceAnswer(part,widget.kind,answer.optionIds)',route)
  self.assertIn('gradeChoiceAnswer(part,widget.kind,existing.rows[0].answer_payload?.optionIds)',route)
  self.assertIn('const stored=r.rowCount?answer.optionIds:',route)
  self.assertIn("await cx.query('COMMIT')",route)
  self.assertIn('submittedFeedback?{feedback:submittedFeedback}',route)
  self.assertNotIn('correctOptionIds:correctIds',route)
 def test_grading_false_by_default_and_exact_set(self):
  self.assertIn('answerKeyEnabled===true',KEY)
  self.assertIn('new Set(ids.filter(id=>allowed.has(id)))',KEY)
  self.assertIn('chosen.size===correct.size',KEY)
  self.assertIn('choices:options.map',KEY)
 def test_properties_canvas_and_independent_questions(self):
  self.assertIn('function ChoiceTruthEditor(',UI)
  self.assertIn('context question={w}',UI)
  self.assertIn('question={selectedQuestion}',UI)
  self.assertIn('question={q}',UI)
  self.assertIn('Resetta stati vero/falso',UI)
  self.assertIn('Risposta corretta!',UI)
  self.assertIn('Risposta sbagliata.',UI)
  self.assertNotIn('<p>Soluzione:</p>',UI)
  self.assertIn('feedbackOptionVerdict(feedback,o.id)',UI)
  self.assertIn('setFeedback(r.feedback||null)',UI)
  self.assertIn('submitted&&feedback&&',UI)
  self.assertIn('.widget-answer-feedback',STYLE)
 def test_key_edits_change_revision_but_not_typography(self):
  self.assertIn('w.answerKeyEnabled===true',REVISIONS)
  self.assertIn('part.answerKeyEnabled===true',REVISIONS)
  self.assertIn('questionRevisionAtHistory',SERVER)
 def test_preflight_is_before_npm(self):
  self.assertIn('test_rc187_answer_key_contracts',CI)
  self.assertLess(CI.index('test_rc187_answer_key_contracts'),CI.index('name: Install reproducibly'))
 def test_rejects_security_mutation(self):
  broken=SERVER.replace('gradeChoiceAnswer(part,widget.kind,existing.rows[0].answer_payload?.optionIds)','gradeChoiceAnswer(part,widget.kind,answer.optionIds)')
  self.assertNotIn('gradeChoiceAnswer(part,widget.kind,existing.rows[0].answer_payload?.optionIds)',broken)
 def test_rejects_missing_public_redaction(self):
  mutated=DOMAIN.replace('const {correctOptionId,correctOptionIds,...publicQuestion}=question','const publicQuestion=question')
  self.assertNotIn('const {correctOptionId,correctOptionIds,...publicQuestion}=question',mutated)
if __name__=='__main__':unittest.main()
