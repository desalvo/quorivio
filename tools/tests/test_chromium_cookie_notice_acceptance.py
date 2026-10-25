"""Regression: fresh Chromium contexts must dismiss the real cookie notice."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

class ChromiumCookieNoticeAcceptance(unittest.TestCase):
 def test_mock_browser_acknowledges_cookie_notice_by_accessible_button(self):
  src=(ROOT/'tools/ci_browser_editor.py').read_text()
  ast.parse(src)
  self.assertIn("page.get_by_role('dialog',name='Informativa cookie funzionali')",src)
  self.assertIn("button.click()",src)
  self.assertIn("await acknowledge_functional_cookie_notice(page)",src)
  self.assertIn("await acknowledge_functional_cookie_notice(mobile)",src)
  self.assertIn("await expect(notice).to_have_count(0)",src)
 def test_real_postgres_browser_acknowledges_notice_after_ui_ready(self):
  src=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
  ast.parse(src)
  self.assertIn("page.get_by_role('dialog',name='Informativa cookie funzionali')",src)
  self.assertIn("button.click()",src)
  self.assertIn("await page.get_by_role('button',name='Apri sessione').first.wait_for()",src)
 def test_no_forced_click_or_test_only_cookie_injection(self):
  for name in ('ci_browser_editor.py','ci_browser_editor_postgres.py'):
   with self.subTest(name=name):
    src=(ROOT/'tools'/name).read_text()
    self.assertNotIn('force=True',src)
    self.assertNotIn('q_cookie_notice=ack',src)
 def test_application_notice_is_a_real_accessible_dialog(self):
  src=(ROOT/'apps/web/src/main.tsx').read_text()
  self.assertIn('aria-label="Informativa cookie funzionali"',src)
  self.assertIn('>Ho capito</button>',src)
  self.assertIn("document.cookie='q_cookie_notice=ack",src)

if __name__=='__main__':unittest.main()
