"""Contract for separate full-content session navigation and resilient dashboard."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
class SessionFullPageNavigation(unittest.TestCase):
 def test_separate_sidebar_destinations(self):
  ui=(ROOT/'apps/web/src/main.tsx').read_text()
  for label in ["['new','Nuova sessione']","['open','Apri sessione']","['calendar','Calendario']"]:self.assertIn(label,ui)
  for pane in ["dashboardPage==='new'", "dashboardPage==='open'", "dashboardPage==='calendar'", "dashboardPage!=='session'"]:self.assertIn(pane,ui)
  self.assertIn("setSelected(s.id);setSnap(null);setDashboardPage('session')",ui)
  self.assertIn("setSessionTab('pages')",ui)
 def test_reflow_and_invitation(self):
  css=(ROOT/'apps/web/src/style.css').read_text()
  self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',css)
  self.assertIn('.session-tab-pages .invitation-panel',css)
 def test_no_new_reference_date_picker(self):
  ui=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertNotIn('Data facoltativa<input',ui)
if __name__=='__main__':unittest.main()
