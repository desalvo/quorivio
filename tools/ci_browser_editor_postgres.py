#!/usr/bin/env python3
"""Real production frontend + PostgreSQL editor acceptance (manual browser_test).

Unlike ci_browser_editor.py, no route is mocked. Uses a disposable localhost
session and a browser cookie jar authenticated through the real API.
"""
import asyncio
import json
import os
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright, expect
from ci_editor_collaboration_fixtures import label_only_remote_patch
from ci_editor_context_tools import ensure_canvas_tools_open, click_canvas_tool, close_canvas_tools


BASE=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
assert urlsplit(BASE).hostname in ('127.0.0.1','localhost') and urlsplit(BASE).scheme=='http'
ART=Path(os.environ.get('QUORIVIO_BROWSER_ARTIFACT_DIR','/tmp/quorivio-browser-artifacts'))

def draft(label='Original'):
 return {'page_design':{'backgroundColor':'#FFFFFF','widgets':[
  {'id':'pg-first','kind':'text','label':label,'position':{'x':10,'y':10,'width':20,'height':20}},
  {'id':'pg-second','kind':'text','label':'Second','position':{'x':40,'y':35,'width':15,'height':15}},
  {'id':'pg-third','kind':'text','label':'Third','position':{'x':75,'y':70,'width':15,'height':10}}
 ]},'result_design':{}}

async def call(context,method,path,body=None,status=200):
 options={'data':body} if body is not None else {}
 response=await context.request.fetch(BASE+path,method=method,**options)
 assert response.status==status,(method,path,response.status,status,(await response.text())[:240])
 return await response.json() if (await response.body()) else None

async def open_editor(page,title):
 await page.goto(BASE+'/',wait_until='domcontentloaded')
 await page.get_by_role('button',name='Apri sessione').first.wait_for()
 notice=page.get_by_role('dialog',name='Informativa cookie funzionali')
 if await notice.is_visible():
  assert await notice.evaluate("element => element.matches(':modal')"), 'Functional cookie notice must be in the browser top layer'
  button=notice.get_by_role('button',name='Ho capito')
  visible_hit=await button.evaluate("""element => {
    const box=element.getBoundingClientRect(), viewport=window.visualViewport;
    const left=viewport?.offsetLeft ?? 0, top=viewport?.offsetTop ?? 0;
    const right=left+(viewport?.width ?? window.innerWidth);
    const bottom=top+(viewport?.height ?? window.innerHeight);
    const cx=box.left+box.width/2, cy=box.top+box.height/2;
    return box.width>0 && box.height>0 && cx>=left && cx<right && cy>=top && cy<bottom;
  }""")
  assert visible_hit, 'Cookie acknowledgement button must be inside the visual viewport before a real click'
  await button.click()
  await expect(notice).to_have_count(0)
 await page.get_by_role('button',name='Apri sessione').first.click()
 card=page.locator('details').filter(has=page.get_by_text(title,exact=True))
 await card.locator('summary').click()
 await card.get_by_role('button',name='Apri sessione').click()
 await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
 await expect(page.get_by_role('group',name='Canvas grafico widget')).to_be_visible()

async def edit_canvas_widget_title(canvas, title):
  """Edit through the visible, accessible widget menu (real pointer actions).

  The canvas title input is intentionally read-only and has pointer-events:none
  until edit mode. Clicking/double-clicking that input directly is intercepted
  by its draggable parent in Chromium. The production menu has a supported
  "Modifica titolo" action which enables the input without bypassing the UI.
  """
  item=canvas.first
  field=item.get_by_role('textbox',name='Titolo text')
  await expect(field).not_to_be_editable()
  await item.click(button='right',position={'x':12,'y':12})
  menu=item.get_by_role('group',name='Azioni widget text')
  await expect(menu).to_be_visible()
  await menu.get_by_role('button',name='Modifica titolo').click()
  await expect(menu).to_have_count(0)
  await expect(field).to_be_editable()
  await field.fill(title)
  await field.press('Enter')
  await expect(field).to_have_value(title)
  await expect(field).not_to_be_editable()

async def await_revision(context,sid,aid,minimum,attempts=55):
 """Wait for confirmed server-side persistence; do not assume a success toast."""
 for _ in range(attempts):
  state=await call(context,'GET',f'/api/sessions/{sid}')
  activity=next(x for x in state['activities'] if x['id']==aid)
  if activity['design_revision']>=minimum:return activity
  await asyncio.sleep(.2)
 raise AssertionError(f'Autosave did not persist revision {minimum} within deadline')

