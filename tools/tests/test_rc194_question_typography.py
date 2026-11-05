"""RC194 regression: formatting hierarchy, long answers and safe rich selection."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text()
RICHTEXT=(ROOT/'apps/web/src/widget-rich-editor.tsx').read_text()
MARKS=(ROOT/'apps/web/src/widget-text-marks.ts').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
DEFAULTS=(ROOT/'apps/web/src/widget-typography-defaults.ts').read_text()
STAGE=(ROOT/'apps/web/src/stage-widget-typography.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()

class RC194QuestionTypography(unittest.TestCase):
    def test_question_default_hierarchy_is_same_everywhere(self):
        self.assertIn('QUESTION_TITLE_SIZE=22',DEFAULTS)
        self.assertIn('QUESTION_ANSWER_SIZE=16',DEFAULTS)
        self.assertIn("fontFamily:style?.fontFamily||'Arial'",DEFAULTS)
        self.assertIn('bold:style?.bold??true',DEFAULTS)
        self.assertIn('answerBold:style?.answerBold??false',DEFAULTS)
        self.assertIn('widgetTextDefaults(widget.kind,widget.style)',STAGE)
        self.assertIn('widgetTextDefaults(w.kind,w.style)',MAIN)

    def test_existing_user_styles_are_not_reset(self):
        self.assertIn('fontSize:style?.fontSize??QUESTION_TITLE_SIZE',DEFAULTS)
        self.assertIn("answerFontFamily:style?.answerFontFamily||style?.fontFamily||'Arial'",DEFAULTS)

    def test_all_widget_faces_reach_answers_and_subquestions(self):
        self.assertIn('answerFontFamily:change.fontFamily',MARKS)
        self.assertIn('const marks=(widget.textMarks||[]).map',MARKS)
        self.assertIn('font-family:var(--q-answer-font-family,inherit)!important',CSS)
        self.assertIn('answerOptionStyle(w.style)',MAIN)
        self.assertIn('const format=widgetTextDefaults(source.kind,source.style)||{}',MAIN)

    def test_selected_range_is_restored_after_reformatting(self):
        self.assertIn('restoreDomTextRange(text,range)',MAIN)
        self.assertIn('text.focus({preventScroll:true})',MAIN)
        self.assertIn('document.activeElement===el',RICHTEXT)
        self.assertIn('onBlur={()=>{remembered.current=null}}',RICHTEXT)

    def test_font_insertion_uses_previous_glyph(self):
        self.assertIn('styleOfPreviousCharacter(oldText,marks,field,first)',MARKS)
        self.assertIn('applySelectionInlineStyle(shifted,field,newText,first,endNew,inherited)',MARKS)

    def test_multiline_options_remain_fully_visible(self):
        self.assertIn('RC194: long answers wrap',CSS)
        self.assertRegex(CSS,r'white-space:pre-wrap!important;overflow-wrap:anywhere!important;min-width:0!important')
        self.assertIn('height:auto!important',CSS)

    def test_early_ci_and_actual_browser_css_guard(self):
        self.assertIn('test_rc194_question_typography',CI)
        self.assertIn('rc194-question-typography.test.ts',CI)
        self.assertIn('ci_rc194_answer_typography_chromium.py',CI)

if __name__=='__main__': unittest.main()
