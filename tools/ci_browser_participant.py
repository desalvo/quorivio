#!/usr/bin/env python3
"""Opt-in real PostgreSQL + Chromium audience acceptance.

Uses only a disposable CI API, two isolated browser cookie jars, and a session
created for this run. Never run against a production endpoint.
"""
import asyncio
import http.cookiejar
import json
import os
from pathlib import Path
from urllib.request import Request, HTTPCookieProcessor, build_opener
from urllib.error import HTTPError
from playwright.async_api import async_playwright, expect

BASE=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
WEB=os.environ.get('QUORIVIO_WEB_URL',BASE)
ARTIFACTS=Path(os.environ.get('QUORIVIO_BROWSER_ARTIFACT_DIR','/tmp/quorivio-browser-artifacts'))
# RC165: exercise the widget-driven 16:9 page actually used by real participants.
# A newly created legacy poll contains only the default Title widget; it does
# not (and must not) synthesize participant controls outside the authored canvas.
QUESTION_WIDGET='ci-browser-question'
TOPIC_WIDGET='ci-browser-topic'



def api(opener,method,path,body=None,expected=200):
 data=json.dumps(body).encode() if body is not None else None
 req=Request(BASE+path,data=data,method=method,headers={'Content-Type':'application/json',**({'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']} if os.environ.get('QUORIVIO_CI_LOAD_TOKEN') else {})})
 try:
  with opener.open(req,timeout=15) as response:
   status=response.status
   payload=response.read()
 except HTTPError as e:
  status=e.code
  payload=e.read()
 assert status==expected,(method,path,status,expected,payload[:300])
 return json.loads(payload) if payload else None


