"""RC255: ensure strict standalone TypeScript and native Node ESM stay compatible."""
from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RC255StandaloneTypeScriptCI(unittest.TestCase):
    def test_pre_npm_guard_remains_in_ci(self):
        ci = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
        self.assertIn('tools.tests.test_rc75_typescript_ci', ci)
        self.assertIn('tools.tests.test_rc255_standalone_typescript_ci', ci)
        self.assertIn('RC255 strict standalone TypeScript and Node ESM compatibility before npm', ci)

    def test_native_node_import_retains_explicit_typescript_extension(self):
        master = (ROOT / 'apps/web/src/slide-master.ts').read_text(encoding='utf-8')
        self.assertIn("from './widget-typography-defaults.ts'", master)
        test = (ROOT / 'tools/tests/test_rc75_typescript_ci.py').read_text(encoding='utf-8')
        self.assertIn("'--noEmit', '--allowImportingTsExtensions', '--strict'", test)
        self.assertIn("'--moduleResolution', 'bundler'", test)

    @unittest.skipUnless(shutil.which('tsc'), 'TypeScript compiler unavailable')
    def test_strict_standalone_rc75_compilation(self):
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', '-q',
             'tools.tests.test_rc75_typescript_ci.RC75TypescriptRegression.test_strict_typescript_compilation_of_affected_independent_modules'],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-4000:])

    @unittest.skipUnless(shutil.which('node'), 'Node.js unavailable')
    def test_real_node_ts_module_import_and_arials(self):
        result = subprocess.run(
            ['node', '--experimental-strip-types', '--test',
             'apps/web/test/rc195-master-typography.test.ts',
             'apps/web/test/rc254-all-widget-schema-fonts.test.ts'],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[-4000:])
        self.assertIn('# fail 0', result.stdout)


if __name__ == '__main__':
    unittest.main()
