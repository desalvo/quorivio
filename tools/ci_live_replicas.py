#!/usr/bin/env python3
"""Real PostgreSQL two-process LISTEN/NOTIFY and WebSocket acceptance.

Uses two API processes sharing a database, not an in-memory mocked bus.
A presenter and participant connect to different replicas, and mutations on
one replica must arrive on the other without polling HTTP for results.
"""
import asyncio
import os
import time
from urllib.parse import urlparse

import aiohttp

A = os.environ.get('QUORIVIO_CI_BASE_URL', 'http://127.0.0.1:8080')
B = os.environ.get('QUORIVIO_CI_REPLICA_URL', 'http://127.0.0.1:8081')
EMAIL = os.environ['QUORIVIO_CI_ADMIN_EMAIL']
PASSWORD = os.environ['QUORIVIO_CI_NEW_PASSWORD']
TOKEN = os.environ['QUORIVIO_CI_LOAD_TOKEN']
HEADERS = {'X-Quorivio-Load-Token': TOKEN}


async def api(client, origin, method, route, body=None, status=200):
    async with client.request(method, origin + route, json=body, headers=HEADERS) as response:
        value = await response.json(content_type=None)
        assert response.status == status, (method, route, response.status, value)
        return value


def ws_url(origin, sid):
    parsed = urlparse(origin)
    return f'{"wss" if parsed.scheme == "https" else "ws"}://{parsed.netloc}/live?session={sid}'


async def snapshot_matching(ws, predicate, description, timeout=12):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        remaining = end - time.monotonic()
        message = await ws.receive(timeout=max(0.01, remaining))
        if message.type != aiohttp.WSMsgType.TEXT:
            raise AssertionError(f'{description}: WebSocket ended: {message.type}')
        payload = message.json()
        if payload.get('type') == 'snapshot' and predicate(payload.get('data') or {}):
            return payload['data']
    raise AssertionError(f'{description}: no matching snapshot in {timeout}s')


async def drain_pending_snapshots(ws):
    """Discard pre-mutation notifications so assertions observe a NEW delivery."""
    while True:
        try:
            message = await ws.receive(timeout=0.12)
        except asyncio.TimeoutError:
            return
        if message.type != aiohttp.WSMsgType.TEXT:
            raise AssertionError(f'WebSocket closed while draining: {message.type}')



