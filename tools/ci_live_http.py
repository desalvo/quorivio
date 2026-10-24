#!/usr/bin/env python3
"""Disposable PostgreSQL-backed live lifecycle acceptance smoke.

Exercises the actual HTTP API with independent participant cookie jars and
concurrent submissions. This is not a 500-client load or WebSocket test.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
import http.cookiejar
import json
import os
import time
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

BASE = os.environ.get('QUORIVIO_CI_BASE_URL', 'http://127.0.0.1:8080')
EMAIL = os.environ['QUORIVIO_CI_ADMIN_EMAIL']
PASSWORD = os.environ['QUORIVIO_CI_NEW_PASSWORD']


def client():
    return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))


def call(opener, method, path, payload=None, expected=200):
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(BASE + path, data=data, method=method,
                  headers={'Content-Type': 'application/json'} if data else {})
    try:
        with opener.open(req, timeout=20) as response:
            status, raw = response.status, response.read()
    except HTTPError as error:
        status, raw = error.code, error.read()
    assert status == expected, f'{method} {path}: expected {expected}, got {status}, {raw[:180]!r}'
    return json.loads(raw) if raw else None


def participant(index, code, aid):
    visitor = client()
    call(visitor, 'POST', f'/api/join/{code}', {'pseudonym': f'CI-{index}'})
    answer = {'activity_id': aid, 'option_id': 'yes'}
    first = call(visitor, 'POST', f'/api/join/{code}/respond', answer)
    second = call(visitor, 'POST', f'/api/join/{code}/respond', answer)
    assert first == {'ok': True, 'already_submitted': False}, first
    assert second == {'ok': True, 'already_submitted': True}, second
    return visitor


def run():
    admin = client()
    call(admin, 'POST', '/api/auth/login', {'email': EMAIL, 'password': PASSWORD})
    session = call(admin, 'POST', '/api/sessions', {'title': 'CI concurrent live lifecycle'}, 201)
    sid, code = session['id'], session['join_code']
    poll = call(admin, 'POST', f'/api/sessions/{sid}/activities', {
        'title': 'CI live poll', 'type': 'poll',
        'options': [{'id': 'yes', 'label': 'Yes'}, {'id': 'no', 'label': 'No'}]
    }, 201)
    aid = poll['id']
    call(admin, 'POST', f'/api/sessions/{sid}/status', {'status': 'active'})
    call(admin, 'POST', f'/api/sessions/{sid}/activities/{aid}/open', {})
    assert call(client(), 'GET', f'/api/join/{code}')['activity']['id'] == aid
    call(client(), 'POST', f'/api/join/{code}/respond',
         {'activity_id': aid, 'option_id': 'yes'}, 401)
    with ThreadPoolExecutor(max_workers=8) as pool:
        visitors = list(pool.map(lambda i: participant(i, code, aid), range(24)))
    report = call(admin, 'GET', f'/api/sessions/{sid}/report.json')
    row = next(row for row in report['totals'] if row['activity_id'] == aid)
    assert row['valid'] == 24 and row['total'] == 24, row
    assert 'participants' not in report and 'pseudonym' not in json.dumps(report)
    call(admin, 'POST', f'/api/sessions/{sid}/activities/{aid}/close', {})
    # Exercise the independent timed-quiz path against PostgreSQL's clock.
    timed = call(admin, 'POST', f'/api/sessions/{sid}/activities', {
        'title': 'CI timed quiz', 'type': 'timed_quiz', 'duration_seconds': 5,
        'correct_option_id': 'yes',
        'options': [{'id': 'yes', 'label': 'Yes'}, {'id': 'no', 'label': 'No'}]
    }, 201)
    tid = timed['id']
    call(admin, 'POST', f'/api/sessions/{sid}/activities/{tid}/open', {})
    accepted = call(visitors[0], 'POST', f'/api/join/{code}/respond',
                    {'activity_id': tid, 'option_id': 'yes'})
    assert accepted['ok'] and not accepted['already_submitted']
    time.sleep(5.3)
    call(visitors[1], 'POST', f'/api/join/{code}/respond',
         {'activity_id': tid, 'option_id': 'yes'}, 409)
    timed_report = call(admin, 'GET', f'/api/sessions/{sid}/report.json')
    timed_row = next(row for row in timed_report['totals'] if row['activity_id'] == tid)
    assert timed_row['valid'] == 1, timed_row
    call(admin, 'POST', f'/api/sessions/{sid}/activities/{tid}/close', {})
    call(visitors[0], 'POST', f'/api/join/{code}/respond',
         {'activity_id': aid, 'option_id': 'no'}, 409)
    call(admin, 'POST', f'/api/sessions/{sid}/status', {'status': 'closed'})
    call(client(), 'GET', f'/api/join/{code}', expected=404)
    print('PASS PostgreSQL HTTP live: 24 independent concurrent participants, idempotency, timed expiry, privacy, closed-state rejection')


if __name__ == '__main__':
    run()
