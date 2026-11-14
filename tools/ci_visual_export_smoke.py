#!/usr/bin/env python3
"""Opt-in, no-persistence smoke of the four visual Quorivio exports.

Use a disposable, non-MFA presenter on a staging instance with its converter
running. Read all credentials from environment variables; never log file data.
"""
from __future__ import annotations

import http.cookiejar
import io
import json
import os
import re
import ssl
import sys
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import HTTPCookieProcessor, HTTPRedirectHandler, Request, build_opener
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

MAX_BYTES = 50 * 1024 * 1024
PPTX_MIME = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
P_NS = '{http://schemas.openxmlformats.org/presentationml/2006/main}'


class SmokeFailure(Exception):
    pass


class RefuseRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def validated_base(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('', '/'):
        raise SmokeFailure('The staging URL must be a bare origin without credentials, path or query')
    if not parsed.netloc or parsed.scheme not in ('http', 'https'):
        raise SmokeFailure('Invalid staging origin')
    if parsed.scheme == 'http' and parsed.hostname not in ('localhost', '127.0.0.1', '::1'):
        raise SmokeFailure('Plain HTTP is permitted only for loopback staging')
    return parsed.geturl().rstrip('/')


def verify_pdf(payload: bytes) -> None:
    if not payload.startswith(b'%PDF-') or b'%%EOF' not in payload[-2048:]:
        raise SmokeFailure('Invalid PDF signature or missing trailer')


def verify_visual_pptx(payload: bytes) -> int:
    try:
        with ZipFile(io.BytesIO(payload)) as z:
            names = z.namelist()
            slides = sorted(n for n in names if re.fullmatch(r'ppt/slides/slide[1-9]\d*\.xml', n))
            if not slides or 'ppt/presentation.xml' not in names or '[Content_Types].xml' not in names:
                raise SmokeFailure('PPTX has no complete presentation or slides')
            if not any(n.startswith('ppt/media/') and n.lower().endswith('.png') for n in names):
                raise SmokeFailure('PPTX is missing visual slide captures')
            for name in slides:
                entry = z.getinfo(name)
                if entry.file_size > 2 * 1024 * 1024:
                    raise SmokeFailure('Oversized PPTX slide XML')
                if not ET.fromstring(z.read(name)).findall('.//' + P_NS + 'pic'):
                    raise SmokeFailure('PPTX contains a slide without visual capture')
            return len(slides)
    except (BadZipFile, ET.ParseError, ValueError) as exc:
        raise SmokeFailure('Invalid PPTX/OOXML document') from exc


def check_filename(header: str | None, view: str, fmt: str) -> None:
    match = re.search(r"filename\*=UTF-8''([^;\s]+)", header or '', flags=re.I)
    if not (header or '').lower().startswith('attachment;') or match is None:
        raise SmokeFailure('Missing UTF-8 attachment filename')
    filename = unquote(match.group(1))
    role = 'presentatore' if view == 'presenter' else 'partecipante'
    if '/' in filename or '\\' in filename or not filename.endswith(f' - {role}.{fmt}'):
        raise SmokeFailure('Incorrect/suspicious view-specific filename')


def make_opener():
    return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()), RefuseRedirect())


def http_request(opener, base: str, route: str, *, data: bytes | None = None, timeout: int = 120):
    headers = {'Accept': 'application/octet-stream'}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    request = Request(base + route, data=data, headers=headers, method='POST' if data is not None else 'GET')
    try:
        response = opener.open(request, timeout=timeout)
    except HTTPError as err:
        err.close()
        return err.code, {}, b''
    with response:
        reported = response.headers.get('Content-Length')
        if reported is not None:
            if not reported.isdecimal() or int(reported) > MAX_BYTES:
                raise SmokeFailure('Invalid or oversized Content-Length')
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise SmokeFailure('Export exceeded the 50 MiB limit')
        if reported is not None and len(body) != int(reported):
            raise SmokeFailure('Incomplete HTTP response')
        return response.status, response.headers, body


def run() -> None:
    base = validated_base(os.environ['QUORIVIO_EXPORT_SMOKE_URL'])
    session_id = os.environ['QUORIVIO_EXPORT_SMOKE_SESSION_ID'].strip()
    email = os.environ['QUORIVIO_EXPORT_SMOKE_EMAIL'].strip()
    password = os.environ['QUORIVIO_EXPORT_SMOKE_PASSWORD']
    if not re.fullmatch(r'[0-9a-fA-F-]{36}', session_id) or not email or not password:
        raise SmokeFailure('Session ID or disposable presenter credentials are invalid')
    route = '/api/sessions/' + quote(session_id, safe='')
    anonymous = make_opener()
    status, _, _ = http_request(anonymous, base, route + '/export.pdf?view=presenter', timeout=20)
    if status != 401:
        raise SmokeFailure('Anonymous export did not return HTTP 401')
    authenticated = make_opener()
    login = json.dumps({'email': email, 'password': password}).encode('utf-8')
    status, _, body = http_request(authenticated, base, '/api/auth/login', data=login, timeout=30)
    if status != 200:
        raise SmokeFailure(f'Staging presenter authentication failed (HTTP {status})')
    try:
        response = json.loads(body)
    except ValueError as exc:
        raise SmokeFailure('Invalid sign-in response') from exc
    if response.get('must_change_password') or response.get('mfa_required'):
        raise SmokeFailure('Use a disposable already-initialized non-MFA staging account')
    for view in ('presenter', 'participant'):
        for fmt in ('pdf', 'pptx'):
            status, headers, payload = http_request(authenticated, base, route + f'/export.{fmt}?view={view}')
            if status != 200:
                raise SmokeFailure(f'{view} {fmt} failed (HTTP {status}); check app/converter logs privately')
            expected = 'application/pdf' if fmt == 'pdf' else PPTX_MIME
            if headers.get('Content-Type', '').split(';', 1)[0].strip().lower() != expected:
                raise SmokeFailure(f'{view} {fmt} has wrong Content-Type')
            check_filename(headers.get('Content-Disposition'), view, fmt)
            if fmt == 'pdf':
                verify_pdf(payload)
                print(f'PASS {view} PDF: {len(payload)} bytes, correct signature/filename')
            else:
                slides = verify_visual_pptx(payload)
                print(f'PASS {view} PPTX: {len(payload)} bytes, {slides} visual slides')
    print('PASS all four authenticated visual exports and anonymous access denial; no documents persisted')


if __name__ == '__main__':
    try:
        run()
    except (SmokeFailure, KeyError, OSError, ssl.SSLError) as exc:
        # Never print the login payload, cookies, URLs, file contents or traceback.
        print('FAIL visual export staging smoke: ' + (str(exc) if isinstance(exc, SmokeFailure) else type(exc).__name__), file=sys.stderr)
        sys.exit(1)
