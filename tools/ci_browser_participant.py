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
from urllib.parse import urlsplit
from urllib.error import HTTPError
from playwright.async_api import async_playwright, expect

BASE=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
WEB=os.environ.get('QUORIVIO_WEB_URL',BASE)
ARTIFACTS=Path(os.environ.get('QUORIVIO_BROWSER_ARTIFACT_DIR','/tmp/quorivio-browser-artifacts'))
# RC165: exercise the widget-driven 16:9 page actually used by real participants.
# A newly created legacy poll contains only the default Title widget; it does
# not (and must not) synthesize participant controls outside the authored canvas.
QUESTION_WIDGET='ci-browser-question'
RATING_WIDGET='ci-browser-rating'
TOPIC_WIDGET='ci-browser-topic'
GRAPHIC_LINE='ci-browser-line'
GRAPHIC_SHAPE='ci-browser-shape'
PRESENTER_CHART='ci-browser-presenter-result'
PRESENTER_COUNT='ci-browser-presenter-count'
FOOTER_WIDGET='ci-browser-footer'



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
 assert status==expected, f'disposable API {method}: HTTP {status}, expected {expected}; paths and response payload intentionally suppressed'
 return json.loads(payload) if payload else None


def validate_disposable_origin(value):
 # Prefix tests are unsafe: http://127.0.0.1:8080@external.example/ also
 # starts with the literal loopback prefix, but its actual host is external.
 try:
  parsed=urlsplit(value)
  port=parsed.port
 except (TypeError,ValueError) as exc:
  raise ValueError('CI browser fixture requires a well-formed loopback origin') from exc
 if (parsed.scheme!='http' or parsed.hostname not in ('localhost','127.0.0.1')
     or port is None or not (1<=port<=65535) or parsed.username or parsed.password
     or parsed.path not in ('','/') or parsed.query or parsed.fragment):
  raise ValueError('CI browser fixture is restricted to disposable loopback origins')
 return f'http://{parsed.hostname}:{port}'


