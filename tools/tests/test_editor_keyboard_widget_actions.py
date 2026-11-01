import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[2] / "apps/web/src/main.tsx"

class EditorWidgetKeyboardActions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_delete_backspace_remove_focused_widget(self):
        self.assertIn("e.key==='Delete'||e.key==='Backspace'", self.source)
        self.assertIn('onChange(deleteWidgetSelection(widgets,ids))', self.source)
        self.assertIn('selectedWidgets.includes(w.id)?selectedWidgets:[w.id]', self.source)

    def test_typing_in_form_fields_is_not_intercepted(self):
        snippet = self.source.split('function keyboardGeometry', 1)[1].split('function end()', 1)[0]
        self.assertLess(snippet.index("closest('input,textarea,button,select,[contenteditable=true]')"), snippet.index("e.key==='Delete'"))

    def test_key_commands_are_announced_and_clean_selection(self):
        self.assertIn('Alt+ArrowDown Delete Backspace Escape', self.source)
        self.assertIn('setActive(null);setContextWidget(null);setEditing(null)', self.source)

if __name__ == "__main__":
    unittest.main()
