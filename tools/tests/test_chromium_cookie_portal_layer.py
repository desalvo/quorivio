"""Regression for Chromium full-gate cookie notice hit testing."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]


class CookiePortalLayer(unittest.TestCase):
    def test_notice_is_rendered_in_document_body_outside_editor_stacking_context(self):
        source=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("import{createPortal}from'react-dom'", source)
        self.assertIn('!cookieAcknowledged&&createPortal(<aside role="dialog"', source)
        self.assertIn('>Ho capito</button></aside>,document.body)}', source)

    def test_cookie_acknowledgement_is_real_user_action_not_test_bypass(self):
        source=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("document.cookie='q_cookie_notice=ack", source)
        self.assertIn('setCookieAcknowledged(true)', source)
        for filename in ('ci_browser_editor.py','ci_browser_editor_postgres.py'):
            script=(ROOT/'tools'/filename).read_text(encoding='utf-8')
            ast.parse(script)
            self.assertIn("notice.get_by_role('button',name='Ho capito').click()", script)
            self.assertNotIn('force=True', script)

    def test_portal_is_used_only_for_functional_notice(self):
        source=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
        self.assertEqual(source.count('createPortal('),1)
        self.assertEqual(source.count('>Ho capito</button>'),1)


if __name__=='__main__':
    unittest.main()