async def main():
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True), timeout=timeout) as admin, \
               aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True), timeout=timeout) as visitor:
        await api(admin, A, 'POST', '/api/auth/login', {'email': EMAIL, 'password': PASSWORD})
        session = await api(admin, A, 'POST', '/api/sessions', {'title': 'CI two-replica live acceptance'}, 201)
        sid, code = session['id'], session['join_code']
        poll = await api(admin, A, 'POST', f'/api/sessions/{sid}/activities', {
            'title': 'Replica poll', 'type': 'poll',
            'options': [{'id': 'yes', 'label': 'Yes'}, {'id': 'no', 'label': 'No'}]
        }, 201)
        aid = poll['id']
        await api(admin, A, 'POST', f'/api/sessions/{sid}/status', {'status': 'active'})
        await api(visitor, B, 'POST', f'/api/join/{code}', {'pseudonym': 'Replica participant'})
        async with admin.ws_connect(ws_url(B, sid), headers={**HEADERS, 'Origin': A}) as presenter_ws, \
                   visitor.ws_connect(ws_url(A, sid), headers={**HEADERS, 'Origin': A}) as participant_ws:
            await snapshot_matching(presenter_ws, lambda d: d.get('session', {}).get('id') == sid,
                                    'presenter initial state')
            initial = await snapshot_matching(participant_ws, lambda d: d.get('session', {}).get('id') == sid,
                                              'participant initial state')
            assert 'results' in initial and not initial['results'], 'participant must not see unpublished results'
            # A mutates, B presenter must receive the PostgreSQL notification.
            await api(admin, A, 'POST', f'/api/sessions/{sid}/activities/{aid}/open', {})
            await snapshot_matching(presenter_ws,
                                    lambda d: d.get('session', {}).get('current_activity_id') == aid,
                                    'A -> B activity open')
            opened = await snapshot_matching(participant_ws,
                                    lambda d: d.get('session', {}).get('current_activity_id') == aid,
                                    'participant sees activity open')
            assert not opened.get('results') and not opened.get('totals'), 'unpublished poll results leaked'
            # Discard queued open-state notifications; require a post-vote notification.
            await drain_pending_snapshots(participant_ws)
            await drain_pending_snapshots(presenter_ws)
            # B mutates, A participant sees updated state; B presenter sees result.
            await api(visitor, B, 'POST', f'/api/join/{code}/respond',
                      {'activity_id': aid, 'option_id': 'yes'})
            repeated = await api(visitor, B, 'POST', f'/api/join/{code}/respond',
                                 {'activity_id': aid, 'option_id': 'yes'})
            assert repeated == {'ok': True, 'already_submitted': True}, repeated
            result = await snapshot_matching(presenter_ws,
                                             lambda d: any(r.get('activity_id') == aid and r.get('count') == 1
                                                           for r in d.get('totals', [])),
                                             'B -> A/B response count')
            assert 'participants' not in result, 'aggregate snapshot must not contain participant records'
            audience = await snapshot_matching(participant_ws,
                                               lambda d: d.get('session', {}).get('current_activity_id') == aid,
                                               'participant receives NEW post-vote snapshot')
            assert not audience.get('results') and not audience.get('totals'), 'unpublished results leaked after vote'
            assert 'connected_participants' not in audience and 'participants' not in audience, 'private presence leaked'
            # Simulate a real network drop after a committed response. The same
            # cookie-bound participant must reconnect on the OTHER replica,
            # receive the current page state immediately and never receive
            # presenter-only totals. Reconnect must not create a second vote.
            await participant_ws.close()
            assert participant_ws.closed, 'initial participant socket did not close'
            async with visitor.ws_connect(ws_url(B, sid), headers={**HEADERS, 'Origin': A}) as recovered_ws:
                recovered = await snapshot_matching(recovered_ws,
                    lambda d: d.get('session', {}).get('current_activity_id') == aid,
                    'disconnected A -> reconnected B participant snapshot')
                assert not recovered.get('results') and not recovered.get('totals'), 'reconnect leaked presenter results'
                assert 'participants' not in recovered and 'connected_participants' not in recovered, 'reconnect leaked presence'
                repeated_after_reconnect = await api(visitor, B, 'POST', f'/api/join/{code}/respond',
                    {'activity_id': aid, 'option_id': 'yes'})
                assert repeated_after_reconnect == {'ok': True, 'already_submitted': True}, repeated_after_reconnect
                # Closing from B must propagate across replicas, including to
                # a fresh socket that was opened only AFTER the committed vote.
                await drain_pending_snapshots(recovered_ws)
                await drain_pending_snapshots(presenter_ws)
                await api(admin, A, 'POST', f'/api/sessions/{sid}/activities/{aid}/close', {})
                participant = await snapshot_matching(recovered_ws,
                    lambda d: d.get('session', {}).get('current_activity_id') is None,
                    'A -> B activity close after reconnect')
                assert not participant.get('results') and not participant.get('totals'), participant
                await api(admin, A, 'POST', f'/api/sessions/{sid}/status', {'status': 'closed'})
                await snapshot_matching(presenter_ws,
                    lambda d: d.get('session', {}).get('status') == 'closed', 'cross-replica session close')
                final = await snapshot_matching(recovered_ws,
                    lambda d: d.get('session', {}).get('status') == 'closed', 'session close after reconnect')
                assert not final.get('results') and not final.get('totals'), 'closed session leaked private results'
    print('PASS PostgreSQL two-replica WebSocket: A->B opening, B->A response, reconnect on B, private state and closing')


if __name__ == '__main__':
    asyncio.run(main())
