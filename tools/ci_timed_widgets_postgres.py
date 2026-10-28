#!/usr/bin/env python3
"""Disposable PostgreSQL CI: timed widget fairness, retries, and atomic topic cap.

Requires a loopback server, an explicit flag and an ephemeral staging load token.
This test does not touch real user accounts or externally accessible services.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from copy import copy
import http.cookiejar
import os
from datetime import datetime, timezone
import subprocess
import time
from urllib.parse import urlsplit
from ci_audience_moderation_postgres import request, visitor, BASE, TOKEN
from urllib.request import HTTPCookieProcessor, build_opener


def duplicate_client(original):
    jar = http.cookiejar.CookieJar()
    source = next(h.cookiejar for h in original.handlers if isinstance(h, HTTPCookieProcessor))
    for cookie in source:
        jar.set_cookie(copy(cookie))
    return build_opener(HTTPCookieProcessor(jar))


def duration_milliseconds(value: object) -> int:
    """Read node-postgres BIGINT as a lossless JSON decimal string.

    The source column elapsed_ms is PostgreSQL int8. The pg driver deliberately
    returns int8 as text, rather than rounding values to JS Number precision.
    """
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
        raise AssertionError(f'Expected decimal-string duration_ms from PostgreSQL int8, got {value!r}')
    parsed = int(value)
    if parsed > (2**63 - 1):
        raise AssertionError('PostgreSQL int8 duration_ms exceeds signed BIGINT range')
    return parsed

def run():
    address=urlsplit(BASE)
    if address.scheme != 'http' or address.hostname not in ('127.0.0.1','localhost') or not address.port:
        raise RuntimeError('Timed acceptance requires disposable loopback HTTP')
    if os.environ.get('QUORIVIO_CI_TIMED_TEST') != '1' or not TOKEN or len(TOKEN) < 32:
        raise RuntimeError('Timed acceptance requires explicit opt-in and ephemeral load token')
    admin=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    request(admin,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'], 'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
    session=request(admin,'POST','/api/sessions',{'title':'CI timed widget/atomic topic acceptance'},201)
    sid,code=session['id'],session['join_code']
    activity=request(admin,'POST',f'/api/sessions/{sid}/activities',{'title':'Timed widget and topic questions','type':'poll',
        'options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]},201)
    aid=activity['id']
    design={'widgets':[
        {'id':'timed1','kind':'timed-quiz','label':'Five-second test','answerMode':'single',
         'options':[{'id':'yes','label':'Correct'},{'id':'no','label':'Wrong'}], 'correctOptionId':'yes', 'durationSeconds':15},
        {'id':'topic1','kind':'topic-question','label':'Ask about this page','showNames':False},
        {'id':'topic-stats','kind':'results-button','label':'Question count','targetWidgetId':'topic1','resultsView':'table'},
    ]}
    patch=request(admin,'PATCH',f'/api/sessions/{sid}/activities/{aid}/design',
        {'page_design':design,'result_design':{},'expected_design_revision':1})
    assert patch['ok'] is True
    request(admin,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
    request(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/open',{})
    same=visitor(code,500)
    widget=f'/api/join/{code}/activities/{aid}/widgets/timed1/respond'
    topic=f'/api/join/{code}/activities/{aid}/topic-widgets/topic1/questions'
    request(same,'GET',f'/api/sessions/{sid}/activities/{aid}/widgets/timed1/timed-leaderboard',expected=401)
    # More HTTP workers than PostgreSQL's default pool: this would deadlock if
    # audience identity performed nested db.query while holding pool clients.
    def send_widget(n):
        return request(duplicate_client(same),'POST',widget,{'option_id':'yes'})
    with ThreadPoolExecutor(max_workers=12) as pool:
        submissions=list(pool.map(send_widget,range(12)))
    assert len(submissions)==12 and sum(not x['already_submitted'] for x in submissions)==1, submissions
    assert all(x['revision']==1 and x['ok'] for x in submissions)
    # Ten-question topic quota is atomic across the same identity and replicas.
    def send_topic(n):
        try:
            request(duplicate_client(same),'POST',topic,{'body':f'Question from concurrent request {n}'},201)
            return 201
        except AssertionError as err:
            if 'got 429' in str(err): return 429
            raise
    with ThreadPoolExecutor(max_workers=12) as pool:
        outcomes=list(pool.map(send_topic,range(12)))
    assert outcomes.count(201)==10 and outcomes.count(429)==2,outcomes
    page=request(admin,'GET',f'/api/sessions/{sid}/activities/{aid}/topic-widgets/topic1/questions?page=1')
    assert page['total']==10 and len(page['items'])==10
    stats=f'/api/sessions/{sid}/activities/{aid}/topic-widgets/topic1/stats'
    assert request(admin,'GET',stats)=={'total':10}
    request(same,'GET',stats,expected=401)
    request(admin,'GET',f'/api/sessions/{sid}/activities/{aid}/topic-widgets/no-such-widget/stats',expected=404)
    assert all(x['participant_name'] is None for x in page['items'])
    ranking=request(admin,'GET',f'/api/sessions/{sid}/activities/{aid}/widgets/timed1/timed-leaderboard')
    assert ranking['answers']==1 and ranking['correct']==1 and len(ranking['ranking'])==1, ranking
    # PostgreSQL BIGINT / int8 is serialized by node-postgres as a decimal
    # string, not a JSON number. Preserve that lossless API representation.
    initial_duration=ranking['ranking'][0]['duration_ms']
    assert duration_milliseconds(initial_duration)>=0, ranking
    assert all('participant_id' not in x for x in ranking['ranking'])
    # Confirm a retry of the original answer remains idempotent after expiry,
    # while a NEW answer arriving after expiry is rejected by PostgreSQL clock.
    # The API returns the authoritative PostgreSQL opening time. A fixed
    # sleep would be flaky under load and falsely report a timeout regression.
    opened_at=request(admin,'GET',f'/api/sessions/{sid}')['activities'][0]['opened_at']
    deadline=datetime.fromisoformat(opened_at.replace('Z','+00:00')).timestamp()+15
    # Create two more correct responses for a deterministic SQL tie fixture.
    second=visitor(code,502)
    third=visitor(code,503)
    request(second,'POST',widget,{'option_id':'yes'})
    request(third,'POST',widget,{'option_id':'yes'})
    pg_url=os.environ.get('DATABASE_URL','')
    if not pg_url.startswith('postgres://quorivio:ci-only-secret@127.0.0.1:5432/'):
        raise RuntimeError('Refusing to rewrite ranking times outside disposable CI database')
    sql=("UPDATE widget_answers SET elapsed_ms=CASE "
         "WHEN participant_id=(SELECT id FROM participants WHERE pseudonym='Q&A test participant 502' AND session_id='"+sid+"') THEN 1000 "
         "WHEN participant_id=(SELECT id FROM participants WHERE pseudonym='Q&A test participant 503' AND session_id='"+sid+"') THEN 1000 "
         "ELSE 2000 END "
         "WHERE session_id='"+sid+"' AND activity_id='"+aid+"' AND widget_id='timed1'")
    pg_env={**os.environ,'PGPASSWORD':'ci-only-secret'}
    subprocess.run(['psql','-X','-v','ON_ERROR_STOP=1','-h','127.0.0.1','-U','quorivio','-d','quorivio','-c',sql],
                   env=pg_env,capture_output=True,text=True,check=True)
    ranks=request(admin,'GET',f'/api/sessions/{sid}/activities/{aid}/widgets/timed1/timed-leaderboard')['ranking']
    assert [r['rank'] for r in ranks]==[1,1,3],ranks
    assert [duration_milliseconds(r['duration_ms']) for r in ranks]==[1000,1000,2000],ranks
    time.sleep(max(0,deadline-time.time()+0.25))
    already=request(duplicate_client(same),'POST',widget,{'option_id':'yes'})
    assert already['already_submitted'] is True and already['revision']==1
    newcomer=visitor(code,501)
    request(newcomer,'POST',widget,{'option_id':'yes'},expected=409)
    # Another timed activity validates the legacy endpoint's expiry behavior.
    legacy=request(admin,'POST',f'/api/sessions/{sid}/activities',{'title':'Legacy timed quiz',
        'type':'timed_quiz','options':[{'id':'yes','label':'Correct'},{'id':'no','label':'Wrong'}],
        'correct_option_id':'yes','duration_seconds':5},201)
    lid=legacy['id']
    request(admin,'POST',f'/api/sessions/{sid}/activities/{lid}/open',{})
    request(same,'POST',f'/api/join/{code}/respond',{'activity_id':lid,'option_id':'yes'})
    time.sleep(5.15)
    repeated=request(same,'POST',f'/api/join/{code}/respond',{'activity_id':lid,'option_id':'yes'})
    assert repeated=={'ok':True,'already_submitted':True},repeated
    request(newcomer,'POST',f'/api/join/{code}/respond',{'activity_id':lid,'option_id':'yes'},expected=409)
    old_rank=request(admin,'GET',f'/api/sessions/{sid}/activities/{lid}/timed-leaderboard')
    assert old_rank['correct']==1 and old_rank['ranking'][0]['rank']==1
    assert duration_milliseconds(old_rank['ranking'][0]['duration_ms'])>=0,old_rank
    # An old page may not accept topic submissions after switching activities.
    request(same,'POST',topic,{'body':'This page is no longer active'},expected=403)
    request(admin,'POST',f'/api/sessions/{sid}/status',{'status':'closed'})
    request(same,'POST',f'/api/join/{code}/respond',{'activity_id':lid,'option_id':'yes'},expected=404)
    print('PASS PostgreSQL timed widgets: 12-way idempotence/pool safety, 10-question concurrent topic quota, deterministic tied-rank fairness, presenter-only rankings, deadline retries, legacy quiz and page close')

if __name__=='__main__': run()
