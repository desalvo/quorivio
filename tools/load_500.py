#!/usr/bin/env python3
"""Authorized anonymous QR/URL load simulation for Quorivio staging (aiohttp).

500 participants TOTAL across shards, plus one optional authenticated presenter observer.
No participant account is created. Every participant has an independent cookie jar.
Source IP selection requires the IPs to be configured on the load-generator host;
for genuinely different public IPs use separate machines / egress gateways.
"""
import argparse
import asyncio
import json
import math
import statistics
import re
import time
from pathlib import Path
from urllib.parse import urlparse, unquote



def options():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--join-url', required=True, help='Actual QR target URL, e.g. https://staging.example/join/SECRET')
    p.add_argument('--session-id', required=True, help='Session UUID used by WebSocket')
    p.add_argument('--users', type=int, default=500, help='Total users across all shards (max 500)')
    p.add_argument('--shards', type=int, default=1)
    p.add_argument('--shard-index', type=int, default=0, help='Zero-based shard index')
    p.add_argument('--ramp-seconds', type=float, default=60)
    p.add_argument('--hold-seconds', type=float, default=180)
    p.add_argument('--presenter-cookie', default='', help='Only for one observer shard; never printed')
    p.add_argument('--load-token', default='', help='Staging-only rate-limit bypass token')
    p.add_argument('--source-ips', default='', help='Comma-separated LOCAL source addresses already assigned to this host')
    p.add_argument('--json-out', default='', help='Optional path for this shard metrics')
    p.add_argument('--latency-samples', action='store_true', help='Include anonymous numeric latency samples for cross-shard SLO audit (no identifiers)')
    p.add_argument('--timeout', type=float, default=20)
    args = p.parse_args()
    if not 1 <= args.users <= 500: p.error('users must be 1..500')
    if not 1 <= args.shards <= args.users or not 0 <= args.shard_index < args.shards: p.error('invalid shards/index')
    if args.ramp_seconds < 0 or args.hold_seconds < 20 or args.timeout <= 0: p.error('invalid timing')
    url = urlparse(args.join_url)
    parts = url.path.rstrip('/').split('/')
    if url.scheme not in ('https', 'http') or not url.netloc or len(parts) != 3 or parts[:2] != ['', 'join'] or not parts[2]:
        p.error('join-url must be an absolute http(s) URL ending in /join/<QR-token>')
    if url.username or url.password or url.query or url.fragment: p.error('URL must not include credentials, query or fragment')
    if not re.fullmatch(r'[0-9a-fA-F-]{36}', args.session_id): p.error('session-id must be a UUID')
    if not re.fullmatch(r'[A-Za-z0-9_-]{8,128}', unquote(parts[2])): p.error('invalid QR token')
    args.origin = f'{url.scheme}://{url.netloc}'
    args.code = unquote(parts[2])
    args.wsurl = f'{"wss" if url.scheme == "https" else "ws"}://{url.netloc}/live?session={args.session_id}'
    args.source_ips = [x.strip() for x in args.source_ips.split(',') if x.strip()]
    return args


