"""Functional deployment contracts and negative checks for RC cycle 29."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from k8s_wizard import DEFAULTS, generate, validate
import ci_k8s_multinode_ingress_smoke as multi


class PublicOriginAndSpread(unittest.TestCase):
    def render(self, **settings):
        with tempfile.TemporaryDirectory(prefix='quorivio-cycle29-test-') as directory:
            generate(validate({**DEFAULTS, **settings}), Path(directory))
            return {f.name: f.read_text() for f in Path(directory).glob('*.yaml')}

    def test_plain_http_ingress_uses_http_origin_without_tls(self):
        doc = self.render(host='quorivio.test.invalid', tls_termination=False)
        self.assertIn('PUBLIC_BASE_URL: "http://quorivio.test.invalid"', doc['10-configmap.yaml'])
        self.assertNotIn('  tls:', doc['40-ingress.yaml'])

    def test_tls_ingress_keeps_https_origin_and_optional_secret(self):
        doc = self.render(host='quorivio.test.invalid', tls_termination=True, tls_secret='')
        self.assertIn('PUBLIC_BASE_URL: "https://quorivio.test.invalid"', doc['10-configmap.yaml'])
        self.assertIn('  tls:', doc['40-ingress.yaml'])
        self.assertNotIn('secretName:', doc['40-ingress.yaml'])

    def test_strict_node_spread_must_be_explicit_and_replicated(self):
        with self.assertRaisesRegex(ValueError, 'Node diversity requires'):
            validate({**DEFAULTS, 'enforce_node_diversity': True})
        for invalid in (1, 'true', None, 0):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                validate({**DEFAULTS, 'enforce_node_diversity': invalid, 'replicas': 2})

    def test_two_node_strict_spread_with_selector_and_disruption_budget(self):
        doc = self.render(replicas=2, enforce_node_diversity=True,
                          asset_access_mode='ReadWriteMany',
                          app_node_selector='quorivio-ci-worker=yes')
        deploy = doc['20-deployment.yaml']
        self.assertIn('whenUnsatisfiable: DoNotSchedule', deploy)
        self.assertIn('minDomains: 2', deploy)
        self.assertIn('"quorivio-ci-worker": "yes"', deploy)
        self.assertIn('maxUnavailable: 0', deploy)
        self.assertIn('minAvailable: 1', doc['25-disruption-budget.yaml'])

    def test_nonstrict_multi_still_allows_single_node_ci(self):
        doc = self.render(replicas=2, asset_access_mode='ReadWriteMany')
        self.assertIn('whenUnsatisfiable: ScheduleAnyway', doc['20-deployment.yaml'])
        self.assertNotIn('minDomains:', doc['20-deployment.yaml'])

    def test_replica_placement_requires_shared_assets(self):
        with self.assertRaisesRegex(ValueError, 'ReadWriteMany'):
            validate({**DEFAULTS, 'replicas': 2, 'enforce_node_diversity': True})


class MultiNodeScriptContracts(unittest.TestCase):
    def test_context_is_fail_closed(self):
        with patch.object(multi, 'run', return_value='kind-production\n'):
            with self.assertRaisesRegex(RuntimeError, 'outside'):
                multi.checked_context()
        with patch.object(multi, 'run', return_value=f'kind-{multi.CLUSTER}\n'):
            multi.checked_context()

    def test_exact_two_worker_nodes(self):
        def fixture(names):
            return json.dumps({'items': [{'metadata': {'name': n, 'labels':
                {'node-role.kubernetes.io/control-plane': ''} if 'control' in n else {}}}
                for n in names]})
        with patch.object(multi, 'run', return_value=fixture(['control', 'worker-1', 'worker-2'])):
            self.assertEqual(multi.workers(), ['worker-1', 'worker-2'])
        with patch.object(multi, 'run', return_value=fixture(['control', 'worker-1'])):
            with self.assertRaisesRegex(RuntimeError, 'precisely two'):
                multi.workers()

    def test_refuse_collocated_and_missing_replica(self):
        with patch.object(multi, 'pods', return_value={'app-a': 'worker-1', 'app-b': 'worker-1'}):
            with self.assertRaisesRegex(RuntimeError, 'separate'):
                multi.assert_distribution(['worker-1', 'worker-2'])
        with patch.object(multi, 'pods', return_value={'app-a': 'worker-1'}):
            with self.assertRaises(RuntimeError):
                multi.assert_distribution(['worker-1', 'worker-2'])

    def test_inspects_distinct_pod_nodes(self):
        with patch.object(multi, 'pods', return_value={'app-b': 'worker-2', 'app-a': 'worker-1'}):
            self.assertEqual(len(multi.assert_distribution(['worker-1', 'worker-2'])), 2)

    def test_host_rejection_probe_is_mandatory(self):
        with patch.object(multi, 'node_script') as node:
            multi.ingress_probe('app-a', bad_host=True)
            self.assertEqual(node.call_args.args[-2:], ('unknown.example.invalid', '404'))
            multi.ingress_probe('app-a')
            self.assertEqual(node.call_args.args[-2:], (multi.HOST, '200'))
            with self.assertRaises(ValueError):
                multi.ingress_probe('app-a', '/admin/secret')

    def test_writes_private_runner_scoped_hostpath_pv(self):
        with tempfile.TemporaryDirectory() as td:
            result = json.loads(multi.write_pv(Path(td)/'pv.json').read_text())
            self.assertEqual(result['spec']['hostPath']['path'], '/var/local/quorivio-ci-rwx')
            self.assertEqual(result['spec']['accessModes'], ['ReadWriteMany'])
            self.assertEqual(result['spec']['storageClassName'], multi.CLASS)

    def test_kubectl_failure_redacts_output(self):
        from subprocess import CompletedProcess
        with patch.object(multi.subprocess, 'run', return_value=CompletedProcess(['kubectl'], 3, 'sensitive-data', 'secret-data')):
            with self.assertRaises(RuntimeError) as context:
                multi.run('kubectl', 'get', 'secret')
            self.assertNotIn('secret-data', str(context.exception))
            self.assertNotIn('sensitive-data', str(context.exception))

    def test_real_remote_runtime_credit_but_no_credit_for_new_untested_kind(self):
        from rc_gate_audit import audit
        from rc_release_preflight import preflight
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        by_id={g['id']:g for g in matrix['gates']}
        self.assertEqual((audit()['score'],preflight()['accepted_gates'],len(matrix['gates'])),
                         (81.75,38,55))
        self.assertEqual(len(preflight()['unaccepted_gates']),17)
        self.assertEqual((by_id['D3']['weight'],by_id['D3']['status']),(0.5,'partial'))
        proof=by_id['D3-OCI-ROOTLESS-RUNTIME']
        self.assertEqual((proof['weight'],proof['status']),(0.5,'accepted'))
        self.assertEqual(proof['verified_run_ids'],[40980312270,40982728705])
        receipt=matrix['rc_cycle29_multinode_local_20261030']
        self.assertEqual((receipt['score_before'],receipt['score_after']),(79,79.25))
        self.assertFalse(receipt['new_kubernetes_multinode_runtime_executed'])
        self.assertFalse(receipt['production_csi_rwx_verified'])
        self.assertFalse(preflight()['release_candidate_ready'])

    def test_ci_job_is_manual_and_does_not_publish(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn("if: github.event_name == 'workflow_dispatch' && inputs.kubernetes_multinode_test", workflow)
        self.assertIn('config: tools/ci_kind_multinode.yaml', workflow)
        self.assertIn('python3 tools/ci_k8s_multinode_ingress_smoke.py', workflow)
        self.assertIn('kind load docker-image quorivio:kind-multinode', workflow)
        self.assertNotIn('docker push', workflow[workflow.index('  kubernetes-multinode-ingress:'):workflow.index('  runtime-architecture:')])

    def test_helm_pdb_and_spread_parity(self):
        values=(ROOT/'helm/quorivio/values.yaml').read_text()
        deploy=(ROOT/'helm/quorivio/templates/deployment.yaml').read_text()
        pdb=(ROOT/'helm/quorivio/templates/pdb.yaml').read_text()
        for fragment in ('enforceNodeDiversity: false', 'replicaCount: 1'):
            self.assertIn(fragment, values)
        for fragment in ('minDomains: 2', 'DoNotSchedule', 'ReadWriteMany', 'maxUnavailable: 0'):
            self.assertIn(fragment, deploy)
        self.assertIn('minAvailable:', pdb)
        self.assertIn('matchLabels:', pdb)

if __name__ == '__main__':
    unittest.main()
