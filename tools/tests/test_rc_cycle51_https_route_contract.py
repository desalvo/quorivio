"""Cycle 51: guard the actual KIND HTTPS call signatures and TLS failure semantics.

A test which calls a keyword-only API positionally must be rejected before the
costly KIND cluster starts. No test grants production TLS or CSI credit.
"""
from __future__ import annotations

import ast
import base64
import http.server
import inspect
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import ci_k8s_multinode_ingress_smoke as cluster


class RouteContract(unittest.TestCase):
    def test_all_https_calls_respect_keyword_only_route_api(self):
        tree = ast.parse((ROOT/'tools/ci_k8s_multinode_ingress_smoke.py').read_text())
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == 'https_ingress_probe']
        self.assertGreaterEqual(len(calls), 6)
        signature = inspect.signature(cluster.https_ingress_probe)
        for n in calls:
            self.assertEqual(len(n.args), 1, f'line {n.lineno}: keyword-only route passed positionally')
            keywords = {k.arg for k in n.keywords}
            self.assertTrue({'ingress','certificate_b64'}.issubset(keywords), n.lineno)
            self.assertIn('path', signature.parameters)
            signature.bind('some-pod', **{k: '/api/health/ready' if k == 'path' else 'test'
                                          for k in keywords})

    def test_bad_untrusted_chain_cannot_pass_for_hostname_or_expired_cert(self):
        source = cluster.https_probe_source()
        self.assertIn('rejectUnauthorized:true', source)
        self.assertNotIn('rejectUnauthorized:false', source)
        self.assertIn('DEPTH_ZERO_SELF_SIGNED_CERT', source)
        self.assertIn('UNABLE_TO_GET_ISSUER_CERT_LOCALLY', source)
        self.assertNotIn("'ERR_TLS_CERT_ALTNAME_INVALID'].includes(err.code)", source)
        self.assertNotIn("'CERT_HAS_EXPIRED'", source)

    def test_wrong_host_still_requires_404_under_valid_tls(self):
        captured = []
        original = cluster.node_script
        try:
            cluster.node_script = lambda *args: captured.append(args)
            cluster.https_ingress_probe('pod-a', ingress='private.example:443',
                                         certificate_b64='Y2VydA==', bad_host=True)
        finally:
            cluster.node_script = original
        self.assertEqual(captured[0][3], 'unknown.example.invalid')
        self.assertEqual(captured[0][4], '404')
        self.assertEqual(captured[0][6], 'trusted')

    def test_entire_kind_https_flow_both_controllers_with_bounded_kubectl_simulator(self):
        """Exercise the real main() control flow; no cluster credentials or network."""
        for controller in ('nginx', 'haproxytech'):
            with self.subTest(controller=controller):
                probes, shell_calls = [], []
                def fake_run(*args, **kwargs):
                    shell_calls.append(args)
                    return ''
                def fake_generate(cfg, folder):
                    folder.mkdir(parents=True)
                    (folder/'10-configmap.yaml').write_text(
                        f'PUBLIC_BASE_URL: "https://{cluster.HOST}"\n')
                    (folder/'40-ingress.yaml').write_text(
                        f'secretName: {cluster.TLS_SECRET}\n')
                def fake_probe(pod, *, ingress, certificate_b64,
                               path='/api/health/ready', bad_host=False, untrusted=False):
                    self.assertEqual(certificate_b64, 'Y2VydA==')
                    self.assertTrue(ingress.endswith(':443'))
                    probes.append((pod, path, bad_host, untrusted))
                with (patch.object(cluster, 'checked_context'),
                      patch.object(cluster, 'workers', return_value=['worker-a','worker-b']),
                      patch.object(cluster, 'run', side_effect=fake_run),
                      patch.object(cluster, 'validate', side_effect=lambda cfg: cfg),
                      patch.object(cluster, 'generate', side_effect=fake_generate),
                      patch.object(cluster, 'issue_ephemeral_https_cert', return_value='Y2VydA=='),
                      patch.object(cluster, 'install_ingress', return_value='nginx:80'),
                      patch.object(cluster, 'haproxy_ingress_service', return_value='haproxy:443'),
                      patch.object(cluster, 'assert_distribution', return_value={
                          'pod-a': 'worker-a', 'pod-b': 'worker-b'}),
                      patch.object(cluster, 'pods', return_value={
                          'pod-a': 'worker-a', 'pod-c': 'worker-b'}),
                      patch.object(cluster, 'shared_mount_check'),
                      patch.object(cluster, 'https_ingress_probe', side_effect=fake_probe)):
                    cluster.main(controller, https=True)
                self.assertIn(('pod-b', '/', False, False), probes)
                self.assertIn(('pod-a', '/api/health/ready', True, False), probes)
                self.assertIn(('pod-a', '/api/health/ready', False, True), probes)
                self.assertIn(('pod-a', '/api/health/live', False, False), probes)
                self.assertTrue(any('delete' in call and 'pod-b' in call for call in shell_calls))

    def test_project_remains_conservative_about_untested_kubernetes(self):
        import json
        matrix = json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        residual = next(x for x in matrix['gates'] if x['id'] == 'B4')
        self.assertEqual(residual['status'], 'partial')
        self.assertIn('RWX', residual['remaining'])
        self.assertIn('HTTPS', (ROOT/'tools/ci_k8s_multinode_ingress_smoke.py').read_text())


if __name__ == '__main__':
    unittest.main()
