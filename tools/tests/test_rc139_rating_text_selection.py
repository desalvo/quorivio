from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
TEXT=(ROOT/'apps/web/src/widget-rich-editor.tsx').read_text()
SCALE=(ROOT/'apps/web/src/rating-choices.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()

class RC139RatingTextSelection(unittest.TestCase):
 def test_shared_rating_no_duplicate_editor_heading(self):
  self.assertEqual(UI.count('<RatingChoices'),3)
  self.assertIn("['rating','reactions','results-button'].includes(w.kind)?{...w,showTitle:false}:w",UI)
  self.assertIn('widget.showTitle!==false',UI)
  self.assertIn('readOnly||disabled||!onSelect',SCALE)
 def test_edit_text_mouse_without_moving_widget(self):
  self.assertIn("if(active)e.stopPropagation()",TEXT)
  self.assertIn("[contenteditable=true],[role=textbox]",UI)
  self.assertIn("if((e.target as HTMLElement).closest('[contenteditable=true]'))return",UI)
 def test_native_property_cursor_and_formatting_close(self):
  self.assertNotIn('e.currentTarget.select()',UI)
  self.assertIn('onClick={()=>setRibbonDismissed(true)}',UI)
  self.assertIn('active&&!ribbonDismissed',UI)
 def test_unified_16_by_9_padding(self):
  self.assertIn('padding:.55em!important',CSS)
  self.assertIn('min-height:0',CSS)

if __name__=='__main__':unittest.main()
