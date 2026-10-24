#!/usr/bin/env python3
"""Opt-in, disposable PostgreSQL-backed 500-participant CI acceptance.

Never target public production. This uses the CI's ephemeral local API, generates
its own private session, and verifies the observer's shared-session peak.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from aggregate_load_500 import reconcile
from ci_live_http import client, call


def run():
    base=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
    if not (base.startswith('http://127.0.0.1:') or base.startswith('http://localhost:')):
        raise RuntimeError('capacity CI is restricted to disposable loopback APIs')
    token=os.environ.get('QUORIVIO_CI_LOAD_TOKEN','')
    if len(token)<32:
        raise RuntimeError('capacity CI requires an ephemeral staging load token')
    admin=client()
    call(admin,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
                                      'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
    session=call(admin,'POST','/api/sessions',{'title':'Disposable 500-participant capacity acceptance'},201)
    sid=session['id']
    try:
        cookie=next(c for c in next(handler.cookiejar for handler in admin.handlers if hasattr(handler,'cookiejar')) if c.name=='q_auth')
        call(admin,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
        # The presenter observer and all 500 independent cookie jars share this session.
        join_url=session['join_url']
        with tempfile.TemporaryDirectory(prefix='quorivio-capacity-') as folder:
            output=Path(folder)/'shard.json'
            args=[sys.executable,'tools/load_500.py','--join-url',join_url,
                  '--session-id',sid,'--users','500','--ramp-seconds','40',
                  '--hold-seconds','35','--timeout','30','--load-token',token,
                  '--presenter-cookie',f'q_auth={cookie.value}', '--json-out',str(output)]
            # Suppress secrets from subprocess arguments and logs on failure.
            proc=subprocess.run(args,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,
                                text=True,timeout=180)
            if not output.exists():
                raise RuntimeError(f'capacity runner failed without report (exit {proc.returncode})')
            report=reconcile([json.loads(output.read_text())],expected=500)
            if proc.returncode or not report['pass']:
                raise RuntimeError(f'capacity acceptance failed: joins={report["anonymous_joins"]}, '
                                   f'websockets={report["websocket_completed"]}, '
                                   f'peak={report["presenter_peak_distinct"]}, '
                                   f'errors={report["reported_errors"]}')
            print('PASS 500 independent participants, shared-session presenter peak >= 475, no errors')
    finally:
        call(admin,'DELETE',f'/api/sessions/{sid}',expected=204)


if __name__=='__main__':
    run()