async def main():
 async with async_playwright() as pw:
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
  headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']} if os.environ.get('QUORIVIO_CI_LOAD_TOKEN') else {}
  context=await browser.new_context(viewport={'width':1440,'height':950},extra_http_headers=headers,accept_downloads=True)
  page=await context.new_page();page.set_default_timeout(12000)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  title='CI real PostgreSQL editor autosave acceptance'
  try:
   await call(context,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
   session=await call(context,'POST','/api/sessions',{'title':title},201)
   sid=session['id'];activity=await call(context,'POST',f'/api/sessions/{sid}/activities',{'title':'Real editor','type':'poll','options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]},201)
   aid=activity['id'];design_path=f'/api/sessions/{sid}/activities/{aid}/design'
   initialized=await call(context,'PATCH',design_path,draft());assert initialized['design_revision']==2
   await open_editor(page,title)
   editor=page.get_by_role('region',name='Editor grafico delle pagine')
   assert await editor.get_by_role('button',name='Esci',exact=True).count()==1
   assert await editor.locator('.editor-bottom-controls').count()==0
   widgets=page.locator('.widget-canvas-item');await expect(widgets).to_have_count(3)
   assert await widgets.evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')==[10,40,75]
   await widgets.first.focus();await page.keyboard.press('ArrowRight')
   assert await widgets.first.evaluate('(e)=>parseFloat(e.style.left)')==11
   saved=await await_revision(context,sid,aid,3)
   assert [w['position']['x'] for w in saved['page_design']['widgets']]==[11,40,75]
   await expect(editor.get_by_text('Salvato automaticamente')).to_be_visible()
   await open_editor(page,title)
   assert await widgets.first.evaluate('(e)=>parseFloat(e.style.left)')==11
   # Rename the current page through the thumbnail menu. No question options,
   # response history, or widget geometry may be overwritten by a title edit.
   await page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta').click()
   page.once('dialog',lambda dialog:asyncio.create_task(dialog.accept('Renamed browser slide')))
   await page.get_by_role('button',name='Rinomina pagina',exact=True).click()
   await expect(page.get_by_role('button',name='Mostra pagina 1: Renamed browser slide',exact=False)).to_be_visible()
   renamed=await call(context,'GET',f'/api/sessions/{sid}')
   renamed_activity=next(x for x in renamed['activities'] if x['id']==aid)
   assert renamed_activity['title']=='Renamed browser slide'
   assert renamed_activity['design_revision']==3
   assert renamed_activity['options']==[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]
   assert renamed_activity['page_design']['widgets'][0]['position']['x']==11
   await open_editor(page,title)
   # Concurrent presenter modifies another field while browser retains stale revision.
   remote_before=await call(context,'GET',f'/api/sessions/{sid}')
   remote_page=next(x for x in remote_before['activities'] if x['id']==aid)
   changed=label_only_remote_patch(remote_page,'pg-first','Remote collaborator')
   await call(context,'PATCH',design_path,changed)
   await widgets.first.focus();await page.keyboard.press('ArrowRight')
   await expect(editor.get_by_text('Conflitto di revisione')).to_be_visible(timeout=12000)
   stale=await call(context,'GET',f'/api/sessions/{sid}')
   current=next(x for x in stale['activities'] if x['id']==aid)
   assert current['design_revision']==4 and current['page_design']['widgets'][0]['label']=='Remote collaborator'
   await page.get_by_role('button',name='Confronta e riconcilia le modifiche').click()
   await expect(page.get_by_text('Nessun conflitto sui singoli campi')).to_be_visible()
   await page.get_by_role('button',name='Applica riconciliazione alla bozza').click()
   merged=await await_revision(context,sid,aid,5)
   assert merged['page_design']['widgets'][0]['label']=='Remote collaborator'
   assert merged['page_design']['widgets'][0]['position']['x']==12
   # Same-field concurrent collision requires explicit human decision.
   remote_design=json.loads(json.dumps(merged['page_design']));remote_design['widgets'][0]['label']='Remote second edit'
   remote_result=json.loads(json.dumps(merged['result_design']));remote_result['header']='Remote results heading'
   await call(context,'PATCH',design_path,{'page_design':remote_design,'result_design':remote_result,'expected_design_revision':5})
   await edit_canvas_widget_title(widgets,'Local second edit')
   await expect(editor.get_by_text('Conflitto di revisione')).to_be_visible(timeout=12000)
   await page.get_by_role('button',name='Confronta e riconcilia le modifiche').click()
   choice=page.get_by_role('combobox',name='Risolvi Widget pg-first · label')
   await expect(choice).to_be_visible();await expect(page.get_by_role('button',name='Applica riconciliazione alla bozza')).to_be_disabled()
   await choice.select_option('local')
   await page.get_by_role('button',name='Applica riconciliazione alla bozza').click()
   resolved=await await_revision(context,sid,aid,7)
   assert resolved['page_design']['widgets'][0]['label']=='Local second edit'
   assert resolved['result_design']['header']=='Remote results heading'
   # Export backup only in active thumbnail context, never as a persistent canvas footer.
   await page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta').click()
   async with page.expect_download() as download_info:
    await page.get_by_role('button',name='Esporta layout JSON').click()
   backup=json.loads(Path(await (await download_info.value).path()).read_text())
   assert backup['format']=='quorivio-local-draft-v2'
   assert backup['base_revision']==7
   await editor.get_by_role('button',name='Esci',exact=True).click()
   await expect(editor).to_have_count(0)
   assert not errors,errors
  except Exception:
   ART.mkdir(parents=True,exist_ok=True)
   try:
    await page.screenshot(path=str(ART/'real-editor-autosave-failure.png'),full_page=True,timeout=5000)
    (ART/'real-editor-autosave.html').write_text(await page.content(),encoding='utf-8')
    (ART/'real-editor-diagnostics.txt').write_text('URL: '+page.url+'\nJS errors: '+repr(errors)+'\n',encoding='utf-8')
   except Exception as e:print('Diagnostic capture failed:',e)
   raise
  finally:
   await context.close();await browser.close()
 print('PASS Chromium PostgreSQL editor: autosave PATCH and read-back, reload persistence, concurrent revision conflict and three-way merge, explicit same-field resolution and page JSON export')

if __name__=='__main__':asyncio.run(main())
