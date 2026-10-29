#!/usr/bin/env python3
"""Disposable PostgreSQL-backed SIGTERM drain acceptance on the *second* API.

Must run only after all multi-replica and load acceptance that uses port 8081.
The surviving API on port 8080 must remain ready. No production SLO claims.
"""
import asyncio
import os
from pathlib import Path
import signal
import time

import aiohttp

A='http://127.0.0.1:8080'
B='http://127.0.0.1:8081'


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
            close=await ws.receive(timeout=7)
            assert close.type in (aiohttp.WSMsgType.CLOSE,aiohttp.WSMsgType.CLOSING), 'WebSocket was not gracefully closed'
            assert ws.close_code==1012 or close.data==1012, 'WebSocket must signal 1012 service restart'
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
