"""RC260: converter upgrade must keep the initial Kustomize base in sync.

No Kubernetes, external YAML parser or third-party dependency is needed.
Includes preflight drift, backup, offline, repeatability and standalone tests.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import k8s_converter_upgrade as upgrade
import k8s_wizard as wizard
from tools.tests.test_rc246_converter_upgrade import fixture, FakeKube
from tools.tests.test_rc258_standalone_wizard_rollout import FAKE_KUBECTL

IMAGE='desalvo/quorivio-converter:latest'


class GeneratedManifestReconciliation(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.generated=self.root/'generated'
        wizard.generate(dict(wizard.DEFAULTS),self.generated)
        self.original={p.name:p.read_bytes() for p in self.generated.iterdir() if p.is_file()}
        self.dep,self.secret=fixture()
        value=re.search(r'(?m)^  DATABASE_URL: ([A-Za-z0-9+/=]+)$',
                        (self.generated/'05-app-secret.yaml').read_text()).group(1)
        self.secret['data']['DATABASE_URL']=value
        self.fake=FakeKube(self.dep,self.secret)
        p=patch.object(upgrade,'run_kubectl',side_effect=self.fake.run)
        p.start();self.addCleanup(p.stop)
        self.plan=self.root/'plan'

    def _plan(self):
        return upgrade.prepare_upgrade('quorivio','quorivio',self.plan,IMAGE,
                                       generated_dir=self.generated)

    def test_planning_is_read_only_for_generated_files(self):
        result=self._plan()
        self.assertEqual(result['generated_dir'],str(self.generated))
        self.assertEqual(self.original,{p.name:p.read_bytes() for p in self.generated.iterdir() if p.is_file()})
        self.assertIn('kustomization.yaml',result['generated_sha256'])
        self.assertNotIn(self.secret['data']['QUORIVIO_WORKER_TOKEN'],str(result))
        self.assertFalse(any('patch' in a for a,_ in self.fake.calls))

    def test_apply_updates_generated_overlay_and_secret_only_after_rollout(self):
        result=self._plan()
        previous={n:self.original[n] for n in self.original if n not in ('05-app-secret.yaml','kustomization.yaml')}
        result=upgrade.apply_upgrade(self.plan)
        self.assertIn('generated_backup',result)
        for name,content in previous.items():self.assertEqual((self.generated/name).read_bytes(),content)
        self.assertEqual((self.generated/'05-app-secret.yaml').stat().st_mode & 0o777,0o600)
        self.assertIn('QUORIVIO_WORKER_TOKEN', (self.generated/'05-app-secret.yaml').read_text())
        self.assertIn('patches:\n  - path: 95-converter-sidecar-patch.json',
                      (self.generated/'kustomization.yaml').read_text())
        overlay=json.loads((self.generated/upgrade.CONVERTER_OVERLAY).read_text())
        self.assertEqual(overlay['spec']['template']['spec']['containers'][1]['image'],IMAGE)
        self.assertEqual(overlay['metadata'],{'name':'quorivio','namespace':'quorivio'})
        self.assertNotIn('resourceVersion',json.dumps(overlay))
        self.assertNotIn('uid',json.dumps(overlay))
        backups=list((self.generated/'.quorivio-manifest-backups').glob('converter-*'))
        self.assertEqual(len(backups),1)
        self.assertEqual((backups[0]/'05-app-secret.yaml').read_bytes(),self.original['05-app-secret.yaml'])
        self.assertTrue(any('rollout' in a for a,_ in self.fake.calls))

    def test_regeneration_does_not_discard_converter_or_token(self):
        self._plan();upgrade.apply_upgrade(self.plan)
        patch_before=(self.generated/upgrade.CONVERTER_OVERLAY).read_bytes()
        encoded=self.secret['data']['QUORIVIO_WORKER_TOKEN']
        wizard.generate(dict(wizard.DEFAULTS),self.generated)
        self.assertEqual((self.generated/upgrade.CONVERTER_OVERLAY).read_bytes(),patch_before)
        self.assertIn('  - path: '+upgrade.CONVERTER_OVERLAY,(self.generated/'kustomization.yaml').read_text())
        self.assertIn('  QUORIVIO_WORKER_TOKEN: '+encoded,(self.generated/'05-app-secret.yaml').read_text())

    def test_reconciliation_after_old_wizard_existing_live_converter(self):
        self._plan();upgrade.apply_upgrade(self.plan)
        (self.generated/upgrade.CONVERTER_OVERLAY).unlink()
        (self.generated/'kustomization.yaml').write_bytes(self.original['kustomization.yaml'])
        (self.generated/'05-app-secret.yaml').write_bytes(self.original['05-app-secret.yaml'])
        backup=upgrade.reconcile_generated(self.generated,'quorivio','quorivio')
        self.assertTrue(Path(backup).is_dir())
        self.assertTrue((self.generated/upgrade.CONVERTER_OVERLAY).is_file())

    def test_refuse_generated_file_changed_after_planning_before_cluster_patch(self):
        self._plan()
        path=self.generated/'kustomization.yaml'
        path.write_text(path.read_text()+'# manual user edit\n')
        with self.assertRaisesRegex(upgrade.UpgradeError,'generated files changed'):
            upgrade.apply_upgrade(self.plan)
        self.assertFalse(any('patch' in a for a,_ in self.fake.calls))

    def test_secret_drift_rejected_without_cluster_change(self):
        self.fake.secret['data']['DATABASE_URL']=base64.b64encode(b'rotated elsewhere').decode()
        with self.assertRaisesRegex(upgrade.UpgradeError,'differs from live'):
            self._plan()
        self.assertFalse(self.plan.exists())
        self.assertFalse(any('patch' in a for a,_ in self.fake.calls))

    def test_generated_wrong_deployment_rejected_without_cluster_patch(self):
        path=self.generated/'20-deployment.yaml'
        path.write_text(path.read_text().replace('name: quorivio\n  namespace','name: someone-else\n  namespace',1))
        with self.assertRaisesRegex(upgrade.UpgradeError,'identity differs'):
            self._plan()
        self.assertFalse(any('patch' in a for a,_ in self.fake.calls))

    def test_generated_symlink_rejected(self):
        target=self.generated/'20-deployment.yaml'
        content=target.read_bytes()
        target.unlink()
        target.symlink_to(self.root/'elsewhere')
        with self.assertRaisesRegex(upgrade.UpgradeError,'regular wizard file'):
            self._plan()
        self.assertFalse((self.root/'elsewhere').exists())

    def test_generated_custom_patches_preserved_during_sync(self):
        self._plan();upgrade.apply_upgrade(self.plan)
        k=self.generated/'kustomization.yaml'
        k.write_text(k.read_text().replace('patches:\n  - path:', 'patches:\n  - path: manual.json\n  - path:'))
        # Allowed merge only with our exact patch; accidental extra custom
        # patches are preserved, not erased by the wizard.
        upgrade.reconcile_generated(self.generated,'quorivio','quorivio')
        self.assertIn('  - path: manual.json',k.read_text())
        self.assertIn('  - path: '+upgrade.CONVERTER_OVERLAY,k.read_text())

    def test_reconcile_token_only_does_not_create_overlay(self):
        backup=upgrade.reconcile_generated_token(self.generated,'quorivio','quorivio')
        self.assertTrue(Path(backup).exists())
        self.assertFalse((self.generated/upgrade.CONVERTER_OVERLAY).exists())
        self.assertEqual((self.generated/'kustomization.yaml').read_bytes(),self.original['kustomization.yaml'])
        self.assertIn('QUORIVIO_WORKER_TOKEN',(self.generated/'05-app-secret.yaml').read_text())

    def test_sync_refuses_missing_live_converter_without_modifying_generated(self):
        with self.assertRaisesRegex(upgrade.UpgradeError,'absent or ambiguous'):
            upgrade.reconcile_generated(self.generated,'quorivio','quorivio')
        self.assertEqual(self.original,{p.name:p.read_bytes() for p in self.generated.iterdir() if p.is_file()})

    def test_generated_auto_discovery_and_ambiguous_path(self):
        with patch.object(wizard.Path,'cwd',return_value=self.root):
            self.assertEqual(wizard._generated_directory_from_args(None),self.generated)
            (self.root/'k8s-generated').mkdir()
            (self.root/'k8s-generated/kustomization.yaml').touch()
            (self.root/'k8s-generated/quorivio-overrides.json').touch()
            with self.assertRaisesRegex(ValueError,'Multiple generated'):
                wizard._generated_directory_from_args(None)

    def test_standalone_no_repo_files_in_token_and_sync(self):
        standalone=self.root/'k8s_wizard.py'
        shutil.copy2(ROOT/'tools/k8s_wizard.py',standalone)
        fake=self.root/'fake-kubectl';fake.write_text(FAKE_KUBECTL);fake.chmod(0o700)
        state=self.root/'state.json'
        db={'deployment/quorivio':self.dep,'secret/quorivio-app-secrets':self.secret}
        # Simulate successfully installed live converter from an older wizard.
        patch_ops,_=upgrade.build_patch(self.dep,None,'quorivio-app-secrets',IMAGE)
        from tools.tests.test_rc246_converter_upgrade import apply_json_patch
        db['deployment/quorivio']=apply_json_patch(self.dep,patch_ops)
        state.write_text(json.dumps(db))
        env={**os.environ,'FAKE_KUBECTL_STATE':str(state),'PYTHONPATH':''}
        result=subprocess.run([sys.executable,str(standalone),'--no-self-update','--sync-generated',
              '--kubectl',str(fake),'--generated-dir',str(self.generated),'--set','namespace=quorivio','--set','name=quorivio'],
              cwd=self.root,env=env,capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Generated Kustomize manifests reconciled',result.stdout)
        self.assertTrue((self.generated/upgrade.CONVERTER_OVERLAY).is_file())
        self.assertFalse((self.root/'k8s_converter_upgrade.py').exists())


if __name__=='__main__':unittest.main()
