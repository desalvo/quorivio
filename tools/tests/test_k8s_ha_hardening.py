"""Cycle23: generated K8s resilience and secure atomic credential writing."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from k8s_wizard import DEFAULTS,generate,validate,secure_write


class KubernetesHA(unittest.TestCase):
    def output(self,**kw):
        cfg=validate({**DEFAULTS,**kw})
        root=tempfile.TemporaryDirectory()
        self.addCleanup(root.cleanup)
        p=Path(root.name)
        generate(cfg,p)
        return p

    def test_single_replica_has_no_pdb(self):
        p=self.output()
        self.assertFalse((p/'25-disruption-budget.yaml').exists())
        self.assertNotIn('25-disruption-budget.yaml',(p/'kustomization.yaml').read_text())
        self.assertNotIn('topologySpreadConstraints:',(p/'20-deployment.yaml').read_text())

    def test_three_replicas_have_safe_disruption_budget_and_rolling_update(self):
        p=self.output(replicas=3,asset_access_mode='ReadWriteMany')
        deployment=(p/'20-deployment.yaml').read_text()
        disruption=(p/'25-disruption-budget.yaml').read_text()
        self.assertIn('maxUnavailable: 0',deployment)
        self.assertIn('maxSurge: 1',deployment)
        self.assertIn('terminationGracePeriodSeconds: 45',deployment)
        self.assertIn('topologyKey: kubernetes.io/hostname',deployment)
        self.assertIn('whenUnsatisfiable: ScheduleAnyway',deployment)
        self.assertIn('minAvailable: 2',disruption)
        self.assertIn('app: quorivio',disruption)
        self.assertIn('25-disruption-budget.yaml',(p/'kustomization.yaml').read_text())

    def test_scale_down_removes_stale_pdb(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)
            generate(validate({**DEFAULTS,'replicas':2,'asset_access_mode':'ReadWriteMany'}),p)
            self.assertTrue((p/'25-disruption-budget.yaml').exists())
            generate(dict(DEFAULTS),p)
            self.assertFalse((p/'25-disruption-budget.yaml').exists())
            self.assertNotIn('25-disruption-budget.yaml',(p/'kustomization.yaml').read_text())

    def test_multi_replica_rejects_rwo(self):
        with self.assertRaises(ValueError):validate({**DEFAULTS,'replicas':2})

    def test_noninteger_and_out_of_range_values_rejected(self):
        for field,value in (('replicas','3'),('replicas',True),('replicas',0),
                            ('max_upload_mb','100'),('max_upload_mb',False),
                            ('container_port',0),('postgres_port',-1)):
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):
                validate({**DEFAULTS,field:value})

    def test_cli_typed_numeric_overrides_persist(self):
        with tempfile.TemporaryDirectory() as root:
            cmd=[sys.executable,str(ROOT/'tools/k8s_wizard.py'),'--unattended',
                 '--output',root,'--set','replicas=2','--set','asset_access_mode=ReadWriteMany',
                 '--set','max_upload_mb=150','--set','container_port=8085']
            process=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
            self.assertEqual(process.returncode,0,process.stderr)
            self.assertIn('replicas: 2',(Path(root)/'20-deployment.yaml').read_text())
            saved=json.loads((Path(root)/'quorivio-overrides.json').read_text())
            self.assertEqual((saved['replicas'],saved['max_upload_mb'],saved['container_port']),(2,150,8085))
            self.assertTrue((Path(root)/'25-disruption-budget.yaml').exists())

    def test_secret_and_saved_overrides_reject_symlink(self):
        for filename in ('05-app-secret.yaml','quorivio-overrides.json'):
            with self.subTest(filename=filename),tempfile.TemporaryDirectory() as root:
                base=Path(root)
                victim=base/'victim'
                victim.write_text('DO NOT ALTER')
                (base/filename).symlink_to(victim)
                with self.assertRaisesRegex(ValueError,'symlink'):
                    generate(dict(DEFAULTS),base)
                self.assertEqual(victim.read_text(),'DO NOT ALTER')

    def test_secure_write_failure_does_not_truncate_old_secret(self):
        with tempfile.TemporaryDirectory() as root:
            target=Path(root)/'private-file'
            secure_write(target,'old-data')
            with patch('k8s_wizard.os.replace',side_effect=OSError('simulated failed atomic replace')):
                with self.assertRaises(OSError):secure_write(target,'new-data')
            self.assertEqual(target.read_text(),'old-data')
            self.assertEqual(list(Path(root).glob('.quorivio-atomic-*')),[])

    def test_credentials_stable_and_private_after_second_generation(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)
            generate(dict(DEFAULTS),p)
            first={f.name:f.read_bytes() for f in p.iterdir()}
            generate(dict(DEFAULTS),p)
            self.assertEqual(first,{f.name:f.read_bytes() for f in p.iterdir()})
            for key in ('05-app-secret.yaml','quorivio-overrides.json'):
                self.assertEqual((p/key).stat().st_mode&0o777,0o600)
            self.assertEqual((p/'20-deployment.yaml').stat().st_mode&0o777,0o644)

    def test_manifest_variants_keep_private_secrets_and_tls(self):
        for variant in (
          {'ingress_controller':'nginx'},
          {'ingress_controller':'haproxy','haproxy_variant':'community'},
          {'ingress_controller':'haproxy','haproxy_variant':'haproxytech','tls_secret':'cert-test'},
        ):
            with self.subTest(variant=variant):
                p=self.output(replicas=2,asset_access_mode='ReadWriteMany',**variant)
                self.assertNotIn('POSTGRES_PASSWORD',(p/'20-deployment.yaml').read_text())
                self.assertIn('minAvailable: 1',(p/'25-disruption-budget.yaml').read_text())
                self.assertIn('ingressClassName:',(p/'40-ingress.yaml').read_text())

    def test_service_readiness_and_websocket_draining(self):
        source=(ROOT/'apps/api/src/server.ts').read_text()
        self.assertIn("status:'draining'",source)
        self.assertIn('shutdownRequested',source)
        self.assertIn("peer.close(1012,'service_restart')",source)
        self.assertIn("process.on('SIGTERM'",source)
        self.assertIn('server.close(async error=>',source)
        self.assertIn('socket.destroy();return;',source)

    def test_disposable_postgres_sigterm_runs_after_load_and_before_cleanup(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertLess(workflow.index('python3 tools/ci_capacity_500.py'),workflow.index('python3 tools/ci_graceful_shutdown.py'))
        self.assertLess(workflow.index('python3 tools/ci_graceful_shutdown.py'),workflow.index('python3 tools/ci_backup_restore.py'))
        script=(ROOT/'tools/ci_graceful_shutdown.py').read_text()
        for needle in ("signal.SIGTERM",'await wait_for_restart_close(ws)','status==503','response.status==200'):
            self.assertIn(needle,script)

    def test_kind_job_is_opt_in_and_does_not_publish(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn("inputs.kubernetes_manifest_test",workflow)
        self.assertIn('helm/kind-action@v1.12.0',workflow)
        self.assertIn('python3 tools/ci_k8s_apiserver_smoke.py',workflow)
        script=(ROOT/'tools/ci_k8s_apiserver_smoke.py').read_text()
        self.assertIn("'--dry-run=server'",script)
        self.assertNotIn("'apply','-k'",script)

if __name__=='__main__':unittest.main()
