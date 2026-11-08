"""RC259: official-GitHub wizard self-update is safe, atomic and standalone.

Tests do NOT contact GitHub or Kubernetes and do not execute downloaded code.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import urllib.error

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import k8s_wizard as wizard

class _Response:
    def __init__(self, content:bytes, url:str=wizard.WIZARD_UPSTREAM_URL):
        self.content=content
        self.url=url
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def geturl(self):return self.url
    def read(self,limit):return self.content[:limit]

class WizardSelfUpdate(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.local=Path(self.temp.name)/'k8s_wizard.py'
        shutil.copy2(ROOT/'tools/k8s_wizard.py',self.local)
        self.original=self.local.read_bytes()
        self.new=self.original.replace(b"WIZARD_VERSION = '0.1.0-dev-rc259'",b"WIZARD_VERSION = '0.1.0-dev-rc260'",1)
        assert self.new != self.original

    def _download(self,body:bytes,url:str=wizard.WIZARD_UPSTREAM_URL):
        return mock.patch.object(wizard.urllib.request,'urlopen',return_value=_Response(body,url))

    def test_version_only_is_standalone_and_offline(self):
        with mock.patch.object(wizard.urllib.request,'urlopen',side_effect=AssertionError('network not allowed')):
            result=subprocess.run([sys.executable,str(self.local),'--version'],capture_output=True,text=True,timeout=6)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('0.1.0-dev-rc259',result.stdout)
        self.assertIn('Quorivio Kubernetes wizard',result.stdout)

    def test_offline_optout_and_no_repository_dependency(self):
        result=subprocess.run([sys.executable,str(self.local),'--no-self-update','--self-update-only'],
            cwd=self.temp.name,capture_output=True,text=True,timeout=6,env={**os.environ,'PYTHONPATH':''})
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('0.1.0-dev-rc259',result.stdout)
        self.assertEqual(self.local.read_bytes(),self.original)

    def test_publishes_a_newer_release_atomically_and_preserves_permissions(self):
        old_mode=self.local.stat().st_mode & 0o777
        with self._download(self.new):
            updated=wizard._maybe_install_official_update(self.local)
        self.assertTrue(updated)
        self.assertEqual(self.local.read_bytes(),self.new)
        self.assertEqual(self.local.stat().st_mode & 0o777,old_mode)
        self.assertEqual(list(self.local.parent.glob('.quorivio-wizard-update-*')),[])
        self.assertFalse((self.local.parent/'k8s_converter_upgrade.py').exists())

    def test_idempotent_same_bytes(self):
        with self._download(self.original):
            self.assertFalse(wizard._maybe_install_official_update(self.local))
        self.assertEqual(self.local.read_bytes(),self.original)

    def test_never_downgrades_or_installs_unversioned_old_upstream(self):
        previous=self.original.replace(b"WIZARD_VERSION = '0.1.0-dev-rc259'",b"WIZARD_VERSION = '0.1.0-dev-rc258'",1)
        for candidate in (previous,self.original.replace(b"WIZARD_VERSION = '0.1.0-dev-rc259'",b"LEGACY_RELEASE = '0.1.0-dev-rc258'",1)):
            with self.subTest(candidate=candidate[:100]),self._download(candidate):
                self.assertFalse(wizard._maybe_install_official_update(self.local))
                self.assertEqual(self.local.read_bytes(),self.original)

    def test_rejects_invalid_utf8_python_and_untrusted_redirect(self):
        invalid=[b'\xff\xfe',b'',self.new+b'\nif (\n',self.new.replace(b'_STANDALONE_COMPONENT_SOURCES',b'NO_EMBEDDED_SOURCES')]
        for candidate in invalid:
            with self.subTest(size=len(candidate)),self._download(candidate):
                with self.assertRaises(wizard.WizardUpdateError):
                    wizard._maybe_install_official_update(self.local)
            self.assertEqual(self.local.read_bytes(),self.original)
        for url in ('https://example.org/untrusted.py','https://raw.githubusercontent.com/other/fork/main/tools/k8s_wizard.py'):
            with self.subTest(url=url),self._download(self.new,url):
                with self.assertRaisesRegex(wizard.WizardUpdateError,'redirected'):
                    wizard._maybe_install_official_update(self.local)

    def test_refuses_symlink_without_touching_target(self):
        aliased=self.local.parent/'aliased.py'
        aliased.symlink_to(self.local)
        with mock.patch.object(wizard,'_download_official_wizard',side_effect=AssertionError('network must not be called')):
            with self.assertRaisesRegex(wizard.WizardUpdateError,'symlink'):
                wizard._maybe_install_official_update(aliased)
        self.assertEqual(self.local.read_bytes(),self.original)

    def test_offline_retrieval_fails_closed(self):
        with mock.patch.object(wizard.urllib.request,'urlopen',side_effect=urllib.error.URLError('no network')):
            with self.assertRaisesRegex(wizard.WizardUpdateError,'Cannot securely check'):
                wizard._maybe_install_official_update(self.local)
        self.assertEqual(self.local.read_bytes(),self.original)

    def test_replace_failure_does_not_corrupt_installed_wizard(self):
        with self._download(self.new),mock.patch.object(wizard.os,'replace',side_effect=OSError('read-only')):
            with self.assertRaisesRegex(wizard.WizardUpdateError,'atomically replace'):
                wizard._maybe_install_official_update(self.local)
        self.assertEqual(self.local.read_bytes(),self.original)
        self.assertEqual(list(self.local.parent.glob('.quorivio-wizard-update-*')),[])

    def test_restart_once_with_same_cli_arguments(self):
        class _Restarted(Exception):pass
        args=['k8s_wizard.py','--upgrade-converter','--set','namespace=quorivio','--output','plan']
        with mock.patch.object(wizard.sys,'argv',args),mock.patch.object(wizard,'_maybe_install_official_update',return_value=True) as update, \
             mock.patch.object(wizard.os,'execv',side_effect=_Restarted) as execute, \
             mock.patch.dict(os.environ,{wizard._WIZARD_RESTART_GUARD:''}):
            with self.assertRaises(_Restarted):wizard._run_standalone_cli()
            self.assertEqual(update.call_count,1)
            self.assertEqual(execute.call_args.args[1][2:],args[1:])
            self.assertEqual(os.environ[wizard._WIZARD_RESTART_GUARD],'1')
            # The restarted interpreter has the one-shot guard set.
            self.assertEqual(os.environ[wizard._WIZARD_RESTART_GUARD],'1')

    def test_post_restart_guard_skips_second_network_check(self):
        with mock.patch.object(wizard.sys,'argv',['k8s_wizard.py','--self-update-only']), \
             mock.patch.dict(os.environ,{wizard._WIZARD_RESTART_GUARD:'1'}), \
             mock.patch.object(wizard,'_maybe_install_official_update',side_effect=AssertionError('update loop')):
            self.assertEqual(wizard._run_standalone_cli(),0)

    def test_required_github_error_stops_before_any_cluster_operation(self):
        with mock.patch.object(wizard.sys,'argv',['k8s_wizard.py','--upgrade-converter']), \
             mock.patch.dict(os.environ,{wizard._WIZARD_RESTART_GUARD:''}), \
             mock.patch.object(wizard,'_maybe_install_official_update',side_effect=wizard.WizardUpdateError('offline')), \
             mock.patch.object(wizard,'main',side_effect=AssertionError('CLI must not run')):
            self.assertEqual(wizard._run_standalone_cli(),3)

    def test_updater_only_trusts_official_github_main_and_has_bounded_transfer(self):
        self.assertEqual(wizard.WIZARD_UPSTREAM_URL,'https://raw.githubusercontent.com/desalvo/quorivio/main/tools/k8s_wizard.py')
        self.assertLess(wizard.WIZARD_MAX_DOWNLOAD_BYTES,3*1024*1024)
        with self._download(b'x'*(wizard.WIZARD_MAX_DOWNLOAD_BYTES+1)):
            with self.assertRaisesRegex(wizard.WizardUpdateError,'exceeds'):
                wizard._maybe_install_official_update(self.local)

if __name__=='__main__':unittest.main()
