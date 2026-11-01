import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[2] / "apps/web/src/main.tsx"

class CanvasPointerSafety(unittest.TestCase):
    def test_form_fields_do_not_begin_canvas_drag(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("closest('button,input,select,textarea,[contenteditable=true]')", source)

    def test_lost_pointer_capture_restores_initial_geometry(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn('onPointerCancel={cancelGesture} onLostPointerCapture={cancelGesture}', source)
        self.assertIn('onChange(g.groupBase||widgets)', source)

if __name__ == "__main__": unittest.main()
