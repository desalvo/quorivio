"""RC216 browser acceptance: login must be located by accessible semantics.

The compiled Chromium run 42145939288 showed correct access form but the old
`main.narrow` test selector caused a false failure. Keep the whole expiration and
recovery scenario, and fail closed if selectors or its assertions regress.
"""
from pathlib import Path
import unittest

SCRIPT = (Path(__file__).resolve().parents[1] / 'ci_browser_editor.py').read_text(encoding='utf8')


def _validate(src: str) -> None:
    start = src.index("state['auth_error']=401")
    end = src.index("state['session_active']=False", start)
    scenario = src[start:end]
    required = (
        "state['auth_error']=401",
        "await page.reload(wait_until='domcontentloaded')",
        "await await_frontend_mount(page,errors)",
        "get_by_role('heading',name='Accedi come presentatore',exact=True)",
        "get_by_role('textbox',name='Email o nickname')",
        "get_by_role('textbox',name='Password')",
        "get_by_role('button',name='Accedi',exact=True)",
        "get_by_role('region',name='Editor grafico delle pagine')).to_have_count(0)",
        "state['auth_error']=None",
        "get_by_role('region',name='Editor grafico delle pagine')",
        "await expect(editor).to_be_visible(timeout=30000)",
    )
    for token in required:
        if token not in scenario:
            raise ValueError('expired-auth browser scenario lost assertion: ' + token)
    if "main.narrow" in scenario:
        raise ValueError('stale login selector detected')
    if scenario.count("await page.reload(wait_until='domcontentloaded')") != 2:
        raise ValueError('scenario must verify both 401 login and restored editor')
    if 'clear_cookies(' in scenario or 'localStorage.clear' in scenario:
        raise ValueError('must recover without clearing cookies or browser state')


class RC216ExpiredAuthBrowserContract(unittest.TestCase):
    def test_current_preflight_is_wired_before_npm(self):
        workflow = (Path(__file__).resolve().parents[2] / '.github/workflows/ci.yml').read_text(encoding='utf8')
        marker = 'tools.tests.test_rc216_expired_auth_browser_contract'
        self.assertIn(marker, workflow)
        self.assertLess(workflow.index(marker), workflow.index('run: npm install --ignore-scripts --no-audit --no-fund'))

    def test_current_scenario(self):
        _validate(SCRIPT)

    def test_rejects_old_css_selector(self):
        with self.assertRaises(ValueError):
            _validate(SCRIPT.replace("get_by_role('heading',name='Accedi come presentatore',exact=True)", "locator('main.narrow')"))

    def test_rejects_missing_login_form(self):
        with self.assertRaises(ValueError):
            _validate(SCRIPT.replace("get_by_role('textbox',name='Password')", "locator('input')"))

    def test_rejects_disabling_reauthentication(self):
        with self.assertRaises(ValueError):
            _validate(SCRIPT.replace("state['auth_error']=None", "state['auth_error']=401"))

    def test_rejects_cookie_deletion(self):
        with self.assertRaises(ValueError):
            _validate(SCRIPT.replace("state['auth_error']=None", "await page.context.clear_cookies()\n   state['auth_error']=None"))

    def test_rejects_missing_editor_restoration(self):
        with self.assertRaises(ValueError):
            _validate(SCRIPT.replace("await expect(editor).to_be_visible(timeout=30000)\n   state['session_active']=False", "await editor.count()\n   state['session_active']=False"))


if __name__ == '__main__':
    unittest.main()
