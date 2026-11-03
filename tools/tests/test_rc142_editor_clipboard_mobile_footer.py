"""RC142 contracts: page-local editing remains safe while clipboard spans pages."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text()
STYLE=(ROOT/'apps/web/src/style.css').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()

class RC142EditorFeatures(unittest.TestCase):
 def test_cross_page_clipboard_is_session_scoped_and_shortcuts_ignore_text_edits(self):
  clip=(ROOT/'apps/web/src/editor-cross-page-clipboard.ts').read_text()
  for mark in ('sessionId','structuredClone','saveEditorWidgetClipboard','readEditorWidgetClipboard'):
   self.assertIn(mark,clip)
  for mark in ("event.key==='Backspace'", "event.key==='Delete'",'copySelectedWidget()','pasteCopiedWidget()','readEditorWidgetClipboard(sessionId)',"[role=\"textbox\"]"):
   self.assertIn(mark,MAIN)
 def test_mobile_preview_available_everywhere_and_toggle_in_side_by_side(self):
  for mark in ('Anteprima smartphone','▯ Smartphone','Dispositivo partecipante','rehearsal-phone-frame',"mode==='mobile'"):
   self.assertIn(mark,MAIN)
  self.assertIn('width:min(390px,100%)',STYLE)
 def test_footer_format_and_scale_use_persisted_validated_fields(self):
  for mark in ('Font numero pagina','Dimensione numero pagina','Colore numero pagina','Padding destro numero pagina','Padding inferiore numero pagina','Dimensione emoji reazioni','Dimensione pulsanti gradimento','Allinea testo in basso'):
   self.assertIn(mark,MAIN)
  for mark in ('footerNumberPaddingRight','footerNumberPaddingBottom','footerNumberFontSize','footerNumberColor','ratingButtonSize'):
   self.assertIn(mark,DOMAIN)
  self.assertIn("'--footer-pad-right'",MAIN)
  self.assertIn('grid-template-rows:29px',STYLE)
 def test_hotfix_typescript_footer_properties_and_reactive_shared_clipboard(self):
  self.assertIn('as React.CSSProperties}>{item.text}',MAIN)
  self.assertIn('setClipboardAvailable(true)',MAIN)
  self.assertIn('disabled={!clipboardAvailable}',MAIN)
  self.assertNotIn('copiedWidgets',MAIN)
  self.assertIn('readEditorWidgetClipboard(sessionId)',MAIN)
 def test_closing_format_does_not_erase_widget_selection(self):
  self.assertIn('setRibbonDismissed(true)',MAIN)
  self.assertIn('Chiudi Formato widget',MAIN)
  self.assertNotIn('setRibbonDismissed(true);setSelectedWidgets([])',MAIN)

if __name__=='__main__':unittest.main()
