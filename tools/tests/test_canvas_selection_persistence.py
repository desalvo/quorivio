"""Prevent regressions that make in-canvas quiz configuration unusable."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'apps/web/src/main.tsx').read_text()


class CanvasSelectionPersistence(unittest.TestCase):
    def test_pointer_release_keeps_selected_widget(self):
        self.assertIn('function end(e:React.PointerEvent<HTMLDivElement>)', SOURCE)
        self.assertIn('gesture.current?.pointerId===e.pointerId', SOURCE)
        self.assertNotIn('function end(){gesture.current=null;setActive(null)}', SOURCE)

    def test_keyboard_and_click_select_widget(self):
        self.assertIn('if(e.target===e.currentTarget)setActive(w.id)', SOURCE)
        self.assertIn("toggleSelection(w.id)", SOURCE)
        self.assertIn("toggleSelection(w.id,true)", SOURCE)

    def test_removing_selected_widget_clears_selection(self):
        self.assertIn('setActive(null);setContextWidget(null)}}>Elimina', SOURCE)

if __name__ == '__main__':
    unittest.main()
