from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
SRC=(ROOT/'apps/web/src/main.tsx').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
class PresenterLinkedPreview(unittest.TestCase):
 def test_presenter_only_result_control(self):
  self.assertIn("w.kind==='results-button'?<PresenterLinkedResult",SRC)
  self.assertIn("w.kind!=='results-button'",SRC)
  self.assertIn("w.kind==='results-button'?null",SRC)
 def test_results_source_is_page_scoped(self):
  self.assertIn('Widget sorgente statistiche',SRC)
  self.assertIn('targetWidgetId',DOMAIN)
  self.assertIn('const target=d.widgets.find',DOMAIN)
 def test_two_preview_modes_both_entrypoints(self):
  self.assertIn("initialMode={rehearsalMode}",SRC)
  self.assertIn('Anteprime affiancate',SRC)
  self.assertIn('▣ Affiancate',SRC)
  self.assertIn('rehearsal-mode-both',CSS)
 def test_preview_reaction_local_state(self):
  self.assertIn("onClick={()=>submitDemoDirect(w.id,'reactions',emoji)}",SRC)
  self.assertIn("submittedAnswers[REHEARSAL_REACTION_PREFIX+activity.id]",SRC)
  self.assertIn('Nessuna risposta di prova viene salvata',SRC)
 def test_one_full_widget_and_one_selected_text_style_path(self):
  self.assertIn('formatTextRange(w.textMarks||[]',SRC)
  self.assertIn('editing===w.id',SRC)
  self.assertIn('patch(w.id,{style:{...style,...changes}})',SRC)
  self.assertIn('Dimensione del testo',SRC)
  self.assertIn('Font del testo',SRC)
if __name__=='__main__':unittest.main()
