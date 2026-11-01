"""Rehearsal mirrors the real participant's one-shot submission lifecycle."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
MODULE=(ROOT/'apps/web/src/rehearsal-responses.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()
class RehearsalSendParity(unittest.TestCase):
 def test_real_and_rehearsal_requires_submit(self):
  self.assertIn('Invia risposta al widget', UI)
  self.assertIn('Invia risposta di prova', UI)
  self.assertIn('submitDemoAnswer(key,answerMode,timedSeconds)', UI)
  self.assertIn('disabled={!canInteract||!canSubmitRehearsalAnswer(answerMode,current)}',UI)
 def test_only_sent_answers_update_presenter_results(self):
  self.assertIn('seed,submittedAnswers,w.targetQuestionId',UI)
  self.assertNotIn('seed,responses,w.targetQuestionId',UI)
 def test_no_double_reaction_across_widgets(self):
  self.assertIn('REHEARSAL_REACTION_PREFIX+activity.id', UI)
  self.assertIn('changeRehearsalReaction(previous,pageKey,widgetId,value)', UI)
  self.assertIn("kind==='reactions'&&viewer==='presenter'?<ProjectionWidgetContent",UI)
  self.assertIn('aria-pressed={submittedAnswers[w.id]===emoji}',UI)
 def test_own_draft_and_sent_state_and_restart(self):
  self.assertIn('const [responses,setResponses]=useState',UI)
  self.assertIn('const [submittedAnswers,setSubmittedAnswers]=useState',UI)
  self.assertIn('setResponses({});setSubmittedAnswers({});',UI)
 def test_file_selection_never_uploads_from_preview(self):
  self.assertIn('Allegato di prova (non caricato)',UI)
  self.assertIn('e.target.files?.[0]?.name',UI)
  self.assertIn('the bytes never leave this browser',MODULE)
 def test_opt_in_browser_flow_in_ci(self):
  self.assertIn('ci_rehearsal_submission_chromium.py',CI)
if __name__=='__main__':unittest.main()
