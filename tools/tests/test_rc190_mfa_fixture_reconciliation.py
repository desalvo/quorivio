"""RC190: fail closed when an opaque-origin MFA fixture loses storage setup."""
from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (ROOT / 'tools/ci_rc186_mfa_enter_chromium.py').read_text(encoding='utf8')
SMOKE = (ROOT / 'tools/ci_rc190_mfa_fixture_chromium.py').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')


class MFAFixtureReconciliation(unittest.TestCase):
    def test_storage_and_cookie_fixture_mounted_before_compiled_bundle(self):
        for part in ("Object.defineProperty(document, 'cookie'", "Object.defineProperty(window,'localStorage'",
                     "Object.defineProperty(window,'sessionStorage'", "const local = new Map(), session = new Map()"):
            self.assertIn(part, SCRIPT)
        self.assertLess(SCRIPT.index('await page.evaluate(API)'), SCRIPT.index('await page.add_script_tag('))
        self.assertLess(SCRIPT.index('await page.evaluate(API)'), SCRIPT.index("await page.evaluate('''() => ({"))
        self.assertLess(SCRIPT.index('await page.evaluate(\'\'\'() => ({'), SCRIPT.index('await page.add_script_tag('))

    def test_actual_mfa_contract_remains_end_to_end_and_security_scoped(self):
        self.assertIn('await field.press(\'Enter\')', SCRIPT)
        self.assertIn("window.mfaProbe.calls.length===1", SCRIPT)
        self.assertIn('window.mfaProbe.failOnce=true', SCRIPT)
        self.assertIn("for mode in ('email','recovery','button')", SCRIPT)
        self.assertIn('await expect(cookie).to_be_visible(timeout=10000)', SCRIPT)
        self.assertIn('page errors={errors!r}', SCRIPT)
        self.assertNotIn('page.route("**/*", lambda route: route.continue_()', SCRIPT)

    def test_fixture_smoke_is_run_before_browser_login_test(self):
        self.assertIn('python3 tools/ci_rc190_mfa_fixture_chromium.py', WORKFLOW)
        self.assertIn('python3 tools/ci_rc186_mfa_enter_chromium.py', WORKFLOW)
        self.assertLess(WORKFLOW.index('python3 tools/ci_rc190_mfa_fixture_chromium.py'),
                        WORKFLOW.index('python3 tools/ci_rc186_mfa_enter_chromium.py'))
        self.assertIn('await page.evaluate(API)', SMOKE)
        self.assertIn('q_cookie_notice=ack', SMOKE)

    def test_regression_mutations_break_fixture_contract(self):
        checks=("Object.defineProperty(window,'localStorage'", "Object.defineProperty(document, 'cookie'")
        for token in checks:
            mutated=SCRIPT.replace(token, '// BROKEN ', 1)
            self.assertNotEqual(mutated,SCRIPT)
            self.assertNotIn(token,mutated)


if __name__ == '__main__':
    unittest.main()
