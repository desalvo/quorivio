"""Source-level protections for the mock-faithful autosaving editor.

Live React and server-backed persistence acceptance is provided by the manual
browser_test CI; these checks never claim to replace it.
"""
import json
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
MOCK=(ROOT/'tools/ci_browser_editor.py').read_text()
DB=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text()

class EditorMockAutosave(unittest.TestCase):
 def test_layout_has_brand_header_and_sole_exit(self):
  self.assertIn('className="editor-mock-header"',WEB)
  self.assertIn('src="/editor-quorivio-logo.svg" alt="Quorivio"',WEB)
  self.assertIn('className="page-editor-sidebar"',WEB)
  self.assertIn('className="editor-stage"',WEB)
  self.assertIn('className="editor-widget-rail"',WEB)
  self.assertNotIn('className="editor-bottom-controls"',WEB)
  self.assertNotIn('className="canvas-blank-menu-trigger"',WEB)
  self.assertTrue((ROOT/'apps/web/public/editor-quorivio-logo.svg').is_file())

 def test_autosave_verifies_server_readback(self):
  self.assertIn('const timer=window.setTimeout(()=>{if(!pendingPageSave.current)void updatePageDesign()},850)',WEB)
  self.assertIn('expected_design_revision:loadedDesignRevision.current',WEB)
  self.assertIn('verify_design_revision=${saved.design_revision}',WEB)
  self.assertIn('stableJson(persisted.page_design?.widgets||[])!==stableJson(question.widgets)',WEB)
  self.assertIn('autoSaveBlockedSignature===latestPageDraft.current',WEB)
  self.assertIn('Salvato automaticamente',WEB)
  self.assertIn('await updatePageDesign();if(latestPageDraft.current!==savedPageDraft.current)',WEB)

 def test_autosave_reports_success_only_after_server_confirmation(self):
  self.assertIn('let committed=false;',WEB)
  self.assertIn('committed=true;\n  setSnap(refreshed);',WEB)
  self.assertIn('return committed;',WEB)
  self.assertLess(WEB.index('stableJson(persisted.page_design?.widgets||[])'),WEB.index('committed=true;'))

 def test_context_is_gesture_driven(self):
  self.assertIn('onContextMenu={e=>{if((e.target as HTMLElement).closest(".widget-canvas-item"))return;',WEB)
  self.assertIn('contextHold.current=setTimeout(openBlankMenu,580)',WEB)
  self.assertIn('onPointerCancel={clearContextHold}',WEB)
  self.assertIn('>Salva ora</button>',WEB)
  self.assertNotIn('className="canvas-blank-menu-trigger"',WEB)

 def test_page_json_is_scoped_to_selected_thumbnail(self):
  self.assertIn('downloadPageDraftFor(a)',WEB)
  self.assertIn('openImportDraftFor(a,f)',WEB)
  self.assertIn('Esporta layout JSON',WEB)
  self.assertIn('Importa layout JSON',WEB)
  self.assertIn('planPageDraftRecovery(backup,revision)',WEB)
  self.assertIn('latestPageDraft.current!==signature',WEB)

 def test_seventeen_icons_are_unique(self):
  start=WEB.index('const icons:Record<string,React.ReactNode>=')
  mapping=WEB[start:WEB.index('return <>{icons[kind]',start)]
  icons=re.findall(r'(?:[a-z-]+|\'[a-z-]+\'):<([A-Za-z0-9]+) size=\{21\}',mapping)
  self.assertEqual(len(icons),17,icons)
  self.assertEqual(len(set(icons)),17,icons)

 def test_editor_uses_entire_viewport_and_mobile_three_column_grid(self):
  self.assertIn('.editor-ux-v2.powerpoint-editor:not(:fullscreen)',CSS)
  self.assertIn('width:100vw!important;height:100dvh!important',CSS)
  self.assertIn('grid-template-rows:68px minmax(0,1fr)',CSS)
  self.assertIn('grid-template-columns:clamp(84px,20vw,125px) minmax(0,1fr) clamp(51px,13vw,82px)',CSS)
  self.assertIn('aspect-ratio:16/9',CSS)

 def test_real_ci_accepts_autosave_and_mouse_touch(self):
  self.assertIn('await page.reload(wait_until=',MOCK)
  self.assertIn("state['revision']+=1",MOCK)
  self.assertIn("await expect(editor.get_by_text('Salvato automaticamente'))",MOCK)
  self.assertIn('Input.dispatchTouchEvent',MOCK)
  self.assertIn('await open_canvas_context(page)',MOCK)
  self.assertIn('await await_revision(context,sid,aid,3)',DB)
  self.assertIn("current['design_revision']==4",DB)
  self.assertIn('async def await_revision(',DB)
  self.assertIn('tools/ci_editor_mock_layout_chromium.py',WORKFLOW)
  self.assertLess(WORKFLOW.index('tools/ci_editor_mock_layout_chromium.py'),WORKFLOW.index('tools/ci_browser_editor.py'))

 def test_rc_not_promoted_without_new_ci_evidence(self):
  data=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  self.assertNotEqual(data.get('release_candidate_ready'),True)
  self.assertEqual({x['id']:x['status'] for x in data['gates']}['A2'],'partial')
