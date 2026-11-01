"""RC120: conflict status visible, test integrated before real PostgreSQL acceptance."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class RC120ConflictStatus(unittest.TestCase):
 def test_conflict_status_does_not_collapse_in_header(self):
  css=(ROOT/'apps/web/src/style.css').read_text()
  self.assertIn('.editor-ux-v2 .editor-autosave-indicator{flex:0 0 auto;min-width:125px',css)
  self.assertIn('.editor-ux-v2 .editor-mock-brand{flex:1 1 0;overflow:hidden}',css)
  self.assertIn('.editor-ux-v2 .editor-autosave-indicator.has-error{position:absolute',css)
  self.assertIn('overflow:visible;text-overflow:clip',css)
 def test_revision_conflict_is_error_style_even_without_save_error(self):
  src=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn("(pageSaveError||pageConflict)?' has-error'",src)
  self.assertIn("pageConflict?'Conflitto di revisione'",src)
 def test_real_chromium_guard_precedes_database_conflict_acceptance(self):
  wf=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('RC120 always-visible autosave conflict regression before npm',wf)
  self.assertLess(wf.index('python3 tools/ci_browser_editor_conflict_visibility.py'),wf.index('python3 tools/ci_browser_editor_postgres.py'))
  browser=(ROOT/'tools/ci_browser_editor_conflict_visibility.py').read_text()
  self.assertIn("for width in (1440, 1100, 960, 390):",browser)
  self.assertIn("await expect(status).to_be_visible()",browser)
  self.assertIn("values['scroll'] <= values['w'] + 3",browser)
  self.assertIn("Conflitto di revisione",browser)
  postgres=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
  self.assertIn("await expect(editor.get_by_text('Conflitto di revisione')).to_be_visible(timeout=12000)",postgres)
