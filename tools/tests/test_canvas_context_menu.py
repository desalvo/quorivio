"""Canvas context commands must remain independently accessible."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class ContextMenuContract(unittest.TestCase):
    def test_widget_context_actions(self):
        src = (ROOT / 'apps/web/src/main.tsx').read_text()
        for action in ('onContextMenu=', 'onTouchStart=', "e.shiftKey&&e.key==='F10'", 'canvas-context-menu', 'Duplica', 'Porta avanti', 'Porta indietro', 'Modifica titolo', 'Elimina'):
            self.assertIn(action, src)
        self.assertIn("e.key==='Escape'", src)

    def test_style_accessibility(self):
        css = (ROOT / 'apps/web/src/style.css').read_text()
        self.assertIn('.canvas-context-menu button:focus-visible', css)

class ContextMediaContract(unittest.TestCase):
    def test_context_picker_reuses_session_library(self):
        src = (ROOT / 'apps/web/src/main.tsx').read_text()
        self.assertIn('assets={assets} sessionId={selected} onUpload={uploadWidgetMedia} assetBusy={assetBusy}', src)
        self.assertIn('Sostituisci file', src)
        self.assertIn("patch(w.id,{assetId:e.target.value})", src)
        self.assertIn("onUpload(w.id,e.target.files?.[0],w.kind)", src)
        self.assertIn("a.mime_type==='application/pdf'", src)
        self.assertIn("a.mime_type.startsWith('video/')", src)
