#!/usr/bin/env python3
"""Opt-in, disposable PostgreSQL-backed 500-participant CI acceptance.

Never target public production. This uses the CI's ephemeral local API, generates
its own private session, and verifies the observer's shared-session peak.
"""
import argparse
import json
import os
import re
from urllib.parse import urlsplit
from pathlib import Path
import subprocess
import sys
import tempfile
from aggregate_load_500 import reconcile, reconcile_slo


def normalize_disposable_join_url(base_url: str, returned_url: str) -> str:
    """Convert the API's root-relative QR URL into a safe loopback load target.

    The public load simulator legitimately insists on an absolute URL; the
    authenticated session API intentionally returns a path-only join_url.
    No external address, unexpected path, query, fragment or user-info may be
    introduced by a response from the disposable API.
    """
    try:
        base = urlsplit(base_url)
        port = base.port
    except (TypeError, ValueError) as exc:
        raise RuntimeError('capacity CI requires a valid loopback base URL') from exc
    if (base.scheme != 'http' or base.hostname not in ('127.0.0.1', 'localhost')
            or port is None or not 1 <= port <= 65535 or base.username or base.password
            or base.path not in ('', '/') or base.query or base.fragment):
        raise RuntimeError('capacity CI is restricted to disposable loopback APIs')
    if not isinstance(returned_url, str):
        raise RuntimeError('capacity CI requires a session join URL')
    try:
        join = urlsplit(returned_url)
    except ValueError as exc:
        raise RuntimeError('capacity CI received an invalid session join URL') from exc
    if (join.query or join.fragment or join.username or join.password or
            join.scheme not in ('', base.scheme) or
            join.netloc not in ('', base.netloc) or
            not re.fullmatch(r'/join/[A-Za-z0-9_-]{8,128}', join.path)):
        raise RuntimeError('capacity CI refuses an unsafe session join URL')
    # The simulator expects an absolute QR target; the CI may never leave the
    # exact configured loopback origin, even if the API returns an absolute URL.
    return f'{base.scheme}://{base.netloc}{join.path}'


def run(*, strict_slo=False):
    base=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
    # Validate the destination before even authenticating to the disposable API.
    normalize_disposable_join_url(base, '/join/SAFE_TOKEN')
    token=os.environ.get('QUORIVIO_CI_LOAD_TOKEN','')
    if len(token)<32:
        raise RuntimeError('capacity CI requires an ephemeral staging load token')
    from ci_live_http import client, call
    admin=client()
    call(admin,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
                                      'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
    session=call(admin,'POST','/api/sessions',{'title':'Disposable 500-participant capacity acceptance'},201)
    sid=session['id']
    try:
        cookie=next(c for c in next(handler.cookiejar for handler in admin.handlers if hasattr(handler,'cookiejar')) if c.name=='q_auth')
        call(admin,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
        # The presenter observer and all 500 independent cookie jars share this session.
        join_url=normalize_disposable_join_url(base, session['join_url'])
        with tempfile.TemporaryDirectory(prefix='quorivio-capacity-') as folder:
            output=Path(folder)/'shard.json'
            args=[sys.executable,'tools/load_500.py','--join-url',join_url,
                  '--session-id',sid,'--users','500','--ramp-seconds','40',
                  '--hold-seconds','90' if strict_slo else '35','--timeout','30','--load-token',token,
                  '--presenter-cookie',f'q_auth={cookie.value}', '--json-out',str(output)]
            if strict_slo:
                args.append('--latency-samples')
            # Suppress secrets from subprocess arguments and logs on failure.
            proc=subprocess.run(args,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,
                                text=True,timeout=240 if strict_slo else 180)
            if not output.exists():
                # Never echo raw argparse output: child CLI arguments can carry
                # a session QR bearer token and a presenter's auth cookie.
                reason = ('load simulator rejected its arguments' if proc.returncode == 2
                          and 'error:' in (proc.stderr or '')
                          else 'load simulator exited before recording a report')
                raise RuntimeError(f'capacity runner failed without report: {reason} '
                                   f'(exit {proc.returncode})')
            shards=[json.loads(output.read_text())]
            report=(reconcile_slo(shards,expected=500) if strict_slo
                    else reconcile(shards,expected=500))
            if proc.returncode or not report['pass']:
                raise RuntimeError(f'capacity acceptance failed: joins={report["anonymous_joins"]}, '
                                   f'websockets={report["websocket_completed"]}, '
                                   f'peak={report["presenter_peak_distinct"]}, '
                                   f'errors={report["reported_errors"]}')
            if strict_slo:
                print('PASS 500 independent participants; full-sample global join/snapshot p95 SLO, >=60s hold and no errors')
            else:
                print('PASS 500 independent participants, shared-session presenter peak >= 475, no errors')
    finally:
        call(admin,'DELETE',f'/api/sessions/{sid}',expected=204)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict-slo',action='store_true',help='Opt-in 90s hold and complete per-client percentile evidence')
    args=parser.parse_args()
    run(strict_slo=args.strict_slo)
