"""Regression for Chromium full-gate cookie notice hit testing."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]


class CookiePortalLayer(unittest.TestCase):
    def test_notice_is_promoted_to_native_browser_top_layer(self):
        source=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("import{createPortal}from'react-dom'", source)
        self.assertIn('!cookieAcknowledged&&createPortal(<dialog ref={node=>{if(node&&!node.open)node.showModal()}}', source)
        self.assertIn('>Ho capito</button></dialog>,document.body)}', source)

    def test_cookie_acknowledgement_is_real_user_action_not_test_bypass(self):
        source=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("document.cookie='q_cookie_notice=ack", source)
        self.assertIn('setCookieAcknowledged(true)', source)
        self.assertIn('onCancel={event=>event.preventDefault()}',source)
        self.assertIn('node.showModal()',source)
        css=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
        self.assertIn('.functional-cookie-dialog::backdrop',css)
        for filename in ('ci_browser_editor.py','ci_browser_editor_postgres.py'):
            script=(ROOT/'tools'/filename).read_text(encoding='utf-8')
            ast.parse(script)
            self.assertIn("button.click()", script)
            self.assertNotIn('force=True', script)
            self.assertIn("element.matches(':modal')",script)

    def test_modal_cookie_portal_and_nonblocking_widget_tooltip_are_distinct(self):
        source=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
        # Cookie consent, widget tooltip and the accessible rehearsal are distinct portals.
        self.assertEqual(source.count('createPortal('),3)
        self.assertIn('return createPortal(<div className="rehearsal-backdrop"',source)
        self.assertIn('createPortal(<span className=',source)
        self.assertEqual(source.count('<dialog ref={node=>{if(node&&!node.open)node.showModal()}'),1)
        self.assertEqual(source.count('>Ho capito</button>'),1)


if __name__=='__main__':
    unittest.main()
