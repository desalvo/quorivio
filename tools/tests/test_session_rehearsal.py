import pathlib
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class SessionRehearsalContracts(unittest.TestCase):
 def test_preview_no_write_requests(self):
  web=(ROOT/'apps/web/src/main.tsx').read_text()
  block=web.split('function SessionRehearsal(',1)[1].split('function WidgetCanvas(',1)[0]
  self.assertNotIn('request<',block)
  self.assertNotIn('fetch(',block)
  self.assertIn('Ricomincia prova',block)
  self.assertIn('Simulazione locale',block)
 def test_launch_from_dashboard(self):
  web=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn('onClick={()=>setRehearsalOpen(true)}',web)
  self.assertIn('<SessionRehearsal snapshot={snap}',web)
 def test_postit_validated_both_sides(self):
  web=(ROOT/'apps/web/src/main.tsx').read_text()
  domain=(ROOT/'apps/api/src/domain.ts').read_text()
  self.assertIn("'postit','image','video','topic-question','timed-quiz','results-button'].includes(kind)",web)
  self.assertIn("'postit','image','video','topic-question','timed-quiz','results-button'].includes(w.kind)",domain)
