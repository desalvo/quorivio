"""CI extended run 41044420650: ingress virtual host and ClamAV readiness contracts."""
from __future__ import annotations
import http.server
import subprocess
import threading
import unittest
from pathlib import Path
import sys
import yaml

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from ci_k8s_multinode_ingress_smoke import ingress_http_source

class ProbeHandler(http.server.BaseHTTPRequestHandler):
    captured_host=''
    def do_GET(self):
        type(self).captured_host=self.headers.get('Host','')
        self.send_response(200 if self.headers.get('Host')=='quorivio-multi.example.invalid' else 404)
        self.end_headers()
        self.wfile.write(b'ok')
    def log_message(self,*args):pass

class Cycle33ExtendedCI(unittest.TestCase):
    def test_vhost_probe_reaches_actual_host_based_route(self):
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),ProbeHandler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            endpoint=f'http://127.0.0.1:{server.server_port}/api/health/ready'
            result=subprocess.run(['node','-e',ingress_http_source(),endpoint,'quorivio-multi.example.invalid','200'],capture_output=True,timeout=10)
            self.assertEqual(result.returncode,0)
            self.assertEqual(ProbeHandler.captured_host,'quorivio-multi.example.invalid')
            result=subprocess.run(['node','-e',ingress_http_source(),endpoint,'wrong.example.invalid','404'],capture_output=True,timeout=10)
            self.assertEqual(result.returncode,0)
        finally:server.shutdown();thread.join(timeout=5);server.server_close()

    def test_clamav_waits_for_ping_pong_and_does_not_skip_signature(self):
        workflow=yaml.safe_load((ROOT/'.github/workflows/ci.yml').read_text())
        job=workflow['jobs']['clamav-runtime']
        steps=job['steps']
        checks=[s for s in steps if s.get('name')]
        wait=next(i for i,s in enumerate(checks) if 'PING/PONG' in s['name'])
        verify=next(i for i,s in enumerate(checks) if 'EICAR detection' in s['name'])
        self.assertLess(wait,verify)
        self.assertIn('--wait-ready',checks[wait]['run'])
        source=(ROOT/'tools/ci_clamav_real.mjs').read_text()
        self.assertIn("received.slice(0,terminator)==='PONG'",source)
        self.assertIn('eicar_not_detected',source)
        self.assertIn('clean_scan_',source)
        self.assertNotIn('console.error(error)',source)

    def test_multinode_job_uses_node_http_not_fetch_host(self):
        code=ingress_http_source()
        self.assertIn('http.request',code)
        self.assertIn('headers:{Host:process.argv[2]}',code)
        self.assertNotIn('fetch(',code)
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('kubectl get ingressclass',workflow)

if __name__=='__main__':unittest.main()
