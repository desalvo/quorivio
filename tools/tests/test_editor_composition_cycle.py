"""Source-contract checks for editor composition controls (not browser E2E)."""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

class EditorCompositionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tsx = (ROOT / 'apps/web/src/main.tsx').read_text()
        cls.css = (ROOT / 'apps/web/src/style.css').read_text()

    def test_widget_copy_uses_distinct_identity(self):
        self.assertIn('const duplicateWidget=', self.tsx)
        self.assertIn('crypto.randomUUID()', self.tsx)
        self.assertIn('onClick={()=>duplicateWidget(w)}', self.tsx)

    def test_layer_order_preserves_existing_items(self):
        self.assertIn("direction:'front'|'back'", self.tsx)
        self.assertIn("widgets.filter(w=>w.id!==id),item", self.tsx)
        self.assertIn("[item,...widgets.filter(w=>w.id!==id)]", self.tsx)

    def test_grid_is_optional_and_keyboard_access_retained(self):
        self.assertIn('const [snapGrid,setSnapGrid]', self.tsx)
        self.assertIn('Aggancia alla griglia (5%)', self.tsx)
        self.assertIn('aria-keyshortcuts=', self.tsx)
        self.assertIn('.canvas-layer-tools button:focus-visible', self.css)

if __name__ == '__main__':
    unittest.main()
