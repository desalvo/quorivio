from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[2]
UI=(R/'apps/web/src/main.tsx').read_text()
TEXT=(R/'apps/web/src/widget-rich-editor.tsx').read_text()
STYLE=(R/'apps/web/src/widget-text-marks.ts').read_text()
ANSWER=(R/'apps/web/src/widget-answer-style.ts').read_text()
CSS=(R/'apps/web/src/style.css').read_text()

class RC140ScopeParity(unittest.TestCase):
 def test_invasive_layer_icons_removed_but_context_actions_retained(self):
  self.assertNotIn('className="canvas-layer-tools"',UI)
  for title in ('Duplica</button>','Porta avanti</button>','Porta indietro</button>'):self.assertIn(title,UI)
 def test_explicit_scope_and_proportional_whole_widget_scaling(self):
  for flag in ('Ambito della formattazione','Widget intero','Titolo</option>','Descrizione</option>','Risposte</option>','Scala proporzionale di tutti i testi'):self.assertIn(flag,UI)
  self.assertIn('scaleAllWidgetTypography(w,1.1)',UI)
  self.assertIn('answerFontSize:scale(',STYLE)
  self.assertIn('fontSize:scale(mark.style.fontSize',STYLE)
 def test_caret_and_answers_style_parity(self):
  self.assertIn('data-widget-text-field={field}',TEXT)
  self.assertIn('targetField=(e.target as HTMLElement).closest',UI)
  self.assertIn('formatSelectedOrEntireField(',UI)
  self.assertIn('applyAllWidgetTypeface(w,changes',UI)
  self.assertIn('style={answerOptionStyle(w.style)}',UI)
  self.assertIn('answerOptionStyle(marks.style)',UI)
  self.assertIn('answerFontFamily: e.target.value', UI.replace('answerFontFamily:e.target.value','answerFontFamily: e.target.value'))
  self.assertIn('const size=`${((style?.answerFontSize',ANSWER)
  self.assertIn('fontSize:size',ANSWER)
  self.assertIn('onKeyDownCapture={e=>',UI)
 def test_editor_and_preview_shared_text_wrapping(self):
  self.assertIn('canvas-widget-answer-preview[data-answer-mode]',CSS)
  self.assertIn('white-space:normal!important',CSS)

if __name__=='__main__':unittest.main()
