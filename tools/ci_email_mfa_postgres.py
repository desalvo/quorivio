#!/usr/bin/env python3
"""Real PostgreSQL, real SMTPS (disposable TLS sink), and HTTP email MFA acceptance.

Only against a locally started, throwaway CI database/API. No codes, cookies,
passwords or capture contents are emitted in logs. Uses a fresh dedicated user.
"""
from __future__ import annotations
import http.cookiejar
from concurrent.futures import ThreadPoolExecutor
import json
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPCookieProcessor, build_opener

BASE = os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
CAPTURE = Path(os.environ.get('QUORIVIO_CI_SMTP_CAPTURE','/tmp/quorivio-ci-mail.jsonl'))


def assert_disposable() -> None:
    url = urlsplit(BASE)
    if url.scheme != 'http' or url.hostname not in ('127.0.0.1','localhost') or not url.port:
        raise RuntimeError('MFA CI requires an explicit local HTTP API')
    if os.environ.get('QUORIVIO_CI_MFA_TEST') != '1':
        raise RuntimeError('MFA CI requires QUORIVIO_CI_MFA_TEST=1')
    if not CAPTURE.is_file() or CAPTURE.is_symlink() or os.stat(CAPTURE).st_mode & 0o077:
        raise RuntimeError('MFA CI requires a private disposable SMTPS capture file')


def client():
    return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))


def request(opener,method,path,data=None,expected=200):
    raw=json.dumps(data).encode() if data is not None else None
    req=Request(BASE+path,data=raw,method=method,headers={'Content-Type':'application/json'})
    try:
        with opener.open(req,timeout=10) as r:status,body=r.status,r.read()
    except HTTPError as e:status,body=e.code,e.read()
    assert status==expected, f'HTTP {method} {path}: expected {expected}, got {status}'
    return json.loads(body) if body else None


def request_status(opener, method, path, data):
    raw=json.dumps(data).encode()
    req=Request(BASE+path,data=raw,method=method,headers={'Content-Type':'application/json'})
    try:
        with opener.open(req,timeout=10) as r:return r.status
    except HTTPError as e:return e.code


def messages():
    return [json.loads(line) for line in CAPTURE.read_text(encoding='utf-8').splitlines() if line.strip()]


def receive_code(offset,ttl):
    for _ in range(40):
        rows=messages()
        if len(rows)>offset:
            assert len(rows)==offset+1, 'unexpected duplicate SMTP delivery'
            msg=rows[-1]['message']
            # Encodings may be quoted-printable; extract the 6-digit code only.
            match=re.search(r'verification code is (\d{6})',msg)
            assert match and f'expires in {ttl} minutes' in msg, 'SMTP delivery/TTL invalid'
            assert 'ci-email-mfa-' in rows[-1]['recipient'], 'email sent to unexpected recipient'
            return match.group(1)
        time.sleep(0.15)
    raise AssertionError('SMTPS message did not arrive')


def expire_challenge(challenge):
    assert re.fullmatch(r'[0-9a-f-]{36}',challenge)
    env=os.environ.copy()
    sql=f"UPDATE email_mfa_challenges SET expires_at=now()-interval '1 second' WHERE id='{challenge}'"
    proc=subprocess.run(['psql',env['DATABASE_URL'],'-X','-q','-c',sql],env=env,capture_output=True,text=True,timeout=10)
    assert proc.returncode==0, 'PostgreSQL expiry fixture failed'


