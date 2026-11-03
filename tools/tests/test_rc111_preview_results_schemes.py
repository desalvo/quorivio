"""RC111 safeguards for preview portals, results text wrapping and access to schemes."""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()

class PreviewAndResults(unittest.TestCase):
 def test_preview_openers_keep_modes_and_portal(self):
  self.assertIn("(['presenter','participant','mobile','both'] as RehearsalMode[]).map",MAIN)
  self.assertIn('setRehearsalMode(m);setRehearsalOpen(true)',MAIN)
  self.assertIn('Dispositivo partecipante',MAIN)
  self.assertIn('Anteprima smartphone',MAIN)
  self.assertIn("return createPortal(<div className=\"rehearsal-backdrop\"",MAIN)
  self.assertIn('document.body);',MAIN)
  self.assertRegex(CSS,r'body\s*>\s*\.rehearsal-backdrop\s*\{[^}]*z-index:\s*15000',)
  self.assertIn('editor-floating-panel',CSS)
 def test_long_answers_and_source_wrap_not_ellipsis(self):
  self.assertRegex(CSS,r'\.linked-results\s*>\s*strong,\s*\.linked-results\s*>\s*small,\s*\.linked-results-row\s*>\s*span\s*\{[^}]*white-space:normal!important')
  self.assertRegex(CSS,r'\.linked-results-row\s*\{[^}]*min-width:0')
  self.assertIn('overflow-wrap:anywhere!important',CSS)
  self.assertIn('className="linked-results-items"',MAIN)
 def test_schema_editor_discoverable_from_dashboard_and_fullscreen_editor(self):
  self.assertIn('dashboard-schemes-shortcut',MAIN)
  self.assertIn('aria-label="Apri editor degli schemi della sessione"',MAIN)
  self.assertIn('editor-schemes-open',MAIN)
  self.assertIn('if(confirmPageNavigation()){setRehearsalOpen(false);setInspectedWidget(\'\');openSchemaEditor()}',MAIN)
  self.assertIn("setDashboardPage('master')",MAIN)
 def test_scheme_editor_still_validates_concurrent_edits(self):
  self.assertIn('const fresh=await request<Snapshot>(`/sessions/${selected}`)',MAIN)
  self.assertIn('schemaBaseline.current',MAIN)
  self.assertIn("if(!confirmSchemaNavigation())return",MAIN)

if __name__=='__main__': unittest.main()
