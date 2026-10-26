#!/usr/bin/env python3
"""Real PostgreSQL acceptance for Q&A concurrency, moderation and privacy.

Run only on an explicitly disposable loopback CI instance after provisioning the
CI administrator. Does not require a browser or access to external services.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import http.cookiejar
import json
import os
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, HTTPCookieProcessor, build_opener
from urllib.parse import urlsplit

BASE=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080').rstrip('/')
TOKEN=os.environ.get('QUORIVIO_CI_LOAD_TOKEN','')


def request(opener, method, path, data=None, expected=200):
    payload=json.dumps(data).encode() if data is not None else None
    headers={'Content-Type':'application/json'}
    if TOKEN: headers['X-Quorivio-Load-Token']=TOKEN
    req=Request(BASE+path,data=payload,method=method,headers=headers)
    try:
        with opener.open(req,timeout=25) as response:
            status,body=response.status,response.read()
    except HTTPError as error:
        status,body=error.code,error.read()
    assert status==expected, f'{method} {path}: expected {expected}, got {status}, body={body[:160]!r}'
    if not body:return None
    try:return json.loads(body)
    except json.JSONDecodeError:return None


def visitor(code,n):
    opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    request(opener,'POST',f'/api/join/{code}',{'pseudonym':f'Q&A test participant {n}'})
    return opener


def run():
    url=urlsplit(BASE)
    if url.scheme!='http' or url.hostname not in {'127.0.0.1','localhost'} or not url.port:
        raise RuntimeError('Moderation acceptance is restricted to disposable loopback HTTP')
    if os.environ.get('QUORIVIO_CI_MODERATION_TEST')!='1' or not TOKEN:
        raise RuntimeError('Moderation acceptance requires explicit CI flag and temporary load token')
    admin=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    request(admin,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
    session=request(admin,'POST','/api/sessions',{'title':'CI private moderation acceptance'},201)
    sid,code=session['id'],session['join_code']
    page=request(admin,'POST',f'/api/sessions/{sid}/activities',{'title':'CI Q&A','type':'poll','options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]},201)
    aid=page['id']
    api=f'/api/sessions/{sid}/activities/{aid}'
    pub=f'/api/join/{code}/activities/{aid}'
    request(admin,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
    request(admin,'POST',f'{api}/open',{})
    first=visitor(code,0)
    assert request(first,'GET',f'{pub}/questions')==[]
    request(first,'GET',f'{api}/questions/queue',expected=401)
    # Multiple requests from one participant on a shared session, as happens
    # with tabs and separate HTTP replicas, must never exceed three questions.
    def post_one(n):
        try:
            result=request(first,'POST',f'{pub}/questions',{'body':f'Concurrent Q&A request number {n}'},202)
            return 'accepted',result
        except AssertionError as error:
            if 'got 429' in str(error):return 'limited',None
            raise
    with ThreadPoolExecutor(max_workers=12) as pool:
        submitted=list(pool.map(post_one,range(12)))
    assert sum(key=='accepted' for key,_ in submitted)==3,submitted
    assert sum(key=='limited' for key,_ in submitted)==9,submitted
    initial=request(admin,'GET',f'{api}/questions/queue')
    assert initial['total']==3 and initial['counts']=={'pending':3,'approved':0,'rejected':0},initial
    assert request(first,'GET',f'{pub}/questions')==[]
    # A duplicate word is idempotent and must not overwrite the first value.
    assert request(first,'POST',f'{pub}/words',{'word':'  FAIR   Q&A '},202)=={'ok':True,'already_submitted':False}
    assert request(first,'POST',f'{pub}/words',{'word':'different'},202)=={'ok':True,'already_submitted':True}
    assert request(admin,'GET',f'{api}/words')==[{'word':'fair q&a','count':1}]
    # Grow beyond the historical 200 hard limit using bounded pages. 7 other
    # contributors bring us to 24, sufficient to test the pagination boundary.
    others=[visitor(code,n) for n in range(1,8)]
    def submit_many(args):
        participant,n=args
        for i in range(3):
            result=request(participant,'POST',f'{pub}/questions',{'body':f'Moderation queue record {n}-{i}'},202)
            assert result['status']=='pending_moderation'
    with ThreadPoolExecutor(max_workers=7) as pool:
        list(pool.map(submit_many,zip(others,range(1,8))))
    q1=request(admin,'GET',f'{api}/questions/queue?status=pending&page=1')
    q2=request(admin,'GET',f'{api}/questions/queue?status=pending&page=2')
    assert q1['total']==24 and q1['total_pages']==2 and len(q1['items'])==20,q1
    assert q2['total']==24 and len(q2['items'])==4,q2
    assert not set(x['id'] for x in q1['items'])&set(x['id'] for x in q2['items'])
    for invalid in ('status=published','page=0','page=-1','page=999999','page=1%20OR%201=1'):
        request(admin,'GET',f'{api}/questions/queue?{invalid}',expected=400)
    # Atomic bulk moderation: reject two pending records without touching
    # unrelated questions, and disallow malformed/duplicate selections.
    selected=[q2['items'][0]['id'],q2['items'][1]['id']]
    assert request(admin,'PATCH',f'{api}/questions/bulk',{'status':'rejected','ids':selected})=={'ok':True,'updated':2}
    assert request(admin,'GET',f'{api}/questions/queue?status=rejected')['total']==2
    assert request(admin,'GET',f'{api}/questions/queue?status=pending')['total']==22
    request(admin,'PATCH',f'{api}/questions/bulk',{'status':'pending','ids':selected},expected=400)
    request(admin,'PATCH',f'{api}/questions/bulk',{'status':'approved','ids':selected*2},expected=400)
    request(admin,'PATCH',f'{api}/questions/bulk',{'status':'approved','ids':[]},expected=400)
    target=q1['items'][0]
    request(admin,'PATCH',f'{api}/questions/{target["id"]}',{'status':'approved'})
    published=request(first,'GET',f'{pub}/questions')
    assert len(published)==1 and published[0]['id']==target['id'],published
    assert request(first,'POST',f'{pub}/questions/{target["id"]}/upvote',{},200)=={'ok':True,'already_voted':False}
    assert request(first,'POST',f'{pub}/questions/{target["id"]}/upvote',{},200)=={'ok':True,'already_voted':True}
    assert request(others[0],'POST',f'{pub}/questions/{target["id"]}/upvote',{},200)=={'ok':True,'already_voted':False}
    assert request(first,'GET',f'{pub}/questions')[0]['votes']==2
    approved=request(admin,'GET',f'{api}/questions/queue?status=approved&page=1')
    assert approved['total']==1 and approved['items'][0]['votes']==2 and approved['counts']['pending']==21
    # The presenter can reverse an approval; participants cannot read or vote
    # on rejected content, even after previously learning its opaque ID.
    request(admin,'PATCH',f'{api}/questions/{target["id"]}',{'status':'rejected'})
    assert request(first,'GET',f'{pub}/questions')==[]
    request(first,'POST',f'{pub}/questions/{target["id"]}/upvote',{},expected=404)
    rejected=request(admin,'GET',f'{api}/questions/queue?status=rejected')
    assert rejected['total']==3 and rejected['counts']['pending']==21
    request(admin,'PATCH',f'{api}/questions/{target["id"]}',{'status':'approved'})
    assert request(first,'GET',f'{pub}/questions')[0]['votes']==2
    # Isolation: another session cannot see or change these questions.
    unrelated=request(admin,'POST','/api/sessions',{'title':'Unrelated private moderator session'},201)
    empty=request(admin,'GET',f'/api/sessions/{unrelated["id"]}/activities/{aid}/questions/queue?status=all')
    assert empty['total']==0 and empty['items']==[]
    request(admin,'PATCH',f'/api/sessions/{unrelated["id"]}/activities/{aid}/questions/{target["id"]}',{'status':'rejected'},expected=404)
    request(admin,'PATCH',f'{api}/questions/bulk',{'status':'rejected','ids':[target['id'],'33333333-3333-4333-8333-333333333333']},expected=404)
    assert request(admin,'GET',f'{api}/questions/queue?status=approved')['total']==1
    request(admin,'POST',f'/api/sessions/{sid}/status',{'status':'closed'})
    request(first,'POST',f'{pub}/questions',{'body':'A closed page may not accept writes'},expected=403)
    request(first,'POST',f'{pub}/questions/{target["id"]}/upvote',{},expected=403)
    request(first,'GET',f'{pub}/questions',expected=404)
    print('PASS PostgreSQL audience moderation: 12 concurrent submissions/3 cap, 24 records, atomic bulk review, queue pagination, private pending/rejected content, reverse moderation, two-voter idempotency, word dedupe, isolation and closed-page rejection')


if __name__=='__main__':run()
