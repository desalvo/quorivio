"""RC286 final release contracts for .quo, authoring UX and manuals.

Do not confuse the Quorivio vendor MIME prefix or internal hidden temporary
folders with the portable session filename extension.
"""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
API=(ROOT/'apps/api/src/server.ts').read_text()
TRANSFER=(ROOT/'apps/web/src/session-local-transfer.ts').read_text()
SHOT=(ROOT/'tools/ci_manual_real_screenshots.py').read_text()
CATALOG=(ROOT/'tools/manual_screenshot_catalog.py').read_text()

class RC286AuthoringManuals(unittest.TestCase):
 def test_local_session_extension_is_only_quo(self):
  for text in (WEB,API,TRANSFER,(ROOT/'apps/web/test/rc285-local-session-transfer.test.ts').read_text()):
   self.assertNotRegex(text,r'\b(?:import|export)\.quorivio\b')
   self.assertNotRegex(text,r'\.quorivio\b(?=[\x27\"` ])')
  self.assertIn("'/api/sessions/import.quo'",WEB)
  self.assertIn("'/api/sessions/import.quo'",API)
  self.assertIn('quorivio-session.quo',API)
  self.assertIn("return `quorivio-${base||'sessione'}.quo`",TRANSFER)
  self.assertIn('application/vnd.quorivio.session+zip',TRANSFER,'MIME vendor identity is not an archive extension')
 def test_attachment_panel_is_native_and_closed_by_default(self):
  self.assertIn('<details className="panel dashboard-attachments-collapsible"',WEB)
  self.assertIn('<summary>Allegati della sessione',WEB)
  self.assertNotIn('<details open className="panel dashboard-attachments-collapsible"',WEB)
  self.assertIn('.dashboard-attachments-collapsible>summary:focus-visible',CSS)
 def test_thumbnails_show_draft_choices_and_media(self):
  self.assertIn('designActivity===a.id?pageWidgets',WEB)
  self.assertIn('<ThumbnailWidgetContent widget={w}',WEB)
  self.assertIn('thumb-option',WEB)
  self.assertIn('page-editor-preview-real-image',WEB)
  self.assertIn('thumb-chart-bars',WEB)
  self.assertIn('never present fabricated live response counts',CSS)
 def test_long_context_menu_scrolls_without_dismissing(self):
  self.assertIn("event.target.closest('.canvas-context-menu')",WEB)
  self.assertIn('onWheel={e=>e.stopPropagation()}',WEB)
  self.assertIn('onTouchMove={e=>e.stopPropagation()}',WEB)
  self.assertIn('position:fixed!important',CSS)
  self.assertIn('overscroll-behavior:contain',CSS)
  self.assertIn("context?'V/F'",WEB)
  self.assertIn("context?'F':'Falso'",WEB)
 def test_capture_has_more_live_views_and_schema_editor(self):
  for name in ('editor-schema','editor-thumbnails-widgets','editor-widget-context',
               'rehearsal-participant','rehearsal-side-by-side','participant-widescreen'):
   self.assertIn("'"+name+"'",SHOT)
   self.assertIn("'"+name+"'",CATALOG)
  self.assertIn('minimum=18',SHOT)
  self.assertIn("if await attachments.evaluate('(el)=>el.open')",SHOT)
 def test_all_six_manuals_are_expanded_illustrated_and_current(self):
  for role in ('admin','presenter','user'):
   for lang in ('it','en'):
    text=(ROOT/f'docs/manuals-src/{role}-guide.{lang}.md').read_text()
    self.assertIn('RC'+str(__import__('tools.manual_release_metadata',fromlist=['CYCLE']).CYCLE),text)
    self.assertIn('<!-- REAL_SCREENSHOT_GALLERY -->',text)
    self.assertIn('workflow-',text)
    self.assertIn('manual-evidence-rc283/',text)
    self.assertNotRegex(text,r'\b(?:0bb89e6ac79e|bd9141fb671c|[a-f0-9]{40})\b')
  for lang in ('it','en'):
   self.assertIn('.quo',(ROOT/f'docs/manuals-src/presenter-guide.{lang}.md').read_text())
  self.assertIn("'build': f'RC{CYCLE}'",(ROOT/'tools/manual_release_metadata.py').read_text())
  self.assertNotIn(' · Commit ',CATALOG)
 def test_pdf_metadata_and_no_commit_ids(self):
  import fitz
  for role in ('admin','presenter','user'):
   for lang in ('it','en'):
    path=ROOT/f'docs/manuals/{role}-guide.{lang}.pdf'
    doc=fitz.open(path)
    body='\n'.join(page.get_text() for page in doc)
    self.assertIn('RC'+str(__import__('tools.manual_release_metadata',fromlist=['CYCLE']).CYCLE),body)
    self.assertNotRegex(body,r'\b(?:commit|Commit)\s+[0-9a-f]{8,40}\b')
    self.assertNotIn('.quorivio',body)
    self.assertGreaterEqual(len(doc),30)
    self.assertGreaterEqual(sum(len(p.get_image_info()) for p in doc),10)
    doc.close()

if __name__=='__main__':unittest.main()
