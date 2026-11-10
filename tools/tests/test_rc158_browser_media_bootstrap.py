"""RC158: manually dispatched Docker gates must provision mandatory browser tests.

No network, browser or Docker is required for these early, negative-mutation
source-contract regressions. The real JPG/Logo/PostgreSQL acceptance stays a
separate mandatory CI stage and is never mocked here.
"""
from __future__ import annotations

from pathlib import Path
import os
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / '.github/workflows/ci.yml'
NAME = 'RC158 prepare Chromium for mandatory JPG and Logo persistence'
MEDIA = 'Real Chromium JPG background and Logo upload/persistence acceptance'
OPTIONAL = 'Chromium editor UI acceptance (opt-in)'


def named_step(workflow: str, name: str) -> str:
    marker = '      - name: ' + name + '\n'
    if workflow.count(marker) != 1:
        raise AssertionError(f'missing/ambiguous workflow step: {name}')
    tail = workflow.split(marker, 1)[1]
    return tail.split('\n      - ', 1)[0]


def supports_manual_docker_without_browser_checkbox(workflow: str) -> bool:
    try:
        prep = named_step(workflow, NAME)
        media = named_step(workflow, MEDIA)
        optional = named_step(workflow, OPTIONAL)
    except AssertionError:
        return False
    # Both the prerequisite and the JPG/Logo test must be unconditional.
    if re.search(r'^        if:', prep, flags=re.M) or re.search(r'^        if:', media, flags=re.M):
        return False
    if not ('inputs.browser_test' in optional and 'timeout-minutes: 3' in prep):
        return False
    if not (workflow.index('      - name: ' + NAME) < workflow.index('      - name: ' + MEDIA)):
        return False
    if 'python3 -m pip install --disable-pip-version-check --break-system-packages' not in prep:
        return False
    if "'playwright>=1.50,<2'" not in prep:
        return False
    if "python3 -c 'from playwright.async_api import async_playwright'" not in prep:
        return False
    if 'if [ -z "${QUORIVIO_CHROMIUM_PATH:-}" ]; then' not in prep:
        return False
    if 'python3 tools/ci_browser_bootstrap.py --smoke --github-env "$GITHUB_ENV"' not in prep:
        return False
    if 'python3 tools/ci_browser_media_picker_postgres.py' not in media:
        return False
    if '      - name: RC158 required Chromium media dependencies and manual Docker safety preflight\n' not in workflow:
        return False
    return True


