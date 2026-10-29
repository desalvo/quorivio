#!/usr/bin/env python3
"""Disposable PostgreSQL + real SMTPS password-recovery security acceptance.

Only a loopback API, an ephemeral CI admin and a mode-0600 SMTP capture are accepted.
Never print credentials, reset tokens, email bodies or authentication cookies.
"""
from __future__ import annotations

import hashlib
import http.cookiejar
import json
import os
import re
import subprocess
import time
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from email import policy
from email.parser import Parser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit, parse_qs
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE = os.environ.get('QUORIVIO_CI_BASE_URL', 'http://127.0.0.1:8080')
CAPTURE = Path(os.environ.get('QUORIVIO_CI_SMTP_CAPTURE', '/tmp/quorivio-ci-mail.jsonl'))


def assert_disposable():
    u = urlsplit(BASE)
    assert u.scheme == 'http' and u.hostname in ('localhost', '127.0.0.1') and u.port, 'requires loopback API'
    assert os.getenv('QUORIVIO_CI_RECOVERY_TEST') == '1', 'requires explicit opt-in'
    assert os.getenv('GITHUB_RUN_ID', '').isdigit(), 'requires disposable CI run id'
    database = urlsplit(os.getenv('DATABASE_URL', ''))
    assert database.scheme in ('postgres', 'postgresql') and database.hostname in ('127.0.0.1', 'localhost') and database.path == '/quorivio', 'requires disposable loopback PostgreSQL'
    assert os.getenv('QUORIVIO_CI_NEW_PASSWORD') and os.getenv('QUORIVIO_CI_ADMIN_EMAIL')
    assert CAPTURE.is_file() and not CAPTURE.is_symlink(), 'requires private SMTPS sink'
    assert (CAPTURE.stat().st_mode & 0o077) == 0, 'SMTP capture must be 0600'
    assert len(os.getenv('QUORIVIO_CI_LOAD_TOKEN', '')) >= 32, 'requires nonproduction test token'


def client():
    return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))


def call(opener, method, path, payload=None, expected=200):
    headers = {'Content-Type': 'application/json', 'X-Quorivio-Load-Token': os.environ['QUORIVIO_CI_LOAD_TOKEN']}
    req = Request(BASE + path, data=json.dumps(payload).encode() if payload is not None else None,
                  method=method, headers=headers)
    try:
        with opener.open(req, timeout=15) as response:
            status, data = response.status, response.read()
    except HTTPError as exc:
        status, data = exc.code, exc.read()
    assert status == expected, f'{method} {path}: HTTP {status} (expected {expected})'
    return json.loads(data) if data else None


def mail_count():
    return len([x for x in CAPTURE.read_text(encoding='utf-8').splitlines() if x.strip()])


def extract_recovery_token(content: str) -> str:
    """Validate the actual SMTP link without disclosing a bearer in test output.

    A fragment never reaches the HTTP request path, access logs or Referer.
    Legacy query links can still be consumed by the web client, but newly
    issued links must use the private fragment-only representation.
    """
    match = re.search(r'https?://[^\s<>]+', content)
    assert match, 'SMTPS message lacks a valid recovery URL'
    link = urlsplit(match.group(0))
    assert link.scheme == 'https' or (link.scheme == 'http' and link.hostname in ('127.0.0.1', 'localhost')), 'recovery email must use HTTPS (HTTP only for loopback CI)'
    assert link.path == '/' and not link.query, 'recovery URL leaked bearer into request URL'
    params = parse_qs(link.fragment, strict_parsing=True)
    tokens = params.get('reset_token', [])
    assert len(tokens) == 1 and re.fullmatch(r'[A-Za-z0-9_-]{43}', tokens[0]), 'invalid recovery bearer in fragment'
    assert len(params) == 1, 'unexpected recovery URL fragment fields'
    return tokens[0]


def receive_link(offset, recipient):
    for _ in range(50):
        rows = [json.loads(x) for x in CAPTURE.read_text(encoding='utf-8').splitlines() if x.strip()]
        if len(rows) > offset:
            assert len(rows) == offset + 1, 'unexpected duplicate reset mail'
            assert recipient in rows[-1]['recipient'], 'recovery mail delivered to another account'
            msg = Parser(policy=policy.default).parsestr(rows[-1]['message'])
            plain = msg.get_body(preferencelist=('plain',))
            content = plain.get_content() if plain else msg.get_content()
            token = extract_recovery_token(content)
            assert '20 minutes' in content, 'incorrect token expiry in SMTP message'
            return token
        time.sleep(0.15)
    raise AssertionError('password recovery SMTP delivery did not arrive')


def db_scalar(sql):
    proc = subprocess.run(['psql', os.environ['DATABASE_URL'], '-X', '-q', '-t', '-A', '-c', sql],
                          text=True, capture_output=True, timeout=15, check=False)
    assert proc.returncode == 0, 'disposable PostgreSQL query failed'
    return proc.stdout.strip()


