"""Cycle24 security guard and disposable Kubernetes runtime acceptance contracts."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from k8s_wizard import DEFAULTS,generate,guarded_output_directory
import ci_k8s_runtime_smoke as runtime


class GeneratorPathHardening(unittest.TestCase):
    def test_symlink_output_directory_refused_before_secret_generation(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)
            target=p/'real';target.mkdir()
            linked=p/'linked';linked.symlink_to(target,target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlink'):
                generate(dict(DEFAULTS),linked)
            self.assertEqual(list(target.iterdir()),[])

    def test_dangling_symlink_output_refused(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)
            linked=p/'linked';linked.symlink_to(p/'missing-dir',target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlink'):
                guarded_output_directory(linked)
            self.assertFalse((p/'missing-dir').exists())

    def test_symlink_parent_directory_refused(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)
            actual=p/'real';actual.mkdir()
            (p/'alias').symlink_to(actual,target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'symlink'):
                generate(dict(DEFAULTS),p/'alias'/'nested')
            self.assertFalse((actual/'nested').exists())

    def test_file_output_path_refused(self):
        with tempfile.TemporaryDirectory() as root:
            dest=Path(root)/'output';dest.write_text('UNCHANGED')
            with self.assertRaisesRegex(ValueError,'directory'):
                generate(dict(DEFAULTS),dest)
            self.assertEqual(dest.read_text(),'UNCHANGED')

    def test_new_output_directory_created_private(self):
        with tempfile.TemporaryDirectory() as root:
            dest=Path(root)/'output';generate(dict(DEFAULTS),dest)
            self.assertEqual(dest.stat().st_mode&0o777,0o700)
            self.assertEqual((dest/'05-app-secret.yaml').stat().st_mode&0o777,0o600)


class KindRuntimeSmokeContracts(unittest.TestCase):
    def test_runtime_test_is_strictly_opt_in_and_unpublished(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('inputs.kubernetes_runtime_test',workflow)
        self.assertIn("github.event_name == 'workflow_dispatch' && inputs.kubernetes_runtime_test",workflow)
        self.assertIn('kind load docker-image quorivio:kind-runtime',workflow)
        self.assertIn('docker build -t quorivio:kind-runtime .',workflow)
        self.assertNotIn('docker push',workflow[workflow.index('  kubernetes-runtime:'):workflow.index('  runtime-architecture:')])

    def test_disposable_cluster_guard_rejects_wrong_context(self):
        with patch.object(runtime,'cmd',return_value='kind-not-my-cluster\n') as mock:
            with self.assertRaisesRegex(RuntimeError,'outside disposable KIND'):
                runtime.ensure_clean_cluster()
            self.assertEqual(mock.call_count,1)

    def test_single_node_ci_volume_does_not_claim_production_rwx(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=runtime.write_private_pv(Path(tmp))
            manifest=json.loads(path.read_text())
            self.assertEqual(manifest['spec']['accessModes'],['ReadWriteMany'])
            self.assertEqual(manifest['spec']['hostPath']['type'],'Directory')
            self.assertEqual(manifest['spec']['storageClassName'],runtime.PVC_CLASS)
            self.assertIn('ci',runtime.PVC_CLASS)
            self.assertNotIn('production',runtime.__doc__.lower().split('no ingress')[0])

    def test_storage_class_is_no_provisioner_and_single_node_only(self):
        script=(ROOT/'tools/ci_k8s_runtime_smoke.py').read_text()
        self.assertIn("'provisioner':'kubernetes.io/no-provisioner'",script)
        self.assertIn("'volumeBindingMode':'Immediate'",script)
        self.assertIn("'hostPath'",script)
        self.assertNotIn('kubectl apply -k',script)

    def test_service_probe_rejects_unsupported_path(self):
        with self.assertRaisesRegex(ValueError,'Unexpected'):
            runtime.service_probe('pod','/api/admin/secrets')

    def test_probe_calls_real_clusterip_and_checks_response(self):
        with patch.object(runtime,'cmd') as run:
            runtime.service_probe('safe-pod','/api/health/ready')
        args=run.call_args.args
        self.assertEqual(args[:5],('kubectl','-n',runtime.NAMESPACE,'exec','safe-pod'))
        self.assertTrue(any('.svc.cluster.local' in str(x) for x in args))
        self.assertTrue(any('if(!r.ok)' in str(x) for x in args))

    def test_rw_volume_probe_writes_reads_and_cleans_up(self):
        with patch.object(runtime,'cmd') as run:
            runtime.shared_volume_probe('pod-a','pod-b')
        self.assertEqual(run.call_count,3)
        self.assertIn('pod-a',run.call_args_list[0].args)
        self.assertIn('pod-b',run.call_args_list[1].args)
        self.assertIn('pod-a',run.call_args_list[2].args)
        self.assertIn('unlinkSync',str(run.call_args_list[2].args))

    def test_rw_volume_probe_cleans_up_after_read_failure(self):
        def fake(*args,**kwargs):
            if 'pod-b' in args:raise RuntimeError('simulated reader failure')
        with patch.object(runtime,'cmd',side_effect=fake) as run:
            with self.assertRaisesRegex(RuntimeError,'reader failure'):
                runtime.shared_volume_probe('pod-a','pod-b')
        self.assertEqual(run.call_count,3)

    def test_run_command_redacts_private_output_on_failure(self):
        from subprocess import CompletedProcess
        with patch.object(runtime.subprocess,'run',return_value=CompletedProcess(['kubectl'],1,stdout='a-password',stderr='a-password')):
            with self.assertRaises(RuntimeError) as ctx:runtime.cmd('kubectl','apply','-f','secret.yaml')
        self.assertNotIn('a-password',str(ctx.exception))

if __name__=='__main__':unittest.main()