class RequiredBrowserMediaBootstrap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding='utf-8')

    def test_manual_dispatch_provisions_required_browser_even_without_opt_in(self):
        self.assertTrue(supports_manual_docker_without_browser_checkbox(self.workflow))

    def test_playwright_dep_is_reinstalled_only_if_missing_and_browser_smoked_if_needed(self):
        prep = named_step(self.workflow, NAME)
        self.assertIn("if ! python3 -c 'from playwright.async_api import async_playwright'", prep)
        self.assertIn("'playwright>=1.50,<2'", prep)
        self.assertIn('python3 tools/ci_browser_bootstrap.py --smoke', prep)
        self.assertLess(prep.index('python3 -m pip install'), prep.index('if [ -z'))

    def test_mandatory_jpg_logo_postgres_acceptance_not_skipped(self):
        media = named_step(self.workflow, MEDIA)
        self.assertNotIn('if:', media)
        self.assertIn('QUORIVIO_CI_LOAD_TOKEN:', media)
        self.assertIn('ci_browser_media_picker_postgres.py', media)
        media_source = (ROOT / 'tools/ci_browser_media_picker_postgres.py').read_text()
        self.assertIn('from playwright.async_api import async_playwright, expect', media_source)
        self.assertIn('QUORIVIO_CHROMIUM_PATH', media_source)
        self.assertIn('persisted_widget', media_source)

    def test_negative_missing_preparation_fails(self):
        cut = self.workflow.replace('      - name: ' + NAME + '\n', '      - name: Removed preparation\n')
        self.assertFalse(supports_manual_docker_without_browser_checkbox(cut))

    def test_negative_conditional_dependency_step_fails(self):
        cut = self.workflow.replace(
            '      - name: ' + NAME + '\n',
            '      - name: ' + NAME + '\n        if: github.event_name == \'workflow_dispatch\' && inputs.browser_test\n',
        )
        self.assertFalse(supports_manual_docker_without_browser_checkbox(cut))

    def test_negative_missing_install_or_smoke_fails(self):
        for target in ("'playwright>=1.50,<2'", 'python3 tools/ci_browser_bootstrap.py --smoke --github-env "$GITHUB_ENV"'):
            with self.subTest(target=target):
                prefix, after = self.workflow.split('      - name: ' + NAME + '\n', 1)
                body, remainder = after.split('\n      - ', 1)
                cut = prefix + '      - name: ' + NAME + '\n' + body.replace(target, 'REMOVED', 1) + '\n      - ' + remainder
                self.assertFalse(supports_manual_docker_without_browser_checkbox(cut))

    def _mocked_setup_run(self, *, import_exit: int, browser_path: str):
        """Execute the exact CI bash block with a fake Python executable."""
        step = named_step(self.workflow, NAME)
        command = '\n'.join(line[10:] for line in step.split('        run: |\n', 1)[1].splitlines())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / 'python3'
            executable.write_text(
                '#!/usr/bin/env bash\n'
                'if [ "$1" = "-c" ]; then exit "$MOCK_IMPORT_EXIT"; fi\n'
                'if [ "$1" = "-m" ] && [ "$2" = "pip" ]; then echo pip >> "$MOCK_CALLS"; exit 0; fi\n'
                'if [ "$1" = "tools/ci_browser_bootstrap.py" ]; then\n'
                '  echo smoke >> "$MOCK_CALLS"\n'
                '  echo QUORIVIO_CHROMIUM_PATH=/mock/chromium >> "$GITHUB_ENV"\n'
                '  exit 0\n'
                'fi\nexit 77\n'
            )
            executable.chmod(0o700)
            calls = root / 'calls'
            gh_env = root / 'github_env'
            env = {**os.environ, 'PATH': str(root) + ':' + os.environ['PATH'],
                   'QUORIVIO_CHROMIUM_PATH': browser_path,
                   'MOCK_IMPORT_EXIT': str(import_exit), 'MOCK_CALLS': str(calls),
                   'GITHUB_ENV': str(gh_env)}
            result = subprocess.run(['bash', '-e', '-o', 'pipefail', '-c', command],
                                    cwd=ROOT, env=env, capture_output=True,
                                    text=True, timeout=8)
            return result, calls.read_text().splitlines() if calls.exists() else [], (gh_env.read_text() if gh_env.exists() else '')

    def test_real_shell_branch_missing_playwright_and_chromium_bootstraps_both(self):
        result, calls, github_env = self._mocked_setup_run(import_exit=1, browser_path='')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, ['pip', 'smoke'])
        self.assertIn('QUORIVIO_CHROMIUM_PATH=/mock/chromium', github_env)

    def test_real_shell_branch_existing_dependencies_does_not_reinstall(self):
        result, calls, github_env = self._mocked_setup_run(import_exit=0, browser_path='/mock/chromium')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(calls, [])
        self.assertEqual(github_env, '')

    def test_docker_publication_remains_explicit_and_downstream(self):
        s = self.workflow
        image_build = s.split('  image-build:\n', 1)[1].split('\n  kubernetes-api-manifests:', 1)[0]
        self.assertIn('needs: validate', image_build)
        self.assertIn('push: false', image_build)
        self.assertIn('Scan runtime image', image_build)
        manual = s.split('  publish:\n', 1)[1].split('\n  publish-on-commit:', 1)[0]
        self.assertIn("inputs.publish_image == true", manual)
        self.assertIn("needs.publish-platform.result == 'success'", manual)
        self.assertIn('needs: [validate, image-build, publish-platform, publish-converter-platform]', manual)
        self.assertIn("needs.publish-converter-platform.result == 'success'", manual)
        self.assertIn('publish_image:\n        description:', s)
        self.assertIn('default: false', s)


if __name__ == '__main__':
    unittest.main()
