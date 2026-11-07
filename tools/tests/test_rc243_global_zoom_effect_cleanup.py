"""RC243: global zoom useEffect cleanup must return void, not removeProperty string.

React EffectCallback's Destructor cannot return the string from
CSSStyleDeclaration.removeProperty. This test must run before npm in CI.
"""
from __future__ import annotations

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MAIN = ROOT / 'apps/web/src/main.tsx'
WORKFLOW = ROOT / '.github/workflows/ci.yml'


def assert_cleanup_void(source: str) -> None:
    # Match the effect by the scoped zoom property, then inspect its cleanup.
    start = source.index('function GlobalPageZoomShell()')
    end = source.index('createRoot(', start)
    shell = source[start:end]
    assert 'root.style.setProperty(\'zoom\',value)' in shell
    assert 'root.style.removeProperty(\'zoom\')' in shell
    assert 'window.localStorage.setItem(GLOBAL_ZOOM_STORAGE_KEY' in shell
    # Regression: `return()=>root.style.removeProperty(...)` returns a string.
    assert not re.search(r'return\s*\(\s*\)\s*=>\s*root\.style\.removeProperty\(', shell)
    # Braced arrow callback makes the cleanup's return value void.
    assert "return()=>{root.style.removeProperty(\'zoom\');root.style.removeProperty(GLOBAL_ZOOM_CSS_VARIABLE);};" in shell
    assert shell.index('return()=>{root.style.removeProperty') < shell.index('},[zoom]);')


class RC243GlobalZoomCleanup(unittest.TestCase):
    def test_zoom_cleanup_returns_void(self):
        assert_cleanup_void(MAIN.read_text(encoding='utf8'))

    def test_negative_regression_rejects_expression_body_cleanup(self):
        source = MAIN.read_text(encoding='utf8')
        mutated = source.replace('return()=>{root.style.removeProperty(\'zoom\');root.style.removeProperty(GLOBAL_ZOOM_CSS_VARIABLE);};',
                                 'return()=>root.style.removeProperty(\'zoom\');')
        self.assertNotEqual(mutated, source)
        with self.assertRaises(AssertionError):
            assert_cleanup_void(mutated)

    def test_ci_keeps_strict_typecheck_and_new_preflight(self):
        workflow = WORKFLOW.read_text(encoding='utf8')
        self.assertIn('python3 -m unittest tools.tests.test_rc243_global_zoom_effect_cleanup -q', workflow)
        self.assertIn('./node_modules/.bin/tsc --noEmit -p apps/web/tsconfig.json',workflow)
        self.assertIn('python3 tools/verify_rc_cycle242_inventory.py --historical', workflow)
        self.assertIn('python3 tools/verify_rc_cycle243_inventory.py',workflow)

if __name__ == '__main__':
    unittest.main()
