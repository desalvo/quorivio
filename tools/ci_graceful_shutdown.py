#!/usr/bin/env python3
"""Disposable PostgreSQL-backed SIGTERM drain acceptance on the *second* API.

Must run only after all multi-replica and load acceptance that uses port 8081.
The surviving API on port 8080 must remain ready. No production SLO claims.
"""
import asyncio
import json
import os
from pathlib import Path
import signal
import time

import aiohttp

A='http://127.0.0.1:8080'
B='http://127.0.0.1:8081'


async def wait_for_restart_close(ws, seconds=8.0, max_inflight=32):
    """Require a real 1012 handshake, tolerating only queued snapshots.

    A snapshot can be sent concurrently with SIGTERM and can already be in the
    socket's receive queue. The first frame after SIGTERM is therefore not
    necessarily the close frame. An ERROR, a different close code, or a stream
    of unexpected messages is still a hard integration failure.
    """
    deadline = time.monotonic() + seconds
    inflight = 0
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise AssertionError(f'no 1012 restart close within {seconds}s ({inflight} queued snapshots)')
        try:
            message = await ws.receive(timeout=remaining)
        except asyncio.TimeoutError as exc:
            raise AssertionError(f'no 1012 restart close within {seconds}s ({inflight} queued snapshots)') from exc
        if message.type == aiohttp.WSMsgType.TEXT:
            try:
                payload = json.loads(message.data)
            except (TypeError, ValueError) as exc:
                raise AssertionError('invalid queued WebSocket JSON during drain') from exc
            if not isinstance(payload, dict) or payload.get('type') != 'snapshot':
                raise AssertionError('unexpected application message during graceful shutdown')
            inflight += 1
            if inflight > max_inflight:
                raise AssertionError('too many queued WebSocket snapshots during drain')
            continue
        if message.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSING, aiohttp.WSMsgType.CLOSED):
            code = ws.close_code
            if code is None and message.type == aiohttp.WSMsgType.CLOSE:
                code = message.data
            assert code == 1012, f'WebSocket restart close must be 1012 (received {code!r})'
            return inflight
        if message.type == aiohttp.WSMsgType.ERROR:
            raise AssertionError(f'WebSocket transport error during drain: {type(message.data).__name__}')
        raise AssertionError(f'unexpected WebSocket frame during drain: {message.type!s}')


async def main():
    pidfile=Path('/tmp/quorivio-ci-replica.pid')
    pid=int(pidfile.read_text().strip())
    assert pid > 1, 'missing disposable replica PID'
    timeout=aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar(unsafe=True),timeout=timeout) as client:
        async with client.post(A+'/api/auth/login',json={'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
                                                         'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']},
                               headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']}) as response:
            assert response.status==200, 'disposable presenter login failed'
        async with client.post(A+'/api/sessions',json={'title':'CI graceful rolling drain'},
                               headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']}) as response:
            assert response.status==201, 'disposable session creation failed'
            sid=(await response.json())['id']
        async with client.ws_connect(f'ws://127.0.0.1:8081/live?session={sid}',
                                      headers={'Origin':A,'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']}) as ws:
            initial=await ws.receive(timeout=7)
            assert initial.type==aiohttp.WSMsgType.TEXT and initial.json().get('type')=='snapshot', 'no initial live snapshot'
            os.kill(pid,signal.SIGTERM)
            deadline=time.monotonic()+3
            was_draining=False
            while time.monotonic()<deadline:
                try:
                    async with client.get(B+'/api/health/ready') as r:
                        if r.status==503 and (await r.json()).get('status')=='draining':
                            was_draining=True
                            break
                except aiohttp.ClientError:
                    break
                await asyncio.sleep(.075)
            assert was_draining, 'terminating replica never reported readiness=503 before stopping'
            inflight=await wait_for_restart_close(ws)
            print(f'Rolling drain: received WebSocket restart close 1012 after {inflight} in-flight snapshots')
        async with client.get(A+'/api/health/ready') as response:
            assert response.status==200, 'surviving replica failed readiness after peer termination'
        # The HTTP server should stop after the short readiness-drain interval.
        for _ in range(80):
            try:
                os.kill(pid,0)
                # A GitHub Actions background child can briefly remain as a
                # zombie after exiting; it no longer serves connections.
                stat_path=Path(f'/proc/{pid}/stat')
                if stat_path.is_file() and stat_path.read_text().split(') ',1)[1].startswith('Z '):
                    break
            except ProcessLookupError:
                break
            await asyncio.sleep(.1)
        else:
            raise AssertionError('terminated API replica did not exit within 8 seconds')
    print('PASS PostgreSQL rolling SIGTERM: readiness 503 before shutdown, WS 1012, surviving replica healthy')


if __name__=='__main__':
    asyncio.run(main())