def prepare():
 # Validate the parsed hostname before ANY mutating API request.
 validate_disposable_origin(BASE)
 validate_disposable_origin(WEB)
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
  # A real, customized rating must match editor/rehearsal: exactly one
  # comment textarea, authored description, ten buttons and a 24px choice size.
  {'id':RATING_WIDGET,'kind':'rating','label':'Gradimento CI','description':'Descrizione del gradimento CI',
   'style':{'fontFamily':'Arial','fontSize':20,'ratingButtonSize':24,'fillNone':True},
   'position':{'x':81,'y':48,'width':18,'height':34,'rotation':0}},
  {'id':TOPIC_WIDGET,'kind':'topic-question','label':'Domande sul tema',
   'style':{'fontFamily':'Arial','fontSize':16,'fillNone':True},
   'position':{'x':10,'y':60,'width':72,'height':27,'rotation':0}},
  # Deliberately include legacy graphic labels/showTitle=True.  The real
  # participant must render only SVG, just like preview and the editor.
  {'id':GRAPHIC_LINE,'kind':'line','label':'CI_PRIVATE_LINE_CAPTION','showTitle':True,
   'style':{'strokeColor':'#334155','strokeWidth':3,'strokeDash':'dash'},
   'position':{'x':10,'y':51,'width':72,'height':4,'rotation':0}},
  {'id':GRAPHIC_SHAPE,'kind':'shape','label':'CI_PRIVATE_SHAPE_CAPTION','showTitle':True,
   'style':{'shapeType':'circle','fillColor':'#dbeafe','strokeWidth':2},
   'position':{'x':86,'y':65,'width':12,'height':12,'rotation':0}},
  # Presenter-only widgets must not leave even blank background rectangles in
  # the participant DOM; rehearsal uses the exact same visibility policy.
  {'id':PRESENTER_CHART,'kind':'results-button','label':'Presenter chart','targetWidgetId':QUESTION_WIDGET,
   'position':{'x':86,'y':10,'width':12,'height':10,'rotation':0}},
  {'id':PRESENTER_COUNT,'kind':'participant-count','label':'Presenter count',
   'position':{'x':86,'y':35,'width':12,'height':10,'rotation':0}},
  # The mobile footer must occupy the actual bottom of the *visible* document,
  # not the bottom of a taller document that reserves presenter-only tools.
  {'id':FOOTER_WIDGET,'kind':'footer','label':'',
   'footerShowSessionTitle':True,'footerShowPageNumber':True,
   'style':{'fontFamily':'Arial','fontSize':14,'fillNone':True},
   'position':{'x':0,'y':93,'width':100,'height':7,'rotation':0}}]
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
 await expect(page.locator('[data-widget-kind="rating"]')).to_have_count(1)
 rating=page.locator('[data-widget-kind="rating"]')
 await expect(rating.locator('textarea.rating-comment-input')).to_have_count(1)
 await expect(rating.get_by_text('Descrizione del gradimento CI')).to_be_visible()
 await expect(rating.get_by_role('button',name='Vota 9 su 9')).to_have_count(1)
 assert await rating.locator('.rating-choice-buttons>button').count()==10, 'the authored 0–9 scale differs from the preview'
 rating_view=await rating.evaluate('''el=>{
   const comment=el.querySelector('textarea.rating-comment-input');
   const appearance=getComputedStyle(comment);
   return {background:appearance.backgroundColor,color:appearance.color,
           title:getComputedStyle(el).fontSize,
           buttonSize:el.querySelector('.rating-choice-buttons').style.getPropertyValue('--rating-font-size')};
 }''')
 assert rating_view['background']=='rgb(255, 255, 255)' and rating_view['color']=='rgb(20, 43, 68)', 'rating comment contrast differs from editor'
 assert rating_view['buttonSize']=='1.5em', 'rating buttons ignored the authored size'

 # Both graphic SVGs must survive, without a textual label even for old
 # authored widgets whose saved showTitle flag was true.
 await expect(page.locator('[data-widget-kind="line"] svg.widget-graphic-line')).to_have_count(1)
 await expect(page.locator('[data-widget-kind="shape"] svg.widget-graphic-shape')).to_have_count(1)
 assert await page.get_by_text('CI_PRIVATE_LINE_CAPTION').count()==0, 'graphic line caption leaked'
 assert await page.get_by_text('CI_PRIVATE_SHAPE_CAPTION').count()==0, 'graphic shape caption leaked'
 await expect(page.locator('[data-widget-kind="line"]')).to_have_attribute('data-show-title','false')
 await expect(page.locator('[data-widget-kind="shape"]')).to_have_attribute('data-show-title','false')
 assert not await page.locator('[data-widget-kind="results-button"], [data-widget-kind="participant-count"]').count(), 'presenter-only widget shell visible to audience'
 assert await page.get_by_role('region',name='Strumenti interattivi').count()==0, 'unsolicited audience Q&A panel returned'
 await expect(page.locator('[data-widget-kind="footer"]')).to_have_count(1)
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
  await page.screenshot(path=str(ARTIFACTS/(tag+'.png')),full_page=True,timeout=5000,
                        mask=[page.locator('.participant-access-qr')])
  # Authenticated URLs contain a bearer join token.  A full DOM or raw
  # browser error may also contain session cookies or private Q&A contents.
  # Retain only counts and a fixed scenario label in downloadable CI artifacts.
  (ARTIFACTS/(tag+'.txt')).write_text(
      f'Fixture: disposable participant browser\nPage errors (count only): {len(errors)}\n',
      encoding='utf-8')
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
   # RC176: Faithful 16:9 is the exact same authored coordinate system,
   # regardless of browser width. Test the real joined React pages at desktop
   # and 390px before switching modes (not merely a static stylesheet).
   async def normalized_slide_geometry(page):
    return await page.locator('.audience-widget-layout.stage-fidelity').evaluate('''stage=>{
      const canvas=stage.getBoundingClientRect();
      const result={width:canvas.width,height:canvas.height,widgets:{}};
      for(const kind of ['question','rating','topic-question','footer']){
       const widget=stage.querySelector(`[data-widget-kind="${kind}"]`);
       if(!widget)continue;
       const box=widget.getBoundingClientRect();
       result.widgets[kind]=[(box.left-canvas.left)/canvas.width,
         (box.top-canvas.top)/canvas.height,box.width/canvas.width,box.height/canvas.height];
      }
      const field=stage.querySelector('[data-widget-kind="rating"] textarea.rating-comment-input');
      result.commentHeight=field?.getBoundingClientRect().height ?? 0;
      return result;
    }''')
   desktop_slide=await normalized_slide_geometry(p1)
   mobile_slide=await normalized_slide_geometry(p2)
   assert abs(desktop_slide['width']/desktop_slide['height']-16/9)<.025
   assert abs(mobile_slide['width']/mobile_slide['height']-16/9)<.025
   assert desktop_slide['widgets'].keys()==mobile_slide['widgets'].keys()
   for kind,dimensions in desktop_slide['widgets'].items():
    other=mobile_slide['widgets'][kind]
    assert all(abs(a-b)<.025 for a,b in zip(dimensions,other)), f'16:9 {kind} coordinates drift at 390px'
   assert desktop_slide['commentHeight']>0 and mobile_slide['commentHeight']>0
   # The tiny faithful controls can only be considered accessible in the
   # separate reading mode. Never force a 44px minimum on the faithful slide.
   assert mobile_slide['commentHeight']<desktop_slide['commentHeight']*.65, '16:9 response field did not scale'

   # RC176: the three views are different products. Phone is the authored
   # 390 logical-pixel document; reading mode is a neutral-flow document.
   # Previous RC165--175 fixture wrongly clicked "Lettura accessibile" and
   # expected stage-phone, so it could not certify either of the two modes.
   await p2.get_by_role('button',name='Layout smartphone').click()
   await expect(p2.locator('.audience-widget-layout.stage-phone')).to_have_count(1)
   geometry=await p2.locator('.audience-widget-layout.stage-phone').evaluate('''stage=>{
     const sr=stage.getBoundingClientRect(),footer=stage.querySelector('[data-widget-kind="footer"]');
     const fr=footer?.getBoundingClientRect();
     const publicWidgets=[...stage.querySelectorAll(':scope>.page-widget')];
     const kinds=publicWidgets.map(w=>w.dataset.widgetKind);
     // RC217: measure only rendered PUBLIC widgets. The RC207 44px touch
     // rows legitimately increased the question from 248px to 278px; a
     // literal 998px fixture height became obsolete. Extra hidden presenter
     // widgets still increase stage height and MUST fail this invariant.
     const ordered=publicWidgets.map(w=>w.getBoundingClientRect()).sort((a,b)=>a.top-b.top);
     const expectedHeight=16+ordered.reduce((sum,r)=>sum+r.height,0)+Math.max(0,ordered.length-1)*8+16;
     const topGap=ordered.length?ordered[0].top-sr.top:null;
     const gaps=ordered.slice(1).map((r,i)=>r.top-ordered[i].bottom);
     const question=stage.querySelector('[data-widget-kind="question"]');
     return {height:sr.height,expectedHeight,topGap,gaps,
             questionHeight:question?.getBoundingClientRect().height??0,
             footerOffset:fr?sr.bottom-fr.bottom:null,kinds};
   }''')
   # The phone stage must exactly contain its public content: top/bottom
   # margins of 16px, 8px between widgets, and no phantom presenter widgets.
   # Derive the height from visible DOM geometry, not a frozen count from a
   # previous typography version. Long answers can legitimately grow further.
   assert len(geometry['kinds'])==7, 'public phone fixture lost or gained a widget'
   assert geometry['questionHeight']>=278-1, 'RC207 readable question rows shrank'
   assert abs(geometry['height']-geometry['expectedHeight'])<2, 'public phone stage reserves invisible presenter widgets'
   assert geometry['topGap'] is not None and abs(geometry['topGap']-16)<2, 'phone stage top margin drifted'
   assert all(abs(gap-8)<2 for gap in geometry['gaps']), 'phone stage contains phantom vertical gaps'
   assert 10<=geometry['footerOffset']<=20, 'footer does not finish the public phone document'
   assert geometry['kinds'].count('footer')==1
   assert not {'results-button','participant-count'}.intersection(geometry['kinds'])
   number=await p2.locator('.stage-phone .slide-canvas-page-number').evaluate('''el=>{
     const stage=el.closest('.stage-phone'),r=el.getBoundingClientRect(),box=stage.getBoundingClientRect();
     return {font:parseFloat(getComputedStyle(el).fontSize),right:box.right-r.right,bottom:box.bottom-r.bottom};
   }''')
   assert abs(number['font']-14)<.5 and abs(number['right']-5)<1.2 and abs(number['bottom']-5)<1.2, 'phone footer-number typography/insets diverged'

   await p2.get_by_role('button',name='Lettura accessibile').click()
   await expect(p2.locator('.audience-widget-layout.stage-reading')).to_have_count(1)
   reading=await p2.locator('.audience-widget-layout.stage-reading').evaluate('''stage=>{
     const kinds=[...stage.querySelectorAll(':scope>.page-widget')].map(w=>w.dataset.widgetKind);
     const background=getComputedStyle(stage);
     const field=stage.querySelector('[data-widget-kind="rating"] textarea.rating-comment-input');
     const fieldStyle=field?getComputedStyle(field):null;
     return {kinds,backgroundImage:background.backgroundImage,backgroundColor:background.backgroundColor,
       fieldMinHeight:fieldStyle?.minHeight,fieldHeight:field?.getBoundingClientRect().height ?? 0};
   }''')
   assert reading['backgroundImage']=='none' and reading['backgroundColor']=='rgb(255, 255, 255)', 'accessible document inherited the slide background'
   assert reading['kinds'][-1]=='footer', 'footer must be last in the DOM reading order'
   assert not {'shape','line','results-button','participant-count'}.intersection(reading['kinds']), 'decorative/private widgets leaked into accessible reading order'
   assert reading['fieldHeight']>=44, 'accessible response field must remain usable at phone width'
   await p2.get_by_role('button',name='Diapositiva 16:9').click()
   await expect(p2.locator('.audience-widget-layout.stage-fidelity')).to_have_count(1)

   await p1.get_by_role('button',name='Lettura accessibile').click()
   await expect(p1.locator('.audience-widget-layout.stage-reading')).to_have_count(1)
   kinds=await p1.locator('.stage-reading>.page-widget').evaluate_all('(items)=>items.map(w=>w.dataset.widgetKind)')
   assert kinds[-1]=='footer' and kinds.index('question')<kinds.index('topic-question'), 'desktop accessible DOM reading order diverged'
   await p1.get_by_role('button',name='Diapositiva 16:9').click()
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
   assert not errors, f'{len(errors)} browser page error(s) (details intentionally suppressed)'
  except Exception:
   await capture(p1,'participant-desktop-failure',errors)
   await capture(p2,'participant-mobile-failure',errors)
   raise
  finally:
   await desktop.close();await mobile.close();await browser.close()
 print('PASS Chromium + PostgreSQL audience: QR/short-code join, two isolated participants, authored widget answers, HttpOnly reload recovery, idempotency, report privacy, mobile touch, presenter-only topic question, no unsolicited Q&A panel, QR and closure')

if __name__=='__main__':asyncio.run(run())
