"""Cycle 50: strict real-HTTPS KIND test contract, with loopback TLS smoke.

The local loopback server tests the exact node:https probe script. It is NOT
Kubernetes, an independent physical host or a publicly trusted certificate.
"""
from __future__ import annotations

import base64
import http.server
import importlib.util
import json
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import ci_k8s_multinode_ingress_smoke as tls


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        host = self.headers.get('Host')
        if host != tls.HOST:
            self.send_response(404)
            self.end_headers()
            return
        if self.path not in ('/', '/api/health/live', '/api/health/ready'):
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ALIVE')

    def log_message(self, *args):
        pass


class TLSProbe(unittest.TestCase):
    def test_https_mode_writes_explicit_sni_and_requires_certificate_validation(self):
        code = tls.https_probe_source()
        self.assertIn('servername:process.argv[6]', code)
        self.assertIn('rejectUnauthorized:true', code)
        self.assertNotIn('rejectUnauthorized:false', code)
        self.assertIn('DEPTH_ZERO_SELF_SIGNED_CERT', code)

    def test_selected_tls_service_must_be_port_443(self):
        for address in ('ingress.svc.cluster.local', 'ingress.svc.cluster.local:80'):
            with self.assertRaises(ValueError):
                tls.https_ingress_probe('pod-a', ingress=address, certificate_b64='YQ==')

    def test_trusted_pinned_certificate_required(self):
        with self.assertRaises(ValueError):
            tls.https_ingress_probe('pod-a', ingress='ingress.svc.cluster.local:443', certificate_b64='')

    def test_only_health_and_root_paths_allowed(self):
        with self.assertRaises(ValueError):
            tls.https_ingress_probe('pod-a', ingress='ingress.svc.cluster.local:443',
                                    certificate_b64='YQ==', path='/api/private')

    def test_https_probe_argument_placement(self):
        calls = []
        original = tls.node_script
        def stub(*args): calls.append(args)
        try:
            tls.node_script = stub
            tls.https_ingress_probe('pod-1', ingress='service:443', certificate_b64='YQ==', bad_host=True)
            tls.https_ingress_probe('pod-2', ingress='service:443', certificate_b64='YQ==', untrusted=True)
        finally:
            tls.node_script = original
        self.assertEqual(calls[0][2:],('https://service:443/api/health/ready','unknown.example.invalid','404','YQ==','trusted',tls.HOST))
        self.assertEqual(calls[1][2:],('https://service:443/api/health/ready',tls.HOST,'200','YQ==','untrusted',tls.HOST))

    def test_legacy_http_mode_untouched(self):
        code = (ROOT/'tools/ci_k8s_multinode_ingress_smoke.py').read_text()
        self.assertIn("if https:\n                    https_ingress_probe", code)
        self.assertIn("ingress_probe(first, ingress=ingress)", code)
        self.assertIn("if https:\n                    https_ingress_probe(first, path='/api/health/live'", code)

    def test_workflow_separate_opt_in_and_two_controllers(self):
        import yaml
        wf = yaml.safe_load((ROOT/'.github/workflows/ci.yml').read_text())
        workflow_inputs = wf.get('on', wf.get(True))['workflow_dispatch']['inputs']
        self.assertFalse(workflow_inputs['kubernetes_tls_test']['default'])
        job=wf['jobs']['kubernetes-https-ingress']
        self.assertIn('inputs.kubernetes_tls_test',job['if'])
        self.assertEqual(job['strategy']['matrix']['controller'],['nginx','haproxytech'])
        self.assertIn('--tls',str(job['steps']))
        self.assertFalse(any('push' in str(step).lower() for step in job['steps']))

    @unittest.skipUnless(shutil.which('node') and shutil.which('openssl'), 'Node and OpenSSL required')
    def test_real_node_tls_trusted_host_bad_host_and_untrusted(self):
        with tempfile.TemporaryDirectory() as td:
            work=Path(td)
            cert,key=work/'tls.crt',work/'tls.key'
            subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-sha256',
                            '-nodes','-days','1','-subj',f'/CN={tls.HOST}',
                            '-addext',f'subjectAltName=DNS:{tls.HOST}',
                            '-keyout',str(key),'-out',str(cert)],
                           capture_output=True,check=True,timeout=20)
            pinned=base64.b64encode(cert.read_bytes()).decode('ascii')
            server=http.server.HTTPServer(('127.0.0.1',0),Handler)
            ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(str(cert),str(key))
            server.socket=ctx.wrap_socket(server.socket,server_side=True)
            thread=threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                address=f'https://127.0.0.1:{server.server_port}/api/health/ready'
                def probe(host:str, expected:int, ca:str, mode:str='trusted',servername:str=tls.HOST):
                    return subprocess.run(['node','-e',tls.https_probe_source(), address,
                                           host,str(expected),ca,mode,servername],
                                          capture_output=True,text=True,timeout=12)
                self.assertEqual(probe(tls.HOST,200,pinned).returncode,0, 'Pinned CA HTTPS must be accepted')
                self.assertEqual(probe('unknown.example.invalid',404,pinned).returncode,0,'Bad HTTP host rejected under valid TLS')
                self.assertEqual(probe(tls.HOST,200,pinned,'untrusted').returncode,0,'Untrusted cert must be rejected')
                self.assertNotEqual(probe(tls.HOST,200,pinned,servername='unknown.example.invalid').returncode,0,
                                    'Wrong SNI identity must fail')
                self.assertNotEqual(probe(tls.HOST,200,base64.b64encode(b'not a cert').decode()).returncode,0,
                                    'Invalid trust store must fail')
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


if __name__ == '__main__':unittest.main()
