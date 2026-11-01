"""Regression for accessible keyboard manipulation on the canvas."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
class CanvasKeyboardAccess(unittest.TestCase):
    def test_widget_is_keyboard_focusable(self):
        src=(ROOT/'apps/web/src/main.tsx').read_text()
        self.assertIn("tabIndex={0} role=\"group\" data-selected={selectedWidgets.includes(w.id)} onKeyDown={e=>{if(e.key==='ContextMenu'",src)
        self.assertIn('e.preventDefault();',src)
    def test_all_geometry_modes_and_limits(self):
        src=(ROOT/'apps/web/src/main.tsx').read_text()
        start=src.index(' function keyboardGeometry(')
        snippet=src[start:src.index(' function end(',start)]
        for value in ['e.altKey','e.shiftKey','position.rotation','position.width','position.height','position.x','position.y','100-position.width','100-position.height','rejectWidgetCollisions(widgets,widgets.map(item=>item.id===w.id?{...item,position}:item),[w.id])']:
            self.assertIn(value,snippet)
    def test_keyboard_focus_is_visible(self):
        css=(ROOT/'apps/web/src/style.css').read_text()
        self.assertIn('.widget-canvas-item:focus-visible',css)
if __name__=='__main__': unittest.main()