def add_account(admin, suffix):
    email = f'ci-reset-{os.environ["GITHUB_RUN_ID"]}-{suffix}@example.invalid'
    initial = 'ci-reset-initial-long-password-123'
    active = 'ci-reset-active-long-password-123'
    created = call(admin, 'POST', '/api/admin/users',
                   {'email': email, 'temporary_password': initial, 'role': 'user'}, 201)
    assert created['id']
    user = client()
    call(user, 'POST', '/api/auth/login', {'email': email, 'password': initial})
    call(user, 'POST', '/api/auth/change-password', {'current_password': initial, 'new_password': active})
    call(user, 'POST', '/api/auth/login', {'email': email, 'password': active})
    assert call(user, 'GET', '/api/auth/me')['email'] == email
    return email, active, user


def run():
    assert_disposable()
    admin = client()
    call(admin, 'POST', '/api/auth/login',
         {'email': os.environ['QUORIVIO_CI_ADMIN_EMAIL'], 'password': os.environ['QUORIVIO_CI_NEW_PASSWORD']})
    email, old_password, first_session = add_account(admin, 'replay')
    second_session = client()
    call(second_session, 'POST', '/api/auth/login', {'email': email, 'password': old_password})
    assert call(second_session, 'GET', '/api/auth/me')['email'] == email
    # Simulate an already-created login MFA challenge and enrollment. Neither
    # may survive a reset even if the bearer token is otherwise valid.
    for table in ('email_mfa_challenges', 'email_mfa_enrollments'):
        challenge_id = str(uuid4())
        result = db_scalar(f"INSERT INTO {table}(id,user_id,digest,expires_at) "
                           f"SELECT '{challenge_id}',id,repeat('a',64),now()+interval '5 minutes' "
                           f"FROM users WHERE email='{email}' RETURNING id")
        assert challenge_id in result, 'failed to create disposable stale MFA fixture'

    before = mail_count()
    unknown = f'ci-reset-{os.environ["GITHUB_RUN_ID"]}-unknown@example.invalid'
    assert call(client(), 'POST', '/api/auth/password-reset/request', {'email': unknown}, 202) == {'accepted': True}
    assert mail_count() == before, 'unknown account must not be sent a recovery mail'
    assert call(client(), 'POST', '/api/auth/password-reset/request', {'email': email}, 202) == {'accepted': True}
    token = receive_link(before, email)
    digest = hashlib.sha256(token.encode()).hexdigest()
    # SQL uses digest only; never interpolate a bearer token into SQL or logs.
    assert db_scalar(f"SELECT count(*) FROM password_reset_tokens WHERE token_hash='{digest}' AND used_at IS NULL AND expires_at>now()") == '1'
    assert call(client(), 'POST', '/api/auth/password-reset/request', {'email': email}, 202) == {'accepted': True}
    assert mail_count() == before + 1, 'rate-limited duplicate request must not deliver another token'
    call(client(), 'POST', '/api/auth/password-reset/confirm', {'token': token, 'new_password': 'weak'}, 400)
    replacement = 'ci-reset-replacement-long-password-123'
    with ThreadPoolExecutor(max_workers=2) as pool:
        result = list(pool.map(lambda _: confirm_status(token, replacement), range(2)))
    assert sorted(result) == [200, 400], 'a recovery token must be consumed exactly once'
    assert db_scalar(f"SELECT count(*) FROM password_reset_tokens WHERE token_hash='{digest}' AND used_at IS NOT NULL") == '1'
    for table in ('email_mfa_challenges', 'email_mfa_enrollments'):
        assert db_scalar(f"SELECT count(*) FROM {table} WHERE user_id=(SELECT id FROM users WHERE email='{email}')") == '0', 'credential rotation left an active MFA challenge'
    call(first_session, 'GET', '/api/auth/me', expected=401)
    call(second_session, 'GET', '/api/auth/me', expected=401)
    call(client(), 'POST', '/api/auth/login', {'email': email, 'password': old_password}, 401)
    restored = client()
    call(restored, 'POST', '/api/auth/login', {'email': email, 'password': replacement})
    assert call(restored, 'GET', '/api/auth/me')['email'] == email

    # Independent account avoids the per-email 60-second issuance limit.
    exp_email, _, _ = add_account(admin, 'expired')
    offset = mail_count()
    call(client(), 'POST', '/api/auth/password-reset/request', {'email': exp_email}, 202)
    expired = receive_link(offset, exp_email)
    expired_digest = hashlib.sha256(expired.encode()).hexdigest()
    assert db_scalar(f"UPDATE password_reset_tokens SET expires_at=now()-interval '1 second' WHERE token_hash='{expired_digest}' RETURNING id")
    call(client(), 'POST', '/api/auth/password-reset/confirm',
         {'token': expired, 'new_password': replacement}, 400)
    assert call(client(), 'POST', '/api/auth/password-reset/confirm',
                {'token': 'x' * 43, 'new_password': replacement}, 400)['error'] == 'invalid_or_expired_token'
    print('PASS PostgreSQL/TLS SMTP password recovery: private delivery, anti-enumeration, rate limit, digest-only storage, atomic single use, expiry, password rotation and multi-session revocation and MFA challenge invalidation')


def confirm_status(token, replacement):
    return_code = None
    try:
        call(client(), 'POST', '/api/auth/password-reset/confirm',
             {'token': token, 'new_password': replacement}, 200)
        return_code = 200
    except AssertionError as exc:
        if 'HTTP 400 (expected 200)' not in str(exc):
            raise
        return_code = 400
    return return_code


if __name__ == '__main__':
    run()