async def main():
    a = options()
    try:
        import aiohttp
    except ImportError as exc:
        raise SystemExit("Missing aiohttp: install Python load-test requirements before running the simulator") from exc
    indices = [i for i in range(a.users) if i % a.shards == a.shard_index]
    failures, joins, first_snapshots, close_count = [], [], [], 0
    presenter_peak = 0
    started = time.monotonic()
    headers = {'X-Quorivio-Load-Token': a.load_token} if a.load_token else {}
    timeout = aiohttp.ClientTimeout(total=a.timeout)
    ready = asyncio.Event()
    async def observer():
        nonlocal presenter_peak
        try:
            async with aiohttp.ClientSession(timeout=timeout, trust_env=False) as client:
                async with client.ws_connect(a.wsurl, heartbeat=20, headers={'Cookie':a.presenter_cookie,'Origin':a.origin,**headers}) as ws:
                    ready.set()
                    deadline = started+a.ramp_seconds+a.hold_seconds+10
                    while time.monotonic()<deadline:
                        try:
                            msg=await asyncio.wait_for(ws.receive(), timeout=min(5,max(.05,deadline-time.monotonic())))
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                value=json.loads(msg.data)
                                if value.get('type')=='snapshot':
                                    data=value.get('data') or {}
                                    count=data.get('connected_participants')
                                    if isinstance(count,int): presenter_peak=max(presenter_peak,count)
                            elif msg.type in (aiohttp.WSMsgType.CLOSED,aiohttp.WSMsgType.ERROR):
                                raise RuntimeError('presenter socket closed')
                        except asyncio.TimeoutError: pass
        except Exception as exc:
            failures.append('presenter: '+str(exc))
            ready.set()
    async def participant(i):
        nonlocal close_count
        await asyncio.sleep(i*a.ramp_seconds/max(a.users,1))
        bind = a.source_ips[i % len(a.source_ips)] if a.source_ips else None
        connector=aiohttp.TCPConnector(local_addr=(bind,0) if bind else None,limit=0)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, trust_env=False, cookie_jar=aiohttp.CookieJar(unsafe=True)) as client:
            t0=time.monotonic()
            try:
                # Mirror the QR flow: fetch landing page, discover session, join anonymously, open WS.
                async with client.get(a.join_url,headers=headers) as page:
                    if page.status != 200: raise RuntimeError(f'landing HTTP {page.status}')
                    await page.read()
                async with client.get(f'{a.origin}/api/join/{a.code}',headers=headers) as entry:
                    if entry.status != 200:raise RuntimeError(f'entry HTTP {entry.status}')
                    await entry.read()
                async with client.post(f'{a.origin}/api/join/{a.code}', json={'pseudonym':f'Load-{a.shard_index}-{i:04d}'},headers=headers) as joined:
                    if joined.status!=200: raise RuntimeError(f'join HTTP {joined.status}')
                    await joined.read()
                joins.append((time.monotonic()-t0)*1000)
                async with client.ws_connect(a.wsurl,headers={'Origin':a.origin,**headers},heartbeat=20) as ws:
                    deadline=started+a.ramp_seconds+a.hold_seconds
                    seen=False
                    while time.monotonic()<deadline:
                        try:
                            msg=await asyncio.wait_for(ws.receive(),timeout=min(5,max(.05,deadline-time.monotonic())))
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                obj=json.loads(msg.data)
                                if obj.get('type')=='snapshot' and not seen:
                                    data=obj.get('data') or {}
                                    if 'participants' in data or 'connected_participants' in data:
                                        raise RuntimeError('participant snapshot leaked presenter-only fields')
                                    if not data.get('session') or data['session'].get('id')!=a.session_id:
                                        raise RuntimeError('participant snapshot has wrong session')
                                    first_snapshots.append((time.monotonic()-t0)*1000)
                                    seen=True
                            elif msg.type in (aiohttp.WSMsgType.CLOSED,aiohttp.WSMsgType.ERROR):
                                raise RuntimeError('participant socket closed')
                        except asyncio.TimeoutError: pass
                    if not seen: raise RuntimeError('no snapshot received')
                    close_count+=1
            except Exception as exc:
                failures.append(f'participant {i}: {exc}')
    observe=asyncio.create_task(observer()) if a.presenter_cookie else None
    if observe:
        await asyncio.wait_for(ready.wait(),timeout=a.timeout+5)
        if failures: raise RuntimeError('Presenter connection failed; check cookie and session')
    await asyncio.gather(*(participant(i) for i in indices))
    if observe: await observe
    def percentile(series,p):
        s=sorted(series)
        return round(s[min(len(s)-1,math.ceil(len(s)*p)-1)],1) if s else None
    output={'elapsed_seconds':round(time.monotonic()-started,3),'shard':a.shard_index,'shards':a.shards,'target_total':a.users,'target_shard':len(indices),
            'anonymous_joins':len(joins),'websocket_completed':close_count,'errors':len(failures),
            'presenter_peak_distinct':presenter_peak if observe else None,
            'join_latency_ms':{f'p{p}':percentile(joins,p/100) for p in (50,95,99)},
            'first_snapshot_ms':{f'p{p}':percentile(first_snapshots,p/100) for p in (50,95,99)},
            'error_samples':failures[:15],
            'ramp_seconds':a.ramp_seconds,'hold_seconds':a.hold_seconds,
            **({'join_latency_samples_ms':[round(x,1) for x in joins],
                'first_snapshot_samples_ms':[round(x,1) for x in first_snapshots]} if a.latency_samples else {})}
    result=json.dumps(output,indent=2,ensure_ascii=False)
    print(result)
    if a.json_out: Path(a.json_out).write_text(result+'\n',encoding='utf-8')
    if failures or len(joins)!=len(indices) or close_count!=len(indices): raise SystemExit(2)
    if observe and presenter_peak < math.ceil(a.users*.95) and a.shards==1: raise SystemExit(2)

if __name__=='__main__': asyncio.run(main())
