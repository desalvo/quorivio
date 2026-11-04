"""RC86: the native Chromium widget palette gate must track real widget semantics.

The historic hard-coded 17 tools predates the Title and Footer features and
silently blocks real Chromium acceptance after other browser tests succeed.
"""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
PROBE=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC86WidgetPalette(unittest.TestCase):
 def test_current_palette_exposes_title_and_footer_with_all_legacy_widgets(self):
  m=re.search(r"const editorWidgetKinds=\[([^]]+)\] as const", UI)
  self.assertIsNotNone(m)
  kinds=re.findall(r"'([^']+)'",m.group(1))
  self.assertEqual(len(kinds),len(set(kinds)))
  self.assertGreaterEqual(len(kinds),19)
  for required in ('text','question','reactions','participant-count','title','footer'):
   self.assertIn(required,kinds)
  # Shape/line tools use a contextual-preset inserter; other tools keep
  # accessible palette buttons, including title and footer.
  self.assertIn("editorWidgetKinds.map(k=>k==='shape'||k==='line'?<GraphicInsertTool",UI)
  self.assertIn(':<EditorIconTool key={k}',UI)
  self.assertIn('kind={k} disabled={pageWidgets.length>=16}',UI)
  self.assertIn('label={`Aggiungi widget: ${editorWidgetNames[k]}`}',UI)
 def test_browser_uses_real_widget_kinds_not_obsolete_fixed_count(self):
  self.assertNotIn('buttons.count()==17',PROBE)
  self.assertIn('els.map(e=>e.dataset.widgetKind || e.dataset.graphicPalette)',PROBE)
  self.assertIn("graphics=palette.locator('button.editor-icon-tool[data-graphic-palette]')",PROBE)
  self.assertIn('required<=set(kinds)',PROBE)
  self.assertIn('len(kinds)==len(set(kinds))',PROBE)
  self.assertIn("'title','footer'",PROBE)
 def test_icons_and_accessible_labels_remain_verified_in_real_browser(self):
  self.assertIn('e.getAttribute("aria-label")',PROBE)
  self.assertIn("label.startswith('Aggiungi widget: ')",PROBE)
  self.assertIn('len(set(names))==len(names)',PROBE)
  self.assertIn('e.hasAttribute("title")',PROBE)
  self.assertIn("await page.get_by_role('button',name='Aggiungi widget: Testo').click()",PROBE)
 def test_preflight_runs_before_expensive_ci_jobs_and_keeps_real_browser(self):
  self.assertIn('tools.tests.test_rc_cycle86_palette_acceptance',WORKFLOW)
  self.assertLess(WORKFLOW.index('tools.tests.test_rc_cycle86_palette_acceptance'),WORKFLOW.index('npm install --ignore-scripts'))
  self.assertIn('python3 tools/ci_browser_editor.py',WORKFLOW)
