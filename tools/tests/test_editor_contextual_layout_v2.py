"""Quorivio 0.1.0-dev: editor visual redesign interaction and safety contracts.

Real browser visual/device acceptance is provided by the opt-in Chromium workflow.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
WEB = (ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
CSS = (ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
BROWSER = (ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf-8')

class ContextualEditorUX(unittest.TestCase):
    def test_widget_palette_only_icons_with_accessible_names(self):
        self.assertIn('editorWidgetKinds.map(k=><EditorIconTool', WEB)
        self.assertIn('label={`Aggiungi widget: ${editorWidgetNames[k]}`}', WEB)
        self.assertIn('<EditorWidgetIcon kind={k}/>', WEB)
        self.assertNotIn('className="widget-palette"', WEB)

    def test_touch_focus_hover_tooltip(self):
        self.assertIn("if(e.pointerType!=='mouse')showTip()", WEB)
        self.assertIn('className="editor-icon-tool" data-widget-kind={kind} aria-label={label}', WEB)
        self.assertNotIn('className="editor-icon-tool" title={label}',WEB)
        self.assertIn('role="tooltip"', WEB)
        self.assertIn('.editor-floating-tooltip', CSS)
        self.assertIn('createPortal(<span className=', WEB)
        self.assertIn(':focus-within', CSS)

    def test_thumbnail_is_preview_only(self):
        self.assertIn('page-editor-preview-widget', WEB)
        self.assertIn('page-editor-thumb-number', WEB)
        self.assertIn('page-editor-thumb-menu-trigger', WEB)
        self.assertNotIn('className="page-editor-thumb-actions"', WEB)
        self.assertIn('onClick={()=>beginPageDesign(a)}',WEB)

    def test_touch_help_for_visible_text_controls(self):
        self.assertIn("button.title||button.getAttribute('aria-label')||button.textContent?.trim()", WEB)
        self.assertIn('role="status" aria-live="polite"', WEB)
        self.assertIn('editor-touch-assist', CSS)

    def test_creation_respects_unsaved_changes(self):
        self.assertIn("async function createCanvasPageAt(anchorId?:string,where:'before'|'after'='after'){\n if(!confirmPageNavigation())return;",WEB)

    def test_thumbnail_drag_and_keyboard_reordering(self):
        self.assertIn("setData('application/x-quorivio-page',a.id)", WEB)
        self.assertIn('void dropPage(dragged,a.id)', WEB)
        self.assertIn("['ArrowUp','ArrowDown','Home','End']", WEB)
        self.assertIn('void movePage(i,i-1)', WEB)
        self.assertIn('void movePage(i,i+1)', WEB)

    def test_page_menu_relative_insert_and_duplicate(self):
        self.assertIn("createCanvasPageAt(a.id,'before')",WEB)
        self.assertIn("createCanvasPageAt(a.id,'after')",WEB)
        self.assertIn('ids.splice(at+1,0,copy.id)',WEB)
        self.assertIn("`/sessions/${selected}/pages/order`",WEB)
        self.assertIn("aria-expanded={pageThumbMenu===a.id}",WEB)

    def test_page_context_not_ribbon(self):
        self.assertIn('onOpenPageSettings={()=>',WEB)
        self.assertIn('onContextMenu={e=>{if((e.target as HTMLElement).closest(".widget-canvas-item"))return',WEB)
        self.assertIn('pageContextOpen&&<section className="editor-context-drawer"',WEB)
        self.assertNotIn('className="canvas-blank-menu-trigger"',WEB)
        self.assertIn('contextHold.current=setTimeout(openBlankMenu,580)',WEB)
        self.assertNotIn('className="editor-heading"',WEB)

    def test_widget_context_properties_are_scoped(self):
        self.assertIn("onInspectWidget={id=>",WEB)
        self.assertIn("filter(x=>x.w.id===inspectedWidget)",WEB)
        self.assertIn('className="canvas-context-properties"', WEB)
        self.assertIn('Proprietà widget',WEB)

    def test_save_and_merge_unchanged(self):
        self.assertIn('onClick={updatePageDesign}', WEB)
        self.assertIn('pageHasUnsavedChanges||pageSavePending||pageConflict', WEB)
        self.assertIn('applyPageRebase()', WEB)
        self.assertIn('downloadPageDraft', WEB)

    def test_visual_asset_local_and_responsive(self):
        asset=ROOT/'apps/web/public/editor-alpine-atmosphere.webp'
        self.assertGreater(asset.stat().st_size,10_000)
        self.assertIn("url('/editor-alpine-atmosphere.webp')",CSS)
        self.assertIn('@media(max-width:760px)',CSS)
        self.assertIn('backdrop-filter:blur',CSS)

    def test_browser_scenarios_include_context_and_touch(self):
        self.assertIn('await open_canvas_context(page)',BROWSER)
        self.assertIn("await page.set_viewport_size({'width':420,'height':860})",BROWSER)
        self.assertIn("await expect(editor.get_by_role('img',name='Quorivio'))",BROWSER)

if __name__=='__main__':unittest.main()
