#!/usr/bin/env python3
"""Opt-in 500-person *answer* trial against an owner's Quorivio demo presentation.

Unlike tools/load_500.py (which measures WebSocket presence), this submits an
independent, real server-authoritative poll answer from each simulated visitor.
No servers or sessions are modified until an operator explicitly runs this CLI.
The tool refuses arbitrary presentations and does not delete any data.

Presenter's q_auth cookie: QUORIVIO_LOAD_PRESENTER_COOKIE='q_auth=...'
Staging only, optional: QUORIVIO_LOAD_TEST_TOKEN='...'
"""
from __future__ import annotations

import argparse
import asyncio
from collections import Counter
import json
import math
import os
from pathlib import Path
import re
import secrets
import sys
import time
from urllib.parse import urlsplit

DEMO_KEY = 'load-500-v1'
DEMO_QUESTION = 'Prova 500 risposte: quale funzionalità vuoi esplorare?'
OPTIONS = {'live', 'quiz', 'questions'}
WIDGET_ID = 'load-500-question'
UUID = re.compile(r'^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')


def validate_origin(url: str, confirm_host: str) -> str:
    try:
        parsed = urlsplit(url)
        port = parsed.port  # force validation
    except (ValueError, TypeError) as exc:
        raise ValueError('Invalid base URL or port') from exc
    if (parsed.scheme not in ('https', 'http') or not parsed.hostname or
        parsed.username or parsed.password or parsed.query or parsed.fragment or
        parsed.path not in ('', '/') or parsed.hostname.lower() != confirm_host.lower()):
        raise ValueError('--confirm-host must exactly match the server hostname; no URL credentials, paths or fragments')
    if parsed.scheme == 'http' and parsed.hostname not in ('127.0.0.1', 'localhost', '::1'):
        raise ValueError('Real servers must use HTTPS; insecure HTTP is restricted to loopback')
    return f'{parsed.scheme}://{parsed.netloc}'


def validate_join_path(path: str) -> str:
    if not isinstance(path, str) or not re.fullmatch(r'/join/[A-Za-z0-9_-]{8,128}', path):
        raise ValueError('Unexpected join URL; refusing a different destination')
    return path.rsplit('/', 1)[-1]


def percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ranked = sorted(values)
    return round(ranked[max(0, math.ceil(len(ranked)*percent/100)-1)], 1)