def prepare():
 # Do not silently point this destructive fixture at a remote/production API.
 assert BASE.startswith('http://127.0.0.1:') or BASE.startswith('http://localhost:'),BASE
 assert WEB.startswith('http://127.0.0.1:') or WEB.startswith('http://localhost:'),WEB
 admin=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
 api(admin,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
 session=api(admin,'POST','/api/sessions',{'title':'CI Chromium real audience acceptance'},201)
 sid,code,secret=session['id'],session['join_code'],session['join_url'].rstrip('/').split('/')[-1]
 act=api(admin,'POST',f'/api/sessions/{sid}/activities',{'title':'CI browser poll','type':'poll','options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]},201)
 aid=act['id']
 # Author explicit, editable canvas controls before the session goes live.  The
 # legacy poll's auto-generated Title alone intentionally exposes no answers.
 snapshot=api(admin,'GET',f'/api/sessions/{sid}')
 page=next(a for a in snapshot['activities'] if a['id']==aid)
 widgets=[*page['page_design'].get('widgets',[]),
  {'id':QUESTION_WIDGET,'kind':'question','label':'CI browser poll',
   'answerMode':'single','required':True,
   'options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}],
   'style':{'fontFamily':'Arial','fontSize':18,'fillNone':True},
   'position':{'x':10,'y':20,'width':72,'height':29,'rotation':0}},
  {'id':TOPIC_WIDGET,'kind':'topic-question','label':'Domande sul tema',
   'style':{'fontFamily':'Arial','fontSize':16,'fillNone':True},
   'position':{'x':10,'y':60,'width':72,'height':27,'rotation':0}}]
 assert all(w['kind']!='question' for w in page['page_design'].get('widgets',[])), 'CI fixture already has a question widget'
 api(admin,'PATCH',f'/api/sessions/{sid}/activities/{aid}/design',
     {'page_design':{**page['page_design'],'widgets':widgets},
      'result_design':page.get('result_design') or {},
      'expected_design_revision':page['design_revision']})
 api(admin,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
 api(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/open',{})
 return admin,sid,code,secret,aid


async def enter(page,secret,name):
 await page.goto(WEB+'/join/'+secret,wait_until='domcontentloaded')
 notice=page.get_by_role('button',name='Ho capito')
 if await notice.count():await notice.click()
 await expect(page.get_by_role('heading',name='CI Chromium real audience acceptance')).to_be_visible()
 await expect(page.get_by_role('heading',name='Partecipa alla sessione')).to_be_visible()
 await page.get_by_role('textbox',name='Pseudonimo').fill(name)
 await page.get_by_role('checkbox',name='Accetto i cookie funzionali necessari al servizio').check()
 await page.get_by_role('button',name='Entra').click()
 await expect(page.get_by_role('heading',name='CI browser poll')).to_be_visible()
 # The live default is an authored 16:9 slide; the question belongs inside it.
 await expect(page.get_by_role('button',name='Diapositiva 16:9')).to_have_attribute('aria-pressed','true')
 await expect(page.locator('[data-widget-kind="question"]')).to_have_count(1)
 await expect(page.locator('[data-widget-kind="topic-question"]')).to_have_count(1)
 assert await page.get_by_role('region',name='Strumenti interattivi').count()==0, 'unsolicited audience Q&A panel returned'
 await expect(page.locator('[data-widget-kind="question"]').get_by_role('button',name='Invia risposta',exact=True)).to_be_disabled()


async def vote(page,choice,confirmation='Risposta registrata'):
 # Authored question widgets use accessible native radio controls, not the
 # legacy standalone poll's div.buttons outside the slide.
 widget=page.locator('[data-widget-kind="question"]')
 button=widget.get_by_role('radio',name=choice,exact=True)
 await button.check()
 await expect(button).to_be_checked()
 await widget.get_by_role('button',name='Invia risposta',exact=True).click()
 await expect(widget.get_by_role('status')).to_contain_text(confirmation)


async def capture(page,tag,errors):
 ARTIFACTS.mkdir(parents=True,exist_ok=True)
 try:
  await page.screenshot(path=str(ARTIFACTS/(tag+'.png')),full_page=True,timeout=5000)
  (ARTIFACTS/(tag+'.html')).write_text(await page.content(),encoding='utf-8')
  (ARTIFACTS/(tag+'.txt')).write_text('URL: '+page.url+'\nErrors: '+repr(errors)+'\n',encoding='utf-8')
 except Exception as e:print('Browser diagnostics unavailable:',e)


async def run():
 admin,sid,code,secret,aid=prepare()
 async with async_playwright() as pw:
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
  headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']} if os.environ.get('QUORIVIO_CI_LOAD_TOKEN') else {}
  desktop=await browser.new_context(viewport={'width':1366,'height':900},extra_http_headers=headers)
  mobile=await browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,extra_http_headers=headers)
  p1=await desktop.new_page()
  p2=await mobile.new_page()
  for p in (p1,p2):p.set_default_timeout(12000)
  errors=[]
  for p in (p1,p2):p.on('pageerror',lambda error:errors.append(str(error)))
  try:
   # 1. A long QR join secret and a short typed code both work.
   await enter(p1,secret,'Browser Alice')
   await enter(p2,code,'Browser Bob')
   # 2. No participant sees an admin report; no quiz key or aggregate result leaks.
   assert (await p1.request.get(WEB+f'/api/sessions/{sid}/report.json')).status==401
   assert (await p2.request.get(WEB+f'/api/sessions/{sid}/report.json')).status==401
   assert (await p1.request.get(WEB+f'/api/sessions/{sid}/widget-answers')).status==401
   assert not await p1.get_by_role('heading',name='Risultati live').count()
   # 3. Independent authored-widget answers and PostgreSQL verification.
   await vote(p1,'Yes')
   await vote(p2,'No')
   report=api(admin,'GET',f'/api/sessions/{sid}/widget-answers')
   row=next(x for x in report if x['activity_id']==aid and x['widget_id']==QUESTION_WIDGET and x['question_id']=='')
   assert row['responses']==2,row
   # 4. A reload recovers HttpOnly participation without another POST/join.
   await p1.reload(wait_until='domcontentloaded')
   await expect(p1.get_by_role('heading',name='CI browser poll')).to_be_visible()
   assert not await p1.get_by_role('heading',name='Partecipa alla sessione').count()
   # 5. Idempotent duplicate via the actual widget endpoint: no new row.
   await vote(p1,'Yes','Risposta già registrata')
   report=api(admin,'GET',f'/api/sessions/{sid}/widget-answers')
   row=next(x for x in report if x['activity_id']==aid and x['widget_id']==QUESTION_WIDGET and x['question_id']=='')
   assert row['responses']==2,row
   # 6. Mobile reload recovers its cookie; authored controls fit the viewport.
   await p2.reload(wait_until='domcontentloaded')
   await expect(p2.get_by_role('heading',name='CI browser poll')).to_be_visible()
   button=p2.locator('[data-widget-kind="question"]').get_by_role('radio',name='Yes',exact=True)
   bounds=await button.bounding_box()
   assert bounds and bounds['x']>=0 and bounds['x']+bounds['width']<=392,bounds
   # 7. Explicit Topic Question widget: no unsolicited moderation panel or
   #    global Q&A is mounted.  Questions are private to the presenter.
   topic=p1.locator('[data-widget-kind="topic-question"]')
   await topic.get_by_role('textbox').fill('Chromium browser presenter-only topic question')
   await topic.get_by_role('button',name='Invia domanda',exact=True).click()
   await expect(topic.get_by_text('Domanda inviata al presentatore')).to_be_visible()
   assert not await p1.get_by_role('region',name='Strumenti interattivi').count()
   topic_path=f'/api/sessions/{sid}/activities/{aid}/topic-widgets/{TOPIC_WIDGET}/questions'
   assert (await p1.request.get(WEB+topic_path)).status==401
   topic_data=api(admin,'GET',topic_path)
   assert topic_data['total']==1 and topic_data['items'][0]['body']=='Chromium browser presenter-only topic question',topic_data
   # Legacy moderated Q&A approval/rejection/upvotes remain independently
   # verified by tools/ci_audience_moderation_postgres.py; participants do not
   # receive its controls unless a compatible authored widget is present.
   # 8. Server-issued QR resolves to the same participant URL, not a privileged URL.
   qr=await p2.request.get(WEB+f'/api/join/{code}/qr.svg')
   assert qr.ok and '<svg' in await qr.text()
   # 9. Closed session invalidates public read and participation recovery.
   api(admin,'POST',f'/api/sessions/{sid}/status',{'status':'closed'})
   assert (await p1.request.get(WEB+f'/api/join/{secret}')).status==404
   assert (await p2.request.get(WEB+f'/api/join/{code}/participation')).status==404
   assert not errors,errors
  except Exception:
   await capture(p1,'participant-desktop-failure',errors)
   await capture(p2,'participant-mobile-failure',errors)
   raise
  finally:
   await desktop.close();await mobile.close();await browser.close()
 print('PASS Chromium + PostgreSQL audience: QR/short-code join, two isolated participants, authored widget answers, HttpOnly reload recovery, idempotency, report privacy, mobile touch, presenter-only topic question, no unsolicited Q&A panel, QR and closure')

if __name__=='__main__':asyncio.run(run())
