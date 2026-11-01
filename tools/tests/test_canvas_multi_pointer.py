"""A second finger must never hijack an existing canvas gesture."""
from pathlib import Path
import unittest
SOURCE=(Path(__file__).resolve().parents[2]/'apps/web/src/main.tsx').read_text()
class MultiPointerSafety(unittest.TestCase):
    def test_gesture_owned_by_initial_pointer(self):
        self.assertIn('pointerId:number;mode:',SOURCE)
        self.assertIn('if(gesture.current || (e.pointerType',SOURCE)
        self.assertIn('g.pointerId!==e.pointerId',SOURCE)
    def test_release_and_cancel_only_owned_pointer(self):
        self.assertIn('gesture.current?.pointerId===e.pointerId',SOURCE)
        self.assertIn('if(!g||g.pointerId!==e.pointerId)return;onChange(g.groupBase||widgets)',SOURCE)