def run():
    assert_disposable()
    admin=client()
    request(admin,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
    email='ci-email-mfa-'+os.environ['GITHUB_RUN_ID']+'@example.invalid'
    temp='ci-disposable-password-initial-123'
    new='ci-disposable-password-rotated-123'
    user=request(admin,'POST','/api/admin/users',{'email':email,'temporary_password':temp,'role':'user'},201)
    assert user['id']
    account=client()
    request(account,'POST','/api/auth/login',{'email':email,'password':temp})
    request(account,'POST','/api/auth/change-password',{'current_password':temp,'new_password':new})
    request(account,'POST','/api/auth/login',{'email':email,'password':new})
    initial=len(messages())
    pending=request(account,'POST','/api/auth/email-mfa/settings',{'enabled':True,'password':new})
    assert pending['pending_confirmation'] and pending['challenge_id']
    code=receive_code(initial,10)
    request(account,'POST','/api/auth/email-mfa/enrollment/confirm',{'challenge_id':pending['challenge_id'],'code':'999999' if code!='999999' else '888888'},401)
    assert request(account,'POST','/api/auth/email-mfa/enrollment/confirm',{'challenge_id':pending['challenge_id'],'code':code})['reauthentication_required']
    request(account,'GET','/api/auth/me',expected=401)
    request(account,'POST','/api/auth/email-mfa/enrollment/confirm',{'challenge_id':pending['challenge_id'],'code':code},401)
    mfa=request(account,'POST','/api/auth/login',{'email':email,'password':new})
    assert mfa['mfa_required'] and mfa['methods']==['email']
    request(account,'POST','/api/auth/email-mfa/verify',{'challenge_id':mfa['challenge_id'],'code':'000000'},401)
    email_count=len(messages())
    assert request(account,'POST','/api/auth/mfa/challenge/email',{'challenge_id':mfa['challenge_id']})['ok']
    otp=receive_code(email_count,5)
    request(account,'POST','/api/auth/email-mfa/verify',{'challenge_id':mfa['challenge_id'],'code':'999999' if otp!='999999' else '888888'},401)
    assert request(account,'POST','/api/auth/email-mfa/verify',{'challenge_id':mfa['challenge_id'],'code':otp})['email']==email
    assert request(account,'GET','/api/auth/me')['email']==email
    request(account,'POST','/api/auth/email-mfa/verify',{'challenge_id':mfa['challenge_id'],'code':otp},401)
    # Two replicas verifying the same OTP concurrently: exactly one creates a
    # logged-in session; row locking prevents a successful replay.
    concurrent=request(client(),'POST','/api/auth/login',{'email':email,'password':new})
    offset=len(messages())
    request(client(),'POST','/api/auth/mfa/challenge/email',{'challenge_id':concurrent['challenge_id']})
    parallel_otp=receive_code(offset,5)
    with ThreadPoolExecutor(max_workers=2) as executor:
        results=list(executor.map(lambda _:request_status(client(),'POST','/api/auth/email-mfa/verify',
                           {'challenge_id':concurrent['challenge_id'],'code':parallel_otp}),range(2)))
    assert sorted(results)==[200,401],f'concurrent OTP must be single use: {sorted(results)}'
    # Five guesses lock the pending challenge even when the final guess is valid.
    brute=request(client(),'POST','/api/auth/login',{'email':email,'password':new})
    offset=len(messages())
    request(client(),'POST','/api/auth/mfa/challenge/email',{'challenge_id':brute['challenge_id']})
    locked_otp=receive_code(offset,5)
    wrong='999999' if locked_otp!='999999' else '888888'
    for _ in range(5):
        request(client(),'POST','/api/auth/email-mfa/verify',{'challenge_id':brute['challenge_id'],'code':wrong},401)
    request(client(),'POST','/api/auth/email-mfa/verify',{'challenge_id':brute['challenge_id'],'code':locked_otp},401)
    # Account-level message throttling is separately tested under the SQL
    # concurrency contract; avoid CI flakes at an exact UTC minute boundary.
    # Password authentication cannot bypass email MFA, and an expired challenge
    # is never accepted even with a matching valid-looking OTP.
    other=client()
    future=request(other,'POST','/api/auth/login',{'email':email,'password':new})
    assert future['mfa_required']
    expire_challenge(future['challenge_id'])
    request(other,'POST','/api/auth/email-mfa/verify',{'challenge_id':future['challenge_id'],'code':otp},401)
    request(account,'POST','/api/auth/email-mfa/settings',{'enabled':False,'password':new})
    request(account,'GET','/api/auth/me',expected=401)
    again=request(account,'POST','/api/auth/login',{'email':email,'password':new})
    assert not again.get('mfa_required') and request(account,'GET','/api/auth/me')['email']==email
    # Existing revoked challenge cannot be reused after disabling the feature.
    request(other,'POST','/api/auth/mfa/challenge/email',{'challenge_id':future['challenge_id']},401)
    print('PASS PostgreSQL/TLS SMTP MFA: 10m inbox enrollment, invalid codes, revocation, 5m OTP, concurrent single-use, five-guess lockout, expiry, disable and bypass protection')

if __name__=='__main__':run()
