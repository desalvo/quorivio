"""RC109: editor answer controls and one-line centered footer remain contractual."""
from pathlib import Path
import unittest
R = Path(__file__).resolve().parents[2]
MAIN = (R/'apps/web/src/main.tsx').read_text()
DOMAIN = (R/'apps/api/src/domain.ts').read_text()
CSS = (R/'apps/web/src/style.css').read_text()

class EditorAnswerAndFooterRC109(unittest.TestCase):
 def test_response_submit_preview_including_nested_questions(self):
  self.assertIn('requiresAnswerSubmit(w.kind)&&<button',MAIN)
  self.assertIn('canvas-widget-submit-preview',MAIN)
  self.assertIn('Anteprima invio risposta della domanda',MAIN)
  self.assertIn('answerSubmitStyle(w.style)',MAIN)

 def test_answer_fields_are_styled_across_real_and_rehearsal(self):
  self.assertIn('style={answerInputStyle(marks.style)}',MAIN)
  self.assertGreaterEqual(MAIN.count('style={answerInputStyle(w.style)}'),3)
  self.assertIn('style={answerInputStyle(widget.style)}',MAIN)
  self.assertIn('style={answerOptionStyle(marks.style)}',MAIN)
  self.assertIn('style={answerOptionStyle(w.style)}',MAIN)

 def test_custom_properties_are_backend_validated(self):
  for x in ['answerFontFamily','answerFontSize','answerColor','answerBold','answerItalic','submitButtonSize','autoFit']:
   self.assertIn(x,DOMAIN)
  self.assertIn('w.autoFit===undefined||typeof w.autoFit',DOMAIN)

 def test_manual_geometry_disables_autofit_and_can_be_reenabled(self):
  self.assertIn('autoFit:false',MAIN)
  self.assertIn('autoFit:e.shiftKey?false:item.autoFit',MAIN)
  self.assertIn("widgetMayAutoFit(w.kind,w.autoFit)",MAIN)
  self.assertIn("Adatta automaticamente l'altezza al contenuto",MAIN)
  self.assertIn('autoFitExpandedPosition',MAIN)

 def test_footer_title_centered_with_separator(self):
  self.assertIn('box-shadow:inset 0 1px 0',CSS)
  self.assertIn('data-widget-kind="footer"]>.widget-rich-inline',CSS)
  self.assertIn('text-align:center!important',CSS)
  self.assertIn('newFooterWidget',MAIN)

if __name__=='__main__':unittest.main()
