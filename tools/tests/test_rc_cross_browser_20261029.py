"""Cross-engine RC acceptance must use native engines and never inflate gate credit."""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class NativeBrowserRC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        cls.script=(ROOT/'tools/ci_cross_browser_rc.py').read_text(encoding='utf8')
        cls.module=(ROOT/'apps/web/src/rehearsal-dialog.ts').read_text(encoding='utf8')
        cls.ledger=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text(encoding='utf8'))

    def test_opt_in_isolates_slow_native_browser_downloads(self):
        self.assertIn('cross_browser_test:',self.workflow)
        self.assertIn("inputs.cross_browser_test",self.workflow)
        self.assertIn('python3 -m playwright install --with-deps firefox webkit',self.workflow)
        self.assertIn('python3 tools/ci_cross_browser_rc.py --engines firefox webkit',self.workflow)
        self.assertIn('python3 tools/ci_cross_browser_rc.py --engines chromium',self.workflow)
        self.assertNotIn('python3 tools/ci_cross_browser_rc.py --engines firefox webkit\n      - name: Install PostgreSQL',self.workflow)

    def test_real_native_engine_no_chromium_fallback(self):
        self.assertIn("getattr(playwright,engine)",self.script)
        self.assertIn("if engine == 'chromium'",self.script)
        self.assertIn('await browser_type.launch(**kwargs)',self.script)
        self.assertIn('rehearsal-dialog.ts',self.script)
        self.assertIn('from ci_rc_public_stage_chromium import HTML',self.script)
        self.assertIn('1440,900',self.script)
        self.assertIn('390,844',self.script)

    def test_contenteditable_and_zero_controls_remain_keyboard_accessible(self):
        self.assertIn("'[contenteditable]:not([contenteditable=\"false\"])'",self.module)
        self.assertIn("const priorTabindex = root.getAttribute('tabindex')",self.module)
        self.assertIn("if (priorTabindex === null) root.removeAttribute('tabindex')",self.module)
        self.assertIn("element.hasAttribute('tabindex') && Number(element.getAttribute('tabindex')) < 0",self.module)
        self.assertIn("'editor', 'contenteditable",self.script)
        self.assertIn("'shell', 'Empty modal",self.script)

    def test_no_unverified_rc_gate_promotions(self):
        gates=self.ledger['gates']
        self.assertEqual(sum(g['weight'] for g in gates),100)
        self.assertEqual(sum(g['weight']*(1 if g['status']=='accepted' else .5 if g['status']=='partial' else 0) for g in gates),74.0)
        self.assertEqual(len([g for g in gates if g['status']=='partial']),17)

if __name__=='__main__':unittest.main()
