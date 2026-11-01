"""MFA CI requests use an opt-in loopback-only load token, not a production bypass."""
from __future__ import annotations

import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('quorivio_ci_mfa', ROOT / 'tools/ci_email_mfa_postgres.py')
assert SPEC and SPEC.loader
mfa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mfa)

TOKEN = 'ci-disposable-token-never-used-in-production-123456'

class FakeResponse:
    status = 200
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def read(self): return b'{"ok":true}'

class CapturingOpener:
    def __init__(self, reject=False):
        self.requests=[]
        self.reject=reject
    def open(self, request, timeout):
        self.requests.append(request)
        if self.reject:
            raise HTTPError(request.full_url, 401, 'unauthorized', {}, io.BytesIO(b'{"error":"invalid_code"}'))
        return FakeResponse()

class MfaThrottleIsolationTests(unittest.TestCase):
    def test_all_mfa_http_helpers_attach_ephemeral_token_without_leaking_body(self):
        with patch.dict(os.environ, {'QUORIVIO_CI_LOAD_TOKEN': TOKEN}):
            opener=CapturingOpener()
            self.assertTrue(mfa.request(opener, 'GET', '/api/auth/me')['ok'])
            self.assertEqual(mfa.request_status(opener, 'POST', '/api/auth/email-mfa/verify', {'code':'123456'}), 200)
        self.assertEqual(len(opener.requests),2)
        for req in opener.requests:
            self.assertEqual(req.get_header('X-quorivio-load-token'), TOKEN)
            self.assertTrue(req.full_url.startswith('http://127.0.0.1:8080/'))

    def test_negative_otp_responses_still_asserted(self):
        with patch.dict(os.environ, {'QUORIVIO_CI_LOAD_TOKEN': TOKEN}):
            opener=CapturingOpener(reject=True)
            self.assertEqual(mfa.request(opener, 'POST', '/api/auth/email-mfa/verify', {'code':'000000'},401)['error'],'invalid_code')
            self.assertEqual(mfa.request_status(opener,'POST','/api/auth/email-mfa/verify',{'code':'000000'}),401)

    def test_disposable_guard_rejects_missing_or_short_token(self):
        with tempfile.TemporaryDirectory(prefix='ci-mfa-guard-') as tmp:
            capture=Path(tmp)/'mail.jsonl'
            capture.write_text('')
            capture.chmod(0o600)
            with patch.object(mfa,'CAPTURE',capture),patch.object(mfa,'BASE','http://127.0.0.1:8080'):
                for token in ('','short'):
                    with self.subTest(token=token),patch.dict(os.environ,{'QUORIVIO_CI_MFA_TEST':'1','QUORIVIO_CI_LOAD_TOKEN':token}):
                        with self.assertRaisesRegex(RuntimeError,'ephemeral non-production load token'):
                            mfa.assert_disposable()
                with patch.dict(os.environ,{'QUORIVIO_CI_MFA_TEST':'1','QUORIVIO_CI_LOAD_TOKEN':TOKEN}):
                    mfa.assert_disposable()

    def test_disposable_guard_rejects_remote_url_even_with_valid_token(self):
        with tempfile.TemporaryDirectory(prefix='ci-mfa-guard-') as tmp:
            capture=Path(tmp)/'mail.jsonl'
            capture.write_text('')
            capture.chmod(0o600)
            with patch.object(mfa,'CAPTURE',capture),patch.object(mfa,'BASE','https://example.org:443'):
                with patch.dict(os.environ,{'QUORIVIO_CI_MFA_TEST':'1','QUORIVIO_CI_LOAD_TOKEN':TOKEN}):
                    with self.assertRaisesRegex(RuntimeError,'explicit local HTTP API'):
                        mfa.assert_disposable()

    def test_ci_guarantees_persisted_rate_limiter_and_production_fail_closed(self):
        code=(ROOT/'apps/api/src/server.ts').read_text()
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn("process.env.NODE_ENV!=='production'",code)
        self.assertIn('timingSafeEqual(a,b)',code)
        self.assertIn("if(Number(r.rows[0].hits)>100)",code)
        self.assertIn('::add-mask::$load_token',workflow)
        self.assertIn('::add-mask::$smtp_password',workflow)
        self.assertIn('QUORIVIO_CI_SMTP_PASSWORD="$QUORIVIO_CI_SMTP_PASSWORD"',workflow)
        step=workflow.split('      - name: PostgreSQL and real TLS SMTP email MFA lifecycle acceptance',1)[1].split('      - name:',1)[0]
        self.assertIn('QUORIVIO_CI_LOAD_TOKEN: ${{ env.QUORIVIO_CI_LOAD_TOKEN }}',step)
        self.assertIn('python3 tools/ci_email_mfa_postgres.py',step)

if __name__=='__main__':unittest.main()
