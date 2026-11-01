"""Prevent mobile breakpoint from disabling the canvas pointer gestures."""
from pathlib import Path
import re
import unittest

CSS = (Path(__file__).resolve().parents[2] / 'apps/web/src/style.css').read_text()

class MobileTouchCaptureContract(unittest.TestCase):
    def test_mobile_rule_does_not_restore_touch_manipulation_on_widget(self):
        self.assertIn('.widget-canvas-item{touch-action:none;min-width:0;max-width:100%;overflow-wrap:anywhere}', CSS)
        self.assertNotIn('.widget-canvas-item{touch-action:manipulation;', CSS)

    def test_form_controls_remain_touch_interactive(self):
        self.assertIn('.widget-canvas-item button,.widget-canvas-item input,.widget-canvas-item textarea,.widget-canvas-item select{touch-action:manipulation;', CSS)

    def test_resize_and_rotate_handles_keep_raw_pointer_stream(self):
        self.assertIn('.widget-canvas-item [data-resize-edge],.widget-canvas-item [data-rotate-handle]{touch-action:none}', CSS)

if __name__ == '__main__':
    unittest.main()
