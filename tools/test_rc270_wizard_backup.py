"""RC270 Kubernetes wizard backup/PVC regression tests (stdlib only)."""
import base64
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
import re

WIZARD=Path(__file__).with_name('k8s_wizard.py')

class BackupWizardTests(unittest.TestCase):
    def render(self, *settings):
        tmp=tempfile.TemporaryDirectory(prefix='quorivio-rc270-wizard-')
        proc=subprocess.run([sys.executable,str(WIZARD),'--no-self-update','--unattended','--output',tmp.name,*sum((['--set',p] for p in settings),[])],capture_output=True,text=True)
        self.addCleanup(tmp.cleanup)
        return proc,Path(tmp.name)
    def test_posix_schedule_and_sealed_bootstrap_secret(self):
        r,d=self.render('backup_posix_enabled=true','backup_default_backend=posix','backup_directory=nightly','backup_schedule_enabled=true')
        self.assertEqual(r.returncode,0,r.stderr)
        deployment=(d/'20-deployment.yaml').read_text()
        self.assertIn('mountPath: /app/backups-posix',deployment)
        self.assertIn('mountPath: /tmp',deployment)
        self.assertIn('kind: PersistentVolumeClaim',(d/'17-backup-pvc.yaml').read_text())
        secret=(d/'05-app-secret.yaml').read_text()
        match=re.search(r'(?m)^  QUORIVIO_BACKUP_BOOTSTRAP_TARGET_JSON: ([A-Za-z0-9+/=]+)$',secret)
        self.assertIsNotNone(match)
        bootstrap=json.loads(base64.b64decode(match.group(1)))
        self.assertEqual(bootstrap,{'backend':'posix','directory':'nightly'})
        self.assertTrue((d/'05-app-secret.yaml').stat().st_mode & 0o077 == 0)
    def test_direct_nfs_pod_mount(self):
        r,d=self.render('backup_nfs_enabled=true','backup_nfs_host=nfs.example.org','backup_nfs_path=/exports/quorivio','backup_default_backend=nfs')
        self.assertEqual(r.returncode,0,r.stderr)
        deployment=(d/'20-deployment.yaml').read_text()
        self.assertIn('server: \"nfs.example.org\"',deployment)
        self.assertIn('path: \"/exports/quorivio\"',deployment)
        self.assertFalse((d/'17-backup-pvc.yaml').exists())
    def test_invalid_replicated_rwo_volume_rejected(self):
        r,_=self.render('replicas=2','asset_access_mode=ReadWriteMany','backup_posix_enabled=true')
        self.assertNotEqual(r.returncode,0)
        self.assertIn('RWX',r.stderr)
    def test_s3_keys_hidden_from_standard_output(self):
        r,d=self.render('backup_default_backend=s3','backup_bucket=my-backups','backup_access_key=ACCESSKEY','backup_secret_key=PRIVATESECRET')
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertNotIn('PRIVATESECRET',r.stdout)
        self.assertNotIn('PRIVATESECRET',(d/'10-configmap.yaml').read_text())
        self.assertIn('QUORIVIO_BACKUP_BOOTSTRAP_TARGET_JSON',(d/'05-app-secret.yaml').read_text())

if __name__=='__main__':unittest.main()
