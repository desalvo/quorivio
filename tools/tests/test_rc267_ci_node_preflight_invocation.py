"""RC267: execute the actual early CI shell step, not a synthetic approximation.

GitHub Actions run: | scripts are shell programs. Dropping a backslash after
one .test.ts filename makes bash execute the next filename as a command (126).
The test uses Python and the installed Node runtime, with no npm dependencies.
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/ci.yml'
STEP = 'RC266 participant stage background and legacy assertion compatibility before npm'
FILES = (
    'apps/web/test/rc173-public-slide-fidelity.test.ts',
    'apps/web/test/rc266-participant-background-legacy-contract.test.ts',
    'apps/web/test/rc266-floating-window-docking.test.ts',
)


def read_step_script(workflow: str) -> str:
    lines = workflow.splitlines()
    marker = '      - name: ' + STEP
    locations = [index for index, line in enumerate(lines) if line == marker]
    if len(locations) != 1:
        raise AssertionError('RC266 early gate missing or duplicated')
    i = locations[0]
    if i + 1 >= len(lines) or lines[i + 1] != '        run: |':
        raise AssertionError('RC266 early gate must have a multi-line shell script')
    script_lines = []
    for line in lines[i + 2:]:
        if line.strip() and (len(line) - len(line.lstrip(' '))) < 10:
            break
        if line.strip():
            if not line.startswith('          '):
                raise AssertionError('unexpected shell indentation')
            script_lines.append(line[10:])
        else:
            script_lines.append('')
    return '\n'.join(script_lines) + '\n'


class EarlyNodePreflight(unittest.TestCase):
    def test_step_has_one_node_runner_and_all_three_files(self):
        script = read_step_script(WORKFLOW.read_text(encoding='utf-8'))
        self.assertEqual(script.count('node --experimental-strip-types --test'), 1)
        for file in FILES:
            self.assertEqual(script.count(file), 1)
        logical = re.sub(r'\\\s*\n', ' ', script).strip().splitlines()
        self.assertEqual(len(logical), 1, 'one node command; no orphan .test.ts shell command')
        self.assertTrue(logical[0].lstrip().startswith('node --experimental-strip-types --test '))

    def test_step_executes_without_npm_dependencies(self):
        script = read_step_script(WORKFLOW.read_text(encoding='utf-8'))
        result = subprocess.run(['bash', '-euo', 'pipefail', '-c', script], cwd=ROOT,
                                text=True, capture_output=True, timeout=25)
        self.assertEqual(result.returncode, 0,
                         'real early CI shell step failed:\n' + result.stdout[-2800:] + '\n' + result.stderr[-1200:])
        self.assertRegex(result.stdout, r'(?m)^# tests [1-9][0-9]*$')
        self.assertRegex(result.stdout, r'(?m)^# fail 0$')

    def test_regression_fixture_rejects_dropped_continuation(self):
        script = read_step_script(WORKFLOW.read_text(encoding='utf-8'))
        broken = script.replace(FILES[1]+' \
', FILES[1]+'\n')
        self.assertNotEqual(script, broken)
        logical = re.sub(r'\\\s*\n', ' ', broken).strip().splitlines()
        self.assertGreater(len(logical), 1)


if __name__ == '__main__':
    unittest.main()
