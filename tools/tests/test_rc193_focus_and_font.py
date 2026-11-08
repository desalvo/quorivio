"""Focus ownership, Arial defaults, answer typography, font-size arrows and CI guards."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
EDIT=(ROOT/'apps/web/src/widget-rich-editor.tsx').read_text()
STYLE=(ROOT/'apps/web/src/style.css').read_text()
OPTIONS=(ROOT/'apps/web/src/widget-answer-style.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()
class FocusAndFont(unittest.TestCase):
 def test_intermit_focus_is_not_restored_from_sibling(self):
  self.assertIn('document.activeElement===el',EDIT)
  self.assertIn('if(focused&&selection)',EDIT)
  self.assertIn('onBlur={()=>{remembered.current=null}}',EDIT)
  self.assertNotIn('if(active&&selection)restoreDomTextRange',EDIT)
  self.assertIn('el.textContent===value',EDIT)
 def test_numeric_input_and_arrows_are_always_available(self):
  self.assertIn('function WidgetFontSizeControl(',UI)
  self.assertIn('onApply={setSize}',UI)
  self.assertIn('Aumenta dimensione carattere di 1',UI)
  self.assertIn('Diminuisci dimensione carattere di 1',UI)
  self.assertIn('setDraft(value);const next=valid(value)',UI)
  self.assertIn('palette-ribbon-font-stepper button',STYLE)
 def test_arials_and_answer_styles_reach_original_and_independent_options(self):
  # RC257: the original raw fallback accepts the literal CSS face "undefined".
  # The validated helper must guard both the option and the submit button.
  self.assertIn('const family=safeWidgetFontFamily(style?.answerFontFamily,safeWidgetFontFamily(style?.fontFamily));',OPTIONS)
  self.assertIn('fontFamily:safeWidgetFontFamily(style?.submitFontFamily,safeWidgetFontFamily(style?.fontFamily))',OPTIONS)
  self.assertNotIn("style?.fontFamily||'Arial'",OPTIONS)
  self.assertIn("'--q-answer-font-family':family",OPTIONS)
  self.assertIn('canvas-subquestion-option{',STYLE)
  self.assertIn('font-family:var(--q-answer-font-family,Arial)!important',STYLE)
  # The answer-font selector must remain independently operable. Do not
  # pin the test to an unsafe, hardcoded fallback expression in UI source.
  self.assertIn('aria-label="Font campo risposta"',UI)
  self.assertIn('style:{...z.style,answerFontFamily:e.target.value}',UI)
 def test_preflight_is_before_build(self):
  self.assertIn('tools.tests.test_rc193_focus_and_font',CI)
  self.assertIn('apps/web/test/rc193-font-focus.test.ts',CI)
  self.assertLess(CI.index('tools.tests.test_rc193_focus_and_font'),CI.index('run: npm run build'))
