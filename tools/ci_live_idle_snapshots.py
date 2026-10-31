#!/usr/bin/env python3
"""Opt-in real PostgreSQL two-replica, 70s quiet-session snapshot acceptance.

Never connect to production: both API origins must be localhost. The run creates
and removes a disposable session; private cookies/URLs are never logged.
Tests that owner and anonymous participant receive fresh full snapshots even
when there are no session updates after the initial join.
"""
import asyncio
import os
import time
from urllib.parse import urlparse

import aiohttp

from ci_live_replicas import api, ws_url

A = os.getenv('QUORIVIO_CI_BASE_URL', 'http://127.0.0.1:8080')
B = os.getenv('QUORIVIO_CI_REPLICA_URL', 'http://127.0.0.1:8081')
HEADERS = {'Origin': A, 'X-Quorivio-Load-Token': os.environ.get('QUORIVIO_CI_LOAD_TOKEN', '')}


def require_disposable_origins():
    for url in (A, B):
        parsed = urlparse(url)
        if (parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1')
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or parsed.path not in ('', '/') or not parsed.port):
            raise RuntimeError('idle-session acceptance is restricted to disposable loopback APIs')
    if len(HEADERS['X-Quorivio-Load-Token']) < 32:
        raise RuntimeError('missing disposable CI load token')


async def watch_quiet_snapshots(ws, session_id: str, role: str, duration: float = 70, now=time.monotonic):
    started = now()
    times = []
    while now() < started + duration:
        remaining = started + duration - now()
        try:
            msg = await ws.receive(timeout=min(25, max(.01, remaining)))
        except asyncio.TimeoutError:
            if now() < started + duration - .01:
                raise AssertionError(f'{role}: no authoritative snapshot within 25 seconds')
            break
        if msg.type != aiohttp.WSMsgType.TEXT:
            raise AssertionError(f'{role}: live socket closed during idle hold')
        frame = msg.json()
        if frame.get('type') != 'snapshot':
            raise AssertionError(f'{role}: non-snapshot cannot prove data freshness')
        snap = frame.get('data') or {}
        if snap.get('session', {}).get('id') != session_id:
            raise AssertionError(f'{role}: wrong-session snapshot')
        if role == 'participant' and any(k in snap for k in ('connected_participants', 'participants')):
            raise AssertionError('participant received private presenter presence')
        times.append(now() - started)
    # The first 1-2 deliveries may be caused by initial join/presence. Require
    # verified snapshots after two and three scheduled 20s heartbeat intervals.
    if not any(t >= 35 for t in times) or not any(t >= 55 for t in times):
        raise AssertionError(f'{role}: no sustained idle refresh after 35s and 55s')
    return len(times)


async def main():
    require_disposable_origins()
    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True), timeout=timeout) as admin, \
               aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True), timeout=timeout) as visitor:
        await api(admin, A, 'POST', '/api/auth/login', {'email': os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
                                                       'password': os.environ['QUORIVIO_CI_NEW_PASSWORD']})
        session = await api(admin, A, 'POST', '/api/sessions', {'title': 'Disposable idle heartbeat acceptance'}, 201)
        sid, code = session['id'], session['join_code']
        try:
            await api(admin, A, 'POST', f'/api/sessions/{sid}/status', {'status': 'active'})
            await api(visitor, B, 'POST', f'/api/join/{code}', {'pseudonym': 'Idle probe'})
            async with admin.ws_connect(ws_url(B, sid), headers=HEADERS) as presenter, \
                       visitor.ws_connect(ws_url(A, sid), headers=HEADERS) as participant:
                owner_n, audience_n = await asyncio.wait_for(asyncio.gather(
                    watch_quiet_snapshots(presenter, sid, 'presenter'),
                    watch_quiet_snapshots(participant, sid, 'participant'),
                ), timeout=85)
                if owner_n < 3 or audience_n < 3:
                    raise AssertionError('incomplete quiet-session snapshots')
        finally:
            await api(admin, A, 'DELETE', f'/api/sessions/{sid}', status=204)
    print('PASS idle live: 70s two-replica PostgreSQL WebSocket snapshots without mutations, owner/participant isolation, no silent disconnect')


if __name__ == '__main__':
    asyncio.run(main())
