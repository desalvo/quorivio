"""RC261: sync a newly published converter digest into generated without drift."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
from tools.tests.test_rc260_generated_manifest_reconciliation import GeneratedManifestReconciliation
import k8s_converter_upgrade as upgrade


class ConverterImageSync(GeneratedManifestReconciliation):
    # Inherits all earlier RC260 reconciliation behavior. The focused tests
    # below exercise only permitted image drift and forbid unrelated changes.
    def test_safe_image_only_refresh_updates_local_kustomize_without_cluster_writes(self):
        self._plan()
        upgrade.apply_upgrade(self.plan)
        replacement='desalvo/quorivio-converter@sha256:'+'a'*64
        self.fake.deploy['spec']['template']['spec']['containers'][1]['image']=replacement
        initial_patch=(self.generated/upgrade.CONVERTER_OVERLAY).read_bytes()
        call_count=len(self.fake.calls)
        backup=upgrade.reconcile_generated(self.generated,'quorivio','quorivio')
        self.assertTrue(Path(backup).is_dir())
        self.assertFalse(any('patch' in x or 'rollout' in x for x,_ in self.fake.calls[call_count:]))
        updated=json.loads((self.generated/upgrade.CONVERTER_OVERLAY).read_text())
        self.assertEqual(updated['spec']['template']['spec']['containers'][1]['image'],replacement)
        self.assertEqual((Path(backup)/upgrade.CONVERTER_OVERLAY).read_bytes(),initial_patch)
        self.assertIn('95-converter-sidecar-patch.json',(self.generated/'kustomization.yaml').read_text())
        self.assertEqual((self.generated/'05-app-secret.yaml').stat().st_mode & 0o777,0o600)

    def test_unrelated_converter_drift_is_still_rejected(self):
        self._plan()
        upgrade.apply_upgrade(self.plan)
        self.fake.deploy['spec']['template']['spec']['containers'][1]['securityContext']['allowPrivilegeEscalation']=True
        before=(self.generated/upgrade.CONVERTER_OVERLAY).read_bytes()
        with self.assertRaisesRegex(upgrade.UpgradeError,'differs from live'):
            upgrade.reconcile_generated(self.generated,'quorivio','quorivio')
        self.assertEqual((self.generated/upgrade.CONVERTER_OVERLAY).read_bytes(),before)

if __name__=='__main__':unittest.main()
