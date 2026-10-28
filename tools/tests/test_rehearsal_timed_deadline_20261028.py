"""Bounded stateless timed-rehearsal parity; no claims about real devices."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
TIMER=(ROOT/'apps/web/src/rehearsal-timer.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()
class RehearsalTimedDeadline(unittest.TestCase):
 def test_one_clock_for_presenter_and_participant(self):
  self.assertIn('const [pageStartedAt,setPageStartedAt]=useState',UI)
  self.assertIn('[activity?.id,seed]',UI)
  self.assertIn("openedAt={new Date(pageStartedAt).toISOString()}",UI)
  self.assertIn('kind===\'timed-quiz\'&&<PageTimer',UI)
 def test_deadline_is_checked_on_submit_not_just_on_render(self):
  self.assertIn('if(timedSeconds!==undefined&&rehearsalExpired(pageStartedAt,timedSeconds,Date.now()))return',UI)
  self.assertIn('disabled={!canInteract||!canSubmitRehearsalAnswer(answerMode,current)}',UI)
  self.assertIn('Tempo scaduto: risposta di prova non più inviabile',UI)
  self.assertIn('return !sent&&!rehearsalExpired(startedAt,seconds,now)',TIMER)
 def test_browser_gate_added_to_opt_in_chromium(self):
  self.assertIn('python3 tools/ci_rehearsal_timer_chromium.py',CI)
if __name__=='__main__':unittest.main()
