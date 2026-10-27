"""Regression tests: full-browser CI must not block on apt mirrors.

No real browser or network access is required for the deterministic checks.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('ci_browser_bootstrap',ROOT/'tools/ci_browser_bootstrap.py')
BOOT=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOT)


class BrowserBootstrapTests(unittest.TestCase):
    def test_hosted_ubuntu_runner_uses_preinstalled_browser_without_apt(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        assert 'runs-on: ubuntu-24.04' in workflow
        step=workflow.split('      - name: Chromium editor UI acceptance (opt-in)',1)[1].split('      - name: Upload Chromium failure diagnostics',1)[0]
        self.assertIn('python3 tools/ci_browser_bootstrap.py --smoke',step)
        self.assertIn('export QUORIVIO_CHROMIUM_PATH=',step)
        self.assertNotIn('python3 -m playwright install',step)
        self.assertNotIn('apt-get',step)
        self.assertIn('python3 tools/ci_nested_context_css_chromium.py',step)
        self.assertIn('python3 tools/ci_browser_editor.py',step)
        self.assertEqual(workflow.count('name: Production publication'),1)

    def test_all_browser_tests_accept_the_shared_preinstalled_binary(self):
        for name in ('ci_browser_editor.py','ci_browser_editor_postgres.py',
                     'ci_browser_participant.py','ci_browser_profile.py',
                     'ci_widget_title_menu.py','ci_nested_context_css_chromium.py'):
            with self.subTest(name=name):
                text=(ROOT/'tools'/name).read_text()
                self.assertIn('QUORIVIO_CHROMIUM_PATH',text)

    def test_browser_search_prefers_a_working_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            executable=Path(tmp)/'chrome'
            executable.write_text('#!/bin/sh\necho "Chromium 154.0.0"\n')
            executable.chmod(0o700)
            with patch.object(BOOT.shutil,'which',side_effect=lambda x: str(executable) if x=='chromium' else None),\
                 patch.dict(os.environ,{'CHROME_BIN':''}):
                self.assertEqual(BOOT.installed_browser(),executable)

    def test_browser_search_rejects_invalid_version_and_missing_browser(self):
        with patch.object(BOOT.shutil,'which',return_value=None),\
             patch.object(BOOT.subprocess,'run',side_effect=OSError('unavailable')),\
             patch.dict(os.environ,{'CHROME_BIN':''}):
            with self.assertRaisesRegex(RuntimeError,'Refusing apt installation'):
                BOOT.installed_browser()

    def test_version_probe_has_a_bounded_timeout_and_does_not_spawn_shell(self):
        with tempfile.TemporaryDirectory() as tmp:
            exe=Path(tmp)/'chrome'
            exe.write_text('#!/bin/sh\necho "Google Chrome 154.0.0"\n')
            exe.chmod(0o700)
            with patch.object(BOOT.shutil,'which',side_effect=lambda x: str(exe) if x=='google-chrome' else None),\
                 patch.object(BOOT.subprocess,'run', wraps=subprocess.run) as run:
                self.assertEqual(BOOT.installed_browser(),exe)
                self.assertEqual(run.call_args.args[0],(str(exe),'--version'))
                self.assertEqual(run.call_args.kwargs['timeout'],8)
                self.assertNotIn('shell',run.call_args.kwargs)

    def test_browser_path_export_is_only_after_successful_smoke(self):
        script=(ROOT/'tools/ci_browser_bootstrap.py').read_text()
        self.assertLess(script.index('probe_playwright(path)'),script.index('with args.github_env.open'))
        self.assertIn('QUORIVIO_CHROMIUM_PATH={path}\\n',script)

    def test_preflight_does_not_disable_publication_opt_in(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        assert 'github.event_name == \'workflow_dispatch\'' in workflow
        publication=workflow.split('      - name: ',1)[0]  # ensure policy retained in full workflow
        self.assertIn('inputs.publish_image',workflow)
        self.assertIn('inputs.publish_latest',workflow)
        self.assertIn('publish_image:',workflow)


if __name__=='__main__':
    unittest.main()
