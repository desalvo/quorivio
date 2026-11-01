"""RC105 source contracts: floating panels and selected-only geometry."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
TSX=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')

class FloatingEditorContract(unittest.TestCase):
    def test_three_floating_windows(self):
        self.assertIn('function EditorFloatingWindow(',TSX)
        self.assertEqual(TSX.count('<EditorFloatingWindow '),3)
        self.assertEqual(TSX.count('</EditorFloatingWindow>'),3)
        self.assertIn('portal placement="palette"',TSX)
        self.assertIn('portal placement="properties" className="editor-context-drawer editor-widget-drawer"',TSX)
        self.assertIn('portal placement="page" className="editor-context-drawer"',TSX)
    def test_drag_only_from_header(self):
        self.assertIn("closest('.palette-ribbon-head,.editor-drawer-heading')",TSX)
        self.assertIn("closest('button,input,textarea,select,a,[contenteditable=true]')",TSX)
        self.assertIn('e.currentTarget.setPointerCapture(e.pointerId)',TSX)
        self.assertIn('window.innerWidth-width-8',TSX)
        self.assertIn('window.innerHeight-height-8',TSX)
    def test_selection_only_resize_and_absolute_edges(self):
        self.assertRegex(CSS,re.compile(r'\.widget-canvas-item\[data-selected="true"\] > \.widget-resize-edge'))
        self.assertIn('position:absolute!important;display:none!important;visibility:hidden!important;',CSS)
        for edge in 'n ne e se s sw w nw'.split():
            self.assertIn(f'> .widget-resize-edge.edge-{edge}',CSS)
        self.assertIn('.widget-canvas-item:not([data-selected="true"]) > .canvas-remove',CSS)
    def test_palette_outside_layout(self):
        self.assertIn('return portal?createPortal(',TSX)
        self.assertIn('editor-floating-scope',TSX)
        self.assertIn('body .editor-floating-panel.widget-selection-palette',CSS)
        self.assertIn('position:fixed!important',CSS)
    def test_source_keeps_persistent_text_selection(self):
        self.assertIn('onMouseDownCapture={e=>{if((e.target as HTMLElement).closest("button"))e.preventDefault()}}',TSX)

if __name__=='__main__': unittest.main()
