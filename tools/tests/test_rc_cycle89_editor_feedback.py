"""RC89 tests for user-reported editor regressions and safe persistence."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()

class RC89EditorFeedback(unittest.TestCase):
 def test_palette_is_horizontal_above_canvas_with_icon_and_caption(self):
  self.assertIn('className="editor-icon-caption"',UI)
  self.assertIn('.editor-ux-v2 .editor-widget-rail{grid-column:2!important;grid-row:2!important',CSS)
  self.assertIn('.editor-ux-v2 .editor-stage{grid-column:2!important;grid-row:3!important',CSS)
  self.assertIn('flex-direction:column!important',CSS)
  self.assertIn('padding:0!important;margin:0!important;overflow-x:auto',CSS)

 def test_resize_rotation_and_red_delete_are_real_handles(self):
  for marker in ('data-resize-edge','data-rotate-handle',"mode:'move'|'resize'|'rotate'",'onPointerMove={move}','onPointerUp={end}'):
   self.assertIn(marker,UI)
  self.assertIn('overflow:visible!important;touch-action:none!important',CSS)
  self.assertIn('.widget-canvas-item>.canvas-remove{position:absolute!important;top:2px!important;right:2px!important',CSS)
  self.assertIn("if(!window.confirm('Eliminare questo widget dal canvas?'))return",UI)

 def test_text_fields_are_visible_and_styled_in_editor_and_both_rehearsals(self):
  # RC132 introduced a shared, keyboard-resizable editor field (with the
  # Italian typographic apostrophe); RC134 replaced the old presenter label
  # with a non-interactive projection textarea and submit button.
  for marker in ('function EditorAnswerFieldPreview(',
                 'Casella di risposta libera nell’editor',
                 'Casella domanda libera nell’editor',
                 'className="widget-answer-height-handle"',
                 'onKeyDown={e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;',
                 'Risposta simulata ',
                 'widget-free-answer-field',
                 'Colore sfondo casella risposta libera',
                 'Casella per la domanda, sola anteprima presentatore',
                 'className="outline small projection-readonly-submit" disabled tabIndex={-1}'):
   self.assertIn(marker,UI)
  # RC128 uses the same text-area geometry for both rehearsal viewers and
  # makes the presenter preview read-only, with its real submit disabled.
  self.assertIn("aria-label={'Risposta simulata '+key}",UI)
  self.assertIn("readOnly={viewer==='presenter'}",UI)
  self.assertIn("{viewer==='presenter'?'Invia risposta':'Invia risposta di prova'}",UI)
  self.assertIn('disabled={!canInteract||!canSubmitRehearsalAnswer(answerMode,current)}',UI)
  self.assertIn('answerFillColor?:string',DOMAIN)
  # RC109/110/113 extended the allowed fields. Verify that answerFillColor is
  # still in the API allowlist *and* its strict hex-color validation instead
  # of freezing the precise order of an obsolete three-field source literal.
  self.assertRegex(DOMAIN,r"Object\.keys\(v\).*?'answerFillColor'.*?\.includes\(k\)")
  self.assertRegex(DOMAIN,r"\['fillColor','answerFillColor','strokeColor','gradientEndColor'\]\.every")
  self.assertIn('answerInputStyle(w.style)',UI)
  self.assertIn('answerInputStyle(marks.style)',UI)
  self.assertIn('answerInputStyle(widget.style)',UI)

 def test_single_headings_in_reaction_results_and_participant_widgets(self):
  for kind in ('results-button','reactions','participant-count'):
   self.assertIn('[data-widget-kind="'+kind+'"]',CSS)
  self.assertIn('>.widget-rich-inline{position:absolute!important',CSS)

 def test_background_picker_is_hidden_but_upload_persists(self):
  self.assertIn('style={{display:"none"}} aria-hidden="true" tabIndex={-1} type="file"',UI)
  # RC110 intentionally keeps the menu open on upload failure: a blind
  # .then(()=>close) would mask server rejections and break the user's JPG flow.
  self.assertIn('onBackgroundUpload(file).then(applied=>{if(applied)',UI)
  self.assertIn("setBackgroundUploadStatus('Sfondo caricato e applicato.');setBackgroundMenu(false)",UI)
  self.assertIn("else setBackgroundUploadStatus('Caricamento annullato:",UI)
  self.assertIn(".catch(error=>{setBackgroundUploadStatus('Caricamento non riuscito:",UI)
  self.assertNotIn('onBackgroundUpload(file).then(()=>setBackgroundMenu(false))',UI)
  self.assertIn('Carica immagine nello sfondo e nella libreria…',UI)
  self.assertIn("const endpoint=`/api/sessions/${encodeURIComponent(selected)}/${library}`",UI)
  self.assertIn("const applied=await uploadNamedFile(file,mime,'backgrounds')",UI)
  self.assertIn('setQuestionBackgroundAsset(applied.id)',UI)

 def test_preview_buttons_open_real_dialog_and_submit_is_legible(self):
  self.assertIn('aria-haspopup="dialog" aria-expanded={rehearsalOpen&&rehearsalMode===m}',UI)
  self.assertIn('setRehearsalMode(m);setRehearsalOpen(true)',UI)
  self.assertIn('onClose={()=>setRehearsalOpen(false)}',UI)
  self.assertIn('.widget-question>button.outline',CSS)
  self.assertIn('-webkit-text-fill-color:#142c43!important',CSS)

 def test_title_and_footer_schema_editor_are_editable(self):
  self.assertIn('Editor schema · Titolo sessione',UI)
  self.assertIn('Schema footer della pagina',UI)
  self.assertIn('footerShowPageNumber:e.target.checked',UI)
  self.assertIn('footerShowSessionTitle:e.target.checked',UI)
  self.assertIn('newFooterWidget(crypto.randomUUID())',UI)

 def test_preflight_is_early_and_integrity_is_retained(self):
  self.assertIn('test_rc_cycle89_editor_feedback',CI)
  self.assertLess(CI.index('test_rc_cycle89_editor_feedback'),CI.index('npm install --ignore-scripts'))
  self.assertIn('verify_rc_cycle88_inventory.py --historical',CI)
  self.assertIn('verify_rc_cycle89_inventory.py',CI)

if __name__=='__main__':unittest.main()
