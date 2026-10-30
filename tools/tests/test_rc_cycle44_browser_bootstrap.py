"""Regression for standard CI run 41103165554: React startup and cookie top-layer."""
import ast
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]

class ChromiumBrowserBootstrapRegression(unittest.TestCase):
 def test_mock_editor_awaits_react_and_dismisses_cookie_before_navigation(self):
  src=(ROOT/'tools/ci_browser_editor.py').read_text()
  ast.parse(src)
  self.assertIn("await page.locator('#root .app').wait_for(state='visible'",src)
  self.assertIn("await page.reload(wait_until='domcontentloaded')",src)
  for name in ('page','mobile'):
   ready='await await_frontend_mount('+name
   modal='await acknowledge_functional_cookie_notice('+name+')'
   nav=f"await {name}.get_by_role('button',name='Apri sessione').first.wait_for()"
   self.assertLess(src.index(ready),src.index(modal))
   self.assertLess(src.index(modal),src.index(nav))
  self.assertNotIn('force=True',src)

 def test_real_postgres_editor_cookie_order(self):
  src=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
  ast.parse(src)
  self.assertLess(src.index('await button.click()'),src.index("await page.get_by_role('button',name='Apri sessione').first.wait_for()"))
  self.assertIn("if not any(cookie['name']=='q_cookie_notice' for cookie in cookies):",src)

 def test_chromium_probe_is_wired_before_full_editor(self):
  probe=(ROOT/'tools/ci_cookie_modal_order_chromium.py').read_text()
  ast.parse(probe)
  self.assertIn('Native modal must intercept pointer events',probe)
  flow=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertLess(flow.index('python3 tools/ci_cookie_modal_order_chromium.py'),flow.index('python3 tools/ci_browser_editor.py'))

if __name__=='__main__':unittest.main()
