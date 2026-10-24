"""Regression contracts for editor gestures and their stored geometry."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx').read_text()
CSS = (Path(__file__).resolve().parents[2] / 'apps/web/src/style.css').read_text()

class EditorGestures(unittest.TestCase):
    def test_rotation_relative_to_initial_orientation(self):
        self.assertIn('startAngle?:number', SOURCE)
        self.assertIn('(g.pos.rotation??0)+(angle-(g.startAngle??angle))', SOURCE)
    def test_cancel_restores_original_geometry(self):
        self.assertIn('function cancelGesture(e:React.PointerEvent<HTMLDivElement>)', SOURCE)
        self.assertIn('onChange(g.groupBase||widgets)', SOURCE)
        self.assertIn('onPointerCancel={cancelGesture}', SOURCE)
    def test_touch_and_pointer_capture(self):
        self.assertIn('onLostPointerCapture={cancelGesture}', SOURCE)
        self.assertIn('touch-action: none', CSS)

if __name__ == '__main__': unittest.main()