def arguments(argv: list[str] | None = None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url', required=True, help='HTTPS URL of your own Quorivio instance (or loopback HTTP)')
    p.add_argument('--confirm-host', required=True, help='Exact DNS name or loopback hostname, as an anti-mistarget guard')
    p.add_argument('--confirm-run', action='store_true', help='Explicitly authorize synthetic participants and responses')
    p.add_argument('--session-id', help='Optional UUID to choose a specific account demo session')
    p.add_argument('--open-test-question', action='store_true', help='Start the demo session and publish its designated question')
    p.add_argument('--reset-before', action='store_true', help='Explicitly clear previous demo votes and rotate QR before opening the question')
    p.add_argument('--live-presence', action='store_true', help='Keep each participant WebSocket connected and verify presenter-visible count')
    p.add_argument('--hold-seconds', type=float, default=60, help='How long to retain all WebSockets after responses (minimum 20 seconds)')
    p.add_argument('--users', type=int, default=500)
    p.add_argument('--concurrency', type=int, default=30)
    p.add_argument('--ramp-seconds', type=float, default=900, help='900s default respects 100/min/IP rate limit for 2 calls/user')
    p.add_argument('--option-id', choices=sorted(OPTIONS), default='live')
    p.add_argument('--timeout', type=float, default=30)
    p.add_argument('--json-out', type=Path, help='Sanitized, aggregate JSON results (no join tokens, IDs, cookies, or names)')
    a = p.parse_args(argv)
    try:
        a.origin = validate_origin(a.base_url, a.confirm_host)
    except ValueError as exc:
        p.error(str(exc))
    if not a.confirm_run:
        p.error('Pass --confirm-run to authorize this real, mutating 500-person test')
    if not 1 <= a.users <= 500 or not 1 <= a.concurrency <= 100 or a.timeout <= 0 or a.ramp_seconds < 0:
        p.error('users: 1..500; concurrency: 1..100; timeout > 0; ramp-seconds >= 0')
    if a.reset_before and not a.open_test_question:
        p.error('--reset-before requires --open-test-question')
    if a.live_presence and a.users >= 20 and a.hold_seconds < 20:
        p.error('--live-presence requires --hold-seconds >= 20')
    if a.session_id and not UUID.fullmatch(a.session_id):
        p.error('--session-id must be a UUID')
    a.presenter_cookie = os.environ.get('QUORIVIO_LOAD_PRESENTER_COOKIE', '')
    if not re.fullmatch(r'q_auth=[A-Za-z0-9._-]{32,1024}', a.presenter_cookie):
        p.error('Set QUORIVIO_LOAD_PRESENTER_COOKIE=q_auth=... from an authenticated presenter; never supply it on the CLI')
    a.load_token = os.environ.get('QUORIVIO_LOAD_TEST_TOKEN', '')
    if a.load_token and (len(a.load_token) < 32 or len(a.load_token) > 512):
        p.error('The optional staging token must contain 32..512 characters')
    # Server enforces 100 requests/minute/source IP in production. Each synthetic
    # participant needs JOIN + ANSWER, plus a handful of presenter read requests.
    if not a.load_token and a.users > 10 and a.ramp_seconds < a.users*2/90*60:
        p.error('Ramp too aggressive for 100 req/min/source IP: use >= users*2/90*60 seconds, or an authorized staging-only load token')
    return a


async def main(argv: list[str] | None = None):
    a = arguments(argv)
    try:
        import aiohttp
    except ImportError as exc:
        raise SystemExit('Requires aiohttp; install python3 -m pip install aiohttp') from exc
    timeout = aiohttp.ClientTimeout(total=a.timeout)
    hdr = {'Origin':a.origin, 'Cookie':a.presenter_cookie}
    load_headers = {'X-Quorivio-Load-Token':a.load_token} if a.load_token else {}
    hdr.update(load_headers)

    async def get_json(client, method: str, path: str, *, headers=None, data=None, expected=(200,)):
        async with client.request(method, a.origin+path, headers=headers, json=data, allow_redirects=False) as r:
            if r.status not in expected:
                raise RuntimeError(f'{method} {path.split("?")[0].split("/")[2:3][0] if len(path.split("/"))>2 else "api"} HTTP {r.status}')
            return await r.json()

    async with aiohttp.ClientSession(timeout=timeout, trust_env=False) as presenter:
        selected = []
        if a.session_id:
            session = await get_json(presenter,'GET',f'/api/sessions/{a.session_id}',headers=hdr)
            selected = [session['session']]
        else:
            for page in range(1,51):
                result = await get_json(presenter,'GET',f'/api/sessions?page={page}&page_size=100',headers=hdr)
                selected.extend(s for s in result['items'] if s.get('demo_template_key') == DEMO_KEY and s.get('access_role') == 'owner')
                if len(result['items']) < 100:
                    break
        if len(selected) != 1 or selected[0].get('demo_template_key') != DEMO_KEY:
            raise RuntimeError('Expected exactly one private owner demo session; use --session-id or open Dashboard to provision it')
        sid = selected[0]['id']
        if not UUID.fullmatch(sid):
            raise RuntimeError('Invalid demo session ID from server')
        snap = await get_json(presenter,'GET',f'/api/sessions/{sid}',headers=hdr)
        activities = [x for x in snap['activities'] if x.get('type')=='poll' and x.get('title')==DEMO_QUESTION]
        if len(activities)!=1 or {o['id'] for o in activities[0].get('options',[])} != OPTIONS:
            raise RuntimeError('Demo question definition was modified; delete demo session to recreate the official template')
        widget = next((w for w in activities[0].get('page_design',{}).get('widgets',[]) if w.get('id') == WIDGET_ID),None)
        if (not widget or widget.get('kind') != 'question' or widget.get('answerMode') != 'single' or
            {o['id'] for o in widget.get('options',[])} != OPTIONS):
            raise RuntimeError('Demo question widget was modified; delete demo session to recreate it')
        aid = activities[0]['id']
        if not UUID.fullmatch(aid):
            raise RuntimeError('Invalid poll activity ID from server')
        code = validate_join_path(selected[0].get('join_url',''))
        if a.reset_before:
            if snap['session']['status'] in ('active','paused'):
                await get_json(presenter,'POST',f'/api/sessions/{sid}/reset-to-ready',headers=hdr,
                               data={'confirmation':'RESET_SESSION_RESULTS'})
                snap=await get_json(presenter,'GET',f'/api/sessions/{sid}',headers=hdr)
                code=validate_join_path(snap['session'].get('join_url',''))
            elif snap['session']['status']=='closed':
                raise RuntimeError('Closed demo must be deleted and recreated before a new test')
        if a.open_test_question:
            status = snap['session']['status']
            if status == 'closed':
                raise RuntimeError('Demo session is closed; delete it and refresh the Dashboard to recreate it')
            if status != 'active':
                await get_json(presenter,'POST',f'/api/sessions/{sid}/status',headers=hdr,data={'status':'active'})
            if snap['session']['current_activity_id'] != aid:
                await get_json(presenter,'POST',f'/api/sessions/{sid}/activities/{aid}/open',headers=hdr,data={})
        public = await get_json(presenter,'GET',f'/api/join/{code}',headers=load_headers)
        if public.get('session',{}).get('id')!=sid or public.get('activity',{}).get('id')!=aid:
            raise RuntimeError('The specific demo question is not published; use --open-test-question or activate it in the presenter UI')
        async def count_widget_votes():
            stats=await get_json(presenter,'GET',f'/api/sessions/{sid}/widget-answers',headers=hdr)
            if not isinstance(stats,list):
                raise RuntimeError('Widget answer aggregate is unavailable')
            return sum(int(x['responses']) for x in stats if x.get('activity_id')==aid
                       and x.get('widget_id')==WIDGET_ID and x.get('question_id')=='')
        start_votes = await count_widget_votes()
        joined, answered, join_times, answer_times = 0,0,[],[]
        failures=Counter()
        lock=asyncio.Lock()
        semaphore=asyncio.Semaphore(a.concurrency)
        started=time.monotonic()
        run_tag=secrets.token_hex(5)
        completed=0
        submissions_done=asyncio.Event()
        release_presence=asyncio.Event()
        stop_monitor=asyncio.Event()
        presenter_peak=0
        ws_url=f'{"wss" if a.origin.startswith("https:") else "ws"}://{urlsplit(a.origin).netloc}/live?session={sid}'

        async def observer():
            nonlocal presenter_peak
            try:
                async with presenter.ws_connect(ws_url,headers=hdr,heartbeat=20) as ws:
                    while not stop_monitor.is_set():
                        try:
                            msg=await asyncio.wait_for(ws.receive(),timeout=4)
                            if msg.type==aiohttp.WSMsgType.TEXT:
                                payload=json.loads(msg.data)
                                if payload.get('type')=='snapshot':
                                    count=(payload.get('data') or {}).get('connected_participants')
                                    if isinstance(count,int): presenter_peak=max(presenter_peak,count)
                            elif msg.type in (aiohttp.WSMsgType.CLOSED,aiohttp.WSMsgType.ERROR):
                                raise RuntimeError('presenter_ws_closed')
                        except asyncio.TimeoutError:
                            continue
            except Exception:
                failures['presenter_observer_unavailable']+=1

        monitor=asyncio.create_task(observer()) if a.live_presence else None

        async def actor(i:int):
            nonlocal joined,answered,completed
            await asyncio.sleep(i*a.ramp_seconds/max(1,a.users))
            ws=None
            async with aiohttp.ClientSession(timeout=timeout,trust_env=False,cookie_jar=aiohttp.CookieJar(unsafe=True)) as visitor:
                async with semaphore:
                    try:
                        t0=time.monotonic()
                        j=await get_json(visitor,'POST',f'/api/join/{code}',headers=load_headers,
                                         data={'pseudonym':f'Load-{run_tag}-{i:04d}'})
                        if not j.get('ok') or j.get('rejoined'):
                            raise RuntimeError('join not confirmed or existing identity')
                        t1=time.monotonic()
                        async with lock:
                            joined+=1
                            join_times.append((t1-t0)*1000)
                        if a.live_presence:
                            ws=await visitor.ws_connect(ws_url,headers={'Origin':a.origin,**load_headers},heartbeat=20)
                            event=await asyncio.wait_for(ws.receive(),timeout=a.timeout)
                            if event.type!=aiohttp.WSMsgType.TEXT:
                                raise RuntimeError('participant_ws_not_authorized')
                            # The participant stream must not leak presenter-only count.
                            payload=json.loads(event.data)
                            if (payload.get('type')!='snapshot' or
                                'connected_participants' in (payload.get('data') or {})):
                                raise RuntimeError('participant_ws_privacy_or_snapshot_error')
                        result=await get_json(visitor,'POST',f'/api/join/{code}/activities/{aid}/widgets/{WIDGET_ID}/respond',headers=load_headers,
                                              data={'option_id':a.option_id,'question_id':''})
                        if result.get('ok') is not True or result.get('already_submitted'):
                            raise RuntimeError('answer not confirmed as new')
                        t2=time.monotonic()
                        async with lock:
                            answered+=1
                            answer_times.append((t2-t1)*1000)
                    except Exception as exc:
                        # No identifiers, tokens, names or raw HTTP bodies in diagnostics.
                        reason=str(exc)
                        if ' HTTP ' in reason: reason='HTTP_'+reason.rsplit(' HTTP ',1)[-1]
                        elif 'join not confirmed' in reason: reason='join_duplicate'
                        elif 'answer not confirmed' in reason: reason='answer_unconfirmed'
                        elif reason.startswith('participant_ws_'): reason=reason
                        else: reason=type(exc).__name__
                        async with lock: failures[reason]+=1
                    finally:
                        async with lock:
                            completed+=1
                            if completed==a.users:submissions_done.set()
                # Keep all successfully connected participant sockets open until the
                # presenter can inspect the peak. Do not hold the concurrency semaphore.
                if ws is not None:
                    await release_presence.wait()
                    await ws.close()
        tasks=[asyncio.create_task(actor(i)) for i in range(a.users)]
        await submissions_done.wait()
        if a.live_presence:
            await asyncio.sleep(a.hold_seconds)
        release_presence.set()
        await asyncio.gather(*tasks)
        stop_monitor.set()
        if monitor is not None:await monitor
        end_votes = await count_widget_votes()
        delta = end_votes-start_votes
        report = {
            'scenario':'quorivio-load-500-single-poll','target_users':a.users,
            'joined_new':joined,'responses_acknowledged':answered,
            'websocket_presence_enabled':a.live_presence,
            'presenter_peak_connected':presenter_peak if a.live_presence else None,
            'presenter_count_verified':(presenter_peak==a.users) if a.live_presence else None,
            'server_widget_answers_before':start_votes,'server_widget_answers_after':end_votes,
            'server_confirmed_new_responses':delta,
            'join_latency_ms':{f'p{x}':percentile(join_times,x) for x in (50,95,99)},
            'answer_latency_ms':{f'p{x}':percentile(answer_times,x) for x in (50,95,99)},
            'elapsed_seconds':round(time.monotonic()-started,2),
            'error_counts':dict(failures),
            'passed':answered==joined==a.users and delta==a.users and not failures and (not a.live_presence or presenter_peak==a.users),
            'privacy_note':'Only aggregate counts and performance; no join URLs, cookies, PII or individual answers.'
        }
        output=json.dumps(report,ensure_ascii=False,indent=2)
        print(output)
        if a.json_out:
            a.json_out.write_text(output+'\n',encoding='utf8')
        if not report['passed']:
            raise SystemExit(2)


if __name__=='__main__':
    try: asyncio.run(main())
    except (ValueError,RuntimeError) as exc:
        # Error text never embeds secrets; no URLs or cookies in exceptions.
        print(f'Load test rejected: {exc}',file=sys.stderr)
        raise SystemExit(2)
