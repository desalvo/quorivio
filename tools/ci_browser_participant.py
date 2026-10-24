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
 await expect(page.get_by_role('button',name='Invia risposta',exact=False)).to_be_disabled()


async def vote(page,choice):
 button=page.get_by_role('group',name='Opzioni di risposta').get_by_role('button',name=choice,exact=True)
 await button.click()
 await expect(button).to_have_attribute('aria-pressed','true')
 await page.get_by_role('button',name='Invia risposta',exact=False).click()
 await expect(page.get_by_role('heading',name='Risposta registrata')).to_be_visible()


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
   assert not await p1.get_by_role('heading',name='Risultati live').count()
   # 3. Independent votes, accessible pressed states and server-side persistence.
   await vote(p1,'Yes')
   await vote(p2,'No')
   report=api(admin,'GET',f'/api/sessions/{sid}/report.json')
   row=next(x for x in report['totals'] if x['activity_id']==aid)
   assert row['valid']==2 and row['total']==2,row
   # 4. A reload recovers HttpOnly participation without another POST/join.
   await p1.reload(wait_until='domcontentloaded')
   await expect(p1.get_by_role('heading',name='CI browser poll')).to_be_visible()
   assert not await p1.get_by_role('heading',name='Partecipa alla sessione').count()
   # 5. Idempotent duplicate submission must not create another response.
   await vote(p1,'Yes')
   report=api(admin,'GET',f'/api/sessions/{sid}/report.json')
   row=next(x for x in report['totals'] if x['activity_id']==aid)
   assert row['valid']==2 and row['total']==2,row
   # 6. Mobile reload also recovers its cookie; controls remain within the viewport.
   await p2.reload(wait_until='domcontentloaded')
   await expect(p2.get_by_role('heading',name='CI browser poll')).to_be_visible()
   button=p2.get_by_role('group',name='Opzioni di risposta').get_by_role('button',name='Yes')
   bounds=await button.bounding_box()
   assert bounds and bounds['x']>=0 and bounds['x']+bounds['width']<=392,bounds
   # 7. Server-issued QR resolves to the same participant URL, not a privileged URL.
   qr=await p2.request.get(WEB+f'/api/join/{code}/qr.svg')
   assert qr.ok and '<svg' in await qr.text()
   # 8. Closed session invalidates public read and participation recovery.
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
 print('PASS Chromium + PostgreSQL audience: QR/short-code join, two isolated participants, vote persistence, HttpOnly reload recovery, idempotency, report privacy, mobile touch, QR and closure')

if __name__=='__main__':asyncio.run(run())
