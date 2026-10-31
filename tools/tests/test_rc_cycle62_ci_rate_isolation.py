"""RC62: real CI 41186895267 regression, PostgreSQL limiter across HTTP suites."""
from __future__ import annotations

import importlib.util
import io
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from ci_http_isolation import ci_load_headers

TOKEN = 'ephemeral-CI-acceptance-secret-strong-and-unique-123456789'


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools' / (name + '.py'))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self): return b'{"ok":true}'


class FakeOpener:
    def __init__(self, status=200):
        self.requests = []
        self.status = status

    def open(self, request, timeout):
        self.requests.append(request)
        if self.status != 200:
            raise HTTPError(request.full_url, self.status, 'rate_limited', {}, io.BytesIO(b'{"error":"rate_limited"}'))
        return FakeResponse()


class Cycle62CiRateIsolation(unittest.TestCase):
    def test_disposable_token_must_exist_and_never_target_external_host(self):
        with patch.dict(os.environ, {'QUORIVIO_CI_LOAD_TOKEN': TOKEN}):
            for url in ('https://127.0.0.1:8080', 'http://example.com:8080',
                        'http://localhost.evil.invalid:8080',
                        'http://127.0.0.1:8080@evil.invalid',
                        'http://127.0.0.1:8080/attacker',
                        'http://localhost:8080?token=1',
                        'http://127.0.0.1:8080#fragment'):
                with self.subTest(url=url), self.assertRaises(RuntimeError):
                    ci_load_headers(url)
            self.assertEqual(ci_load_headers('http://127.0.0.1:8080')['X-Quorivio-Load-Token'], TOKEN)
            self.assertEqual(ci_load_headers('http://localhost:8080')['X-Quorivio-Load-Token'], TOKEN)
        for token in ('', 'too-short', 'valid-but-newline-' + 'x'*35 + '\n', 'x'*257):
            with self.subTest(length=len(token)), patch.dict(os.environ, {'QUORIVIO_CI_LOAD_TOKEN': token}):
                with self.assertRaises(RuntimeError):
                    ci_load_headers('http://127.0.0.1:8080')

    def test_both_postgres_http_suites_attach_opt_in_token_on_all_methods(self):
        with patch.dict(os.environ, {
            'QUORIVIO_CI_LOAD_TOKEN': TOKEN,
            'QUORIVIO_CI_ADMIN_EMAIL': 'ci-admin@example.invalid',
            'QUORIVIO_CI_ADMIN_PASSWORD': 'ci-initial-password',
            'QUORIVIO_CI_NEW_PASSWORD': 'ci-rotated-password',
        }):
            bg = load('ci_background_library_postgres')
            portable = load('ci_portable_http')
            for target in (bg, portable):
                opener = FakeOpener()
                for method in ('GET', 'POST', 'PATCH', 'DELETE'):
                    if target is bg:
                        target.req(opener, method, '/api/auth/me', {'ok': True} if method != 'GET' else None)
                    else:
                        target.api(method, '/api/auth/me', {'ok': True} if method != 'GET' else None, opener=opener)
                self.assertEqual(len(opener.requests), 4)
                for request in opener.requests:
                    self.assertEqual(request.get_header('X-quorivio-load-token'), TOKEN)
                    self.assertTrue(request.full_url.startswith('http://127.0.0.1:8080/'))

    def test_without_token_requests_fail_closed_before_network_access(self):
        with patch.dict(os.environ, {
            'QUORIVIO_CI_LOAD_TOKEN': '',
            'QUORIVIO_CI_ADMIN_EMAIL': 'ci-admin@example.invalid',
            'QUORIVIO_CI_ADMIN_PASSWORD': 'ci-initial-password',
            'QUORIVIO_CI_NEW_PASSWORD': 'ci-rotated-password',
        }):
            for target in (load('ci_background_library_postgres'), load('ci_portable_http')):
                opener = FakeOpener(status=429)
                with self.assertRaises(RuntimeError):
                    if target.__name__ == 'ci_background_library_postgres':
                        target.req(opener, 'GET', '/api/auth/me')
                    else:
                        target.api('GET', '/api/auth/me', opener=opener)
                self.assertEqual(opener.requests, [])

    def test_ci_propagates_same_ephemeral_token_and_keeps_production_limiter(self):
        flow = (ROOT / '.github/workflows/ci.yml').read_text()
        api = (ROOT / 'apps/api/src/server.ts').read_text()
        for step in ('PostgreSQL-backed portable and profile lifecycle E2E',
                     'PostgreSQL-backed private presenter background library and collaborator copy-on-use'):
            section = flow.split('      - name: ' + step + '\n', 1)[1].split('      - name:', 1)[0]
            self.assertIn('QUORIVIO_CI_LOAD_TOKEN: ${{ env.QUORIVIO_CI_LOAD_TOKEN }}', section)
        self.assertIn('LOAD_TEST_TOKEN: ${{ env.QUORIVIO_CI_LOAD_TOKEN }}', flow)
        self.assertIn("process.env.NODE_ENV!=='production'", api)
        self.assertIn('if(Number(r.rows[0].hits)>100)', api)
        self.assertIn('timingSafeEqual(a,b)', api)


if __name__ == '__main__':
    unittest.main()
