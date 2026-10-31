#!/usr/bin/env python3
"""Disposable PostgreSQL/HTTP acceptance for RC71, no production URLs/secrets.

Verifies the irreversible boundary and page clock against the actual API,
not a mock: first opening, navigation, restart, repeat answers and reset.
"""
import os
import time
from ci_http_isolation import ci_load_headers
from ci_background_library_postgres import req, session, HOST


def run():
    ci_load_headers(HOST)  # rejects non-loopback host or absent short-lived CI token
    admin = session()
    req(admin, 'POST', '/api/auth/login', {
        'email': os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
        'password': os.environ['QUORIVIO_CI_NEW_PASSWORD']})
    created = req(admin, 'POST', '/api/sessions', {'title': 'RC71 disposable lifecycle'}, 201)
    sid, code = created['id'], created['join_code']
    activity = req(admin, 'POST', f'/api/sessions/{sid}/activities', {
        'title': 'Page with countdown', 'type': 'poll',
        'options': [{'id':'yes','label':'Yes'}, {'id':'no','label':'No'}]}, 201)
    aid = activity['id']
    page = {'widgets': [
        {'id':'timer71','kind':'timer','label':'Duration','durationSeconds':90},
        {'id':'reaction71','kind':'reactions','label':'Reactions','reactionIconSize':48},
        {'id':'profile71','kind':'profile','label':'Presenter','description':'Example biography'}]}
    req(admin,'PATCH',f'/api/sessions/{sid}/activities/{aid}/design',{
        'page_design':page,'result_design':{},'expected_design_revision':1})
    qr = req(admin,'GET',f'/api/sessions/{sid}/presenter-qr')
    assert isinstance(qr,bytes) and b'<svg' in qr and b'<svg' not in code.encode()
    req(admin,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
    req(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/open',{})
    initial = next(a for a in req(admin,'GET',f'/api/sessions/{sid}')['activities'] if a['id']==aid)['opened_at']
    assert initial
    audience = session()
    req(audience,'POST',f'/api/join/{code}',{'pseudonym':'RC71 participant'})
    req(audience,'POST',f'/api/join/{code}/respond',{'activity_id':aid,'option_id':'yes'})
    # Visiting a different page then returning cannot extend the clock.
    other = req(admin,'POST',f'/api/sessions/{sid}/activities',{
        'title':'Other page','type':'poll',
        'options':[{'id':'a','label':'A'}, {'id':'b','label':'B'}]},201)['id']
    req(admin,'POST',f'/api/sessions/{sid}/activities/{other}/open',{})
    req(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/open',{})
    revisit=next(a for a in req(admin,'GET',f'/api/sessions/{sid}')['activities'] if a['id']==aid)
    assert revisit['opened_at']==initial
    # A selected keep operation renews the clock without deleting earlier votes.
    req(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/restart-timer',{},expected=400)
    req(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/restart-timer',{'confirmation':'RESTART_PAGE_TIMER'},expected=400)
    time.sleep(1.1)
    req(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/restart-timer',{'confirmation':'RESTART_PAGE_TIMER','clear_responses':False})
    retained=req(admin,'GET',f'/api/sessions/{sid}')
    assert sum(int(x['count']) for x in retained['results'] if x['activity_id']==aid)==1
    # Explicit clear removes the previous answers and permits a new vote.
    time.sleep(1.1)
    req(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/restart-timer',{'confirmation':'RESTART_PAGE_TIMER','clear_responses':True})
    restarted=req(admin,'GET',f'/api/sessions/{sid}')
    later=next(a for a in restarted['activities'] if a['id']==aid)['opened_at']
    assert later!=initial and sum(x['count'] for x in restarted['results'] if x['activity_id']==aid)==0
    req(audience,'POST',f'/api/join/{code}/respond',{'activity_id':aid,'option_id':'no'})
    req(admin,'POST',f'/api/sessions/{sid}/reset-to-ready',{},expected=400)
    req(admin,'POST',f'/api/sessions/{sid}/reset-to-ready',{'confirmation':'RESET_SESSION_RESULTS'})
    reset=req(admin,'GET',f'/api/sessions/{sid}')
    assert reset['session']['status']=='ready' and reset['session']['current_activity_id'] is None
    assert reset['session']['join_code']!=code
    assert reset['results']==[] and all(a['status']=='pending' and a['opened_at'] is None for a in reset['activities'])
    assert next(a for a in reset['activities'] if a['id']==aid)['page_design']['widgets']==page['widgets']
    req(audience,'POST',f'/api/join/{code}/respond',{'activity_id':aid,'option_id':'yes'},expected=404)
    print('PASS disposable PostgreSQL RC71: one-shot first timer, preserved revisit, confirmed restart, re-answer, owner-only reset, cleared stats and persistent design')

if __name__=='__main__':
    run()
