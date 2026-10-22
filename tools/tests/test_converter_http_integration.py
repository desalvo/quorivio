"""Real private HTTP boundary tests for the isolated conversion worker."""
import http.client
import json
import pathlib
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import conversion_worker as worker


class HTTPWorkerIntegration(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.token = 'test-private-worker-token-with-at-least-32-characters'
        self.root_patch = patch.object(worker, 'ROOT', self.root)
        self.token_patch = patch.object(worker, 'TOKEN', self.token)
        self.root_patch.start()
        self.token_patch.start()
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), worker.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)
        self.token_patch.stop()
        self.root_patch.stop()
        self.temp.cleanup()

    def request(self, method, endpoint, content=b'', token=None):
        c = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        headers = {'Content-Type': 'application/json'}
        if token is not None:
            headers['Authorization'] = 'Bearer ' + token
        c.request(method, endpoint, content, headers)
        response = c.getresponse()
        status, payload = response.status, json.loads(response.read())
        c.close()
        return status, payload

    def test_health(self):
        status, body = self.request('GET', '/health')
        self.assertEqual(status, 200)
        self.assertTrue(body['ready'])
        with patch.object(worker, 'TOKEN', ''):
            status, body = self.request('GET', '/health')
            self.assertEqual(status, 503)
            self.assertFalse(body['ready'])

    def test_authentication_and_input_validation(self):
        payload = json.dumps({'job': 'a'*32}).encode()
        self.assertEqual(self.request('POST', '/convert', payload)[0], 403)
        self.assertEqual(self.request('POST', '/convert', payload, 'wrong')[0], 403)
        self.assertEqual(self.request('POST', '/convert', b'{}', self.token)[0], 400)
        self.assertEqual(self.request('POST', '/convert', b'x'*257, self.token)[0], 413)
        self.assertEqual(self.request('POST', '/convert', b'{no json', self.token)[0], 422)
        self.assertEqual(self.request('GET', '/not-supported')[0], 404)

    def test_conversion_through_private_http(self):
        job = 'b'*32
        workspace = self.root / job
        workspace.mkdir()
        (workspace / 'source.pdf').write_bytes(b'%PDF-1.4 test fixture')
        def mock_convert(source, destination):
            self.assertEqual(source, workspace / 'source.pdf')
            self.assertEqual(destination, workspace / 'pages')
            self.assertTrue((workspace / '.conversion-lock').is_dir())
            return {'page_count': 2}
        with patch.object(worker, 'convert', side_effect=mock_convert):
            status, payload = self.request('POST', '/convert', json.dumps({'job': job}).encode(), self.token)
        self.assertEqual(status, 200)
        self.assertEqual(payload, {'page_count': 2})
        self.assertFalse((workspace / '.conversion-lock').exists())


if __name__ == '__main__':
    unittest.main()
