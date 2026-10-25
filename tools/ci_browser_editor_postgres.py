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
 await page.get_by_role('button',name='Apri sessione').first.click()
 card=page.locator('details').filter(has=page.get_by_text(title,exact=True))
 await card.locator('summary').click()
 await card.get_by_role('button',name='Apri sessione').click()
 await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
 await expect(page.get_by_role('group',name='Canvas grafico widget')).to_be_visible()

async def main():
 async with async_playwright() as pw:
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
  headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']} if os.environ.get('QUORIVIO_CI_LOAD_TOKEN') else {}
  context=await browser.new_context(viewport={'width':1440,'height':1000},extra_http_headers=headers)
  page=await context.new_page();page.set_default_timeout(12000)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  title='CI real PostgreSQL editor browser acceptance'
  try:
   await call(context,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
   s=await call(context,'POST','/api/sessions',{'title':title},201)
   sid=s['id'];act=await call(context,'POST',f'/api/sessions/{sid}/activities',{'title':'Real editor','type':'poll','options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]},201)
   aid=act['id'];path=f'/api/sessions/{sid}/activities/{aid}/design'
   first=await call(context,'PATCH',path,draft())
   assert first['design_revision']==2
   await open_editor(page,title)
   canvas=page.locator('.widget-canvas-item')
   await expect(canvas).to_have_count(3)
   assert await canvas.evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')==[10,40,75]
   # Keyboard accessible multi-selection and deterministic group translation.
   region=page.get_by_role('region',name='Organizzazione accessibile dei widget')
   checks=region.get_by_role('checkbox',name='Seleziona')
   await checks.nth(0).check();await checks.nth(1).check()
   await page.get_by_role('button',name='Sposta selezione a destra').click()
   assert (await canvas.evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))'))[:2]==[11,41]
   await page.get_by_role('button',name='Salva layout').click()
   await expect(page.get_by_text('Layout domanda e risultati aggiornato')).to_be_visible()
   persisted=await call(context,'GET',f'/api/sessions/{sid}')
   saved=next(x for x in persisted['activities'] if x['id']==aid)
   assert saved['design_revision']==3 and [w['position']['x'] for w in saved['page_design']['widgets'][:2]]==[11,41]
   await open_editor(page,title)
   assert (await canvas.evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))'))[:2]==[11,41]
   # Simulate a collaborator saving after the editor loaded, without intercepting HTTP.
   collaborator=await call(context,'PATCH',path,{**draft('Remote collaborator'),'expected_design_revision':3})
   assert collaborator['design_revision']==4
   region=page.get_by_role('region',name='Organizzazione accessibile dei widget')
   await region.get_by_role('checkbox',name='Seleziona').first.check()
   await page.get_by_role('button',name='Sposta selezione a destra').click()
   await page.get_by_role('button',name='Salva layout').click()
   await expect(page.get_by_role('alert').filter(has_text='Un altro presentatore')).to_be_visible()
   await expect(page.get_by_role('button',name='Salva layout')).to_be_disabled()
   assert (await call(context,'GET',f'/api/sessions/{sid}'))['activities'][0]['page_design']['widgets'][0]['label']=='Remote collaborator'
   # Safe three-way merge: remote label + local coordinate are independent.
   await page.get_by_role('button',name='Confronta e riconcilia le modifiche').click()
   await expect(page.get_by_text('Nessun conflitto sui singoli campi')).to_be_visible()
   await page.get_by_role('button',name='Applica riconciliazione alla bozza').click()
   await expect(page.get_by_role('alert').filter(has_text='Un altro presentatore')).to_have_count(0)
   await expect(page.get_by_role('button',name='Salva layout')).to_be_enabled()
   # Rebase is strictly local until an explicit save; the server is still revision 4.
   before_save=await call(context,'GET',f'/api/sessions/{sid}')
   current=next(x for x in before_save['activities'] if x['id']==aid)
   assert current['design_revision']==4 and current['page_design']['widgets'][0]['position']['x']==11
   await page.get_by_role('button',name='Salva layout').click()
   await expect(page.get_by_text('Layout domanda e risultati aggiornato')).to_be_visible()
   merged=await call(context,'GET',f'/api/sessions/{sid}')
   current=next(x for x in merged['activities'] if x['id']==aid)
   assert current['design_revision']==5
   assert current['page_design']['widgets'][0]['label']=='Remote collaborator'
   assert current['page_design']['widgets'][0]['position']['x']==12
   # Both presenters now edit the SAME label: explicit resolution is required.
   remote_design=json.loads(json.dumps(current['page_design']))
   remote_design['widgets'][0]['label']='Remote second edit'
   remote_result=json.loads(json.dumps(current['result_design']))
   remote_result['header']='Remote results heading'
   await call(context,'PATCH',path,{'page_design':remote_design,'result_design':remote_result,'expected_design_revision':5})
   await canvas.first.locator('input').fill('Local second edit')
   await page.get_by_role('button',name='Salva layout').click()
   await expect(page.get_by_role('alert').filter(has_text='Un altro presentatore')).to_be_visible()
   await page.get_by_role('button',name='Confronta e riconcilia le modifiche').click()
   choice=page.get_by_role('combobox',name='Risolvi Widget pg-first · label')
   await expect(choice).to_be_visible()
   await expect(page.get_by_role('button',name='Applica riconciliazione alla bozza')).to_be_disabled()
   await choice.select_option('local')
   await page.get_by_role('button',name='Applica riconciliazione alla bozza').click()
   await page.get_by_role('button',name='Salva layout').click()
   resolved=await call(context,'GET',f'/api/sessions/{sid}')
   current=next(x for x in resolved['activities'] if x['id']==aid)
   assert current['design_revision']==7
   assert current['page_design']['widgets'][0]['label']=='Local second edit'
   assert current['result_design']['header']=='Remote results heading'
   # Destructive recovery remains available and must be explicitly confirmed.
   remote_design=json.loads(json.dumps(current['page_design']))
   remote_design['widgets'][0]['label']='Remote final edit'
   await call(context,'PATCH',path,{'page_design':remote_design,'result_design':current['result_design'],'expected_design_revision':7})
   await canvas.first.locator('input').fill('Local final edit')
   await page.get_by_role('button',name='Salva layout').click()
   await expect(page.get_by_role('alert').filter(has_text='Un altro presentatore')).to_be_visible()
   page.once('dialog',lambda d:asyncio.create_task(d.dismiss()))
   await page.get_by_role('button',name='Ricarica layout dal server').click()
   await expect(page.get_by_role('alert').filter(has_text='Un altro presentatore')).to_be_visible()
   page.once('dialog',lambda d:asyncio.create_task(d.accept()))
   await page.get_by_role('button',name='Ricarica layout dal server').click()
   await expect(page.get_by_role('alert').filter(has_text='Un altro presentatore')).to_have_count(0)
   await expect(page.get_by_role('button',name='Salva layout')).to_be_disabled()
   assert await page.locator('.widget-canvas-item').first.locator('input').input_value()=='Remote final edit'
   # User-initiated local backup: no persistent browser storage and no implicit PATCH.
   await canvas.first.locator('input').fill('Restored from local JSON')
   async with page.expect_download() as download_info:
    await page.get_by_role('button',name='Esporta bozza JSON').click()
   download=await download_info.value
   backup=json.loads(Path(await download.path()).read_text())
   assert backup['format']=='quorivio-local-draft-v2'
   assert backup['base_revision']==8
   assert backup['base_draft']['widgets'][0]['label']=='Remote final edit'
   assert backup['draft']['widgets'][0]['label']=='Restored from local JSON'
   await canvas.first.locator('input').fill('Discarded temporary local edit')
   page.once('dialog',lambda d:asyncio.create_task(d.accept()))
   await page.locator('.page-draft-import input').set_input_files({'name':'recovery.json','mimeType':'application/json','buffer':json.dumps(backup).encode()})
   await expect(canvas.first.locator('input')).to_have_value('Restored from local JSON')
   assert (await call(context,'GET',f'/api/sessions/{sid}'))['activities'][0]['design_revision']==8
   # A newer remote revision forces three-way recovery; never silently overwrite.
   latest=await call(context,'GET',f'/api/sessions/{sid}')
   activity=next(x for x in latest['activities'] if x['id']==aid)
   changed=json.loads(json.dumps(activity['page_design']))
   changed['widgets'][0]['label']='Newer remote value'
   await call(context,'PATCH',path,{'page_design':changed,'result_design':activity['result_design'],'expected_design_revision':8})
   page.once('dialog',lambda d:asyncio.create_task(d.accept()))
   await page.locator('.page-draft-import input').set_input_files({'name':'recovery.json','mimeType':'application/json','buffer':json.dumps(backup).encode()})
   await expect(page.get_by_role('heading',name='Riconciliazione con la versione server 9')).to_be_visible()
   choice=page.get_by_role('combobox',name='Risolvi Widget pg-first · label')
   await choice.select_option('local')
   await page.get_by_role('button',name='Applica riconciliazione alla bozza').click()
   assert (await call(context,'GET',f'/api/sessions/{sid}'))['activities'][0]['design_revision']==9
   await page.get_by_role('button',name='Salva layout').click()
   final=await call(context,'GET',f'/api/sessions/{sid}')
   final_page=next(x for x in final['activities'] if x['id']==aid)
   assert final_page['design_revision']==10
   assert final_page['page_design']['widgets'][0]['label']=='Restored from local JSON'
   assert not errors,errors
  except Exception:
   ART.mkdir(parents=True,exist_ok=True)
   try:
    await page.screenshot(path=str(ART/'real-editor-failure.png'),full_page=True,timeout=5000)
    (ART/'real-editor-failure.html').write_text(await page.content(),encoding='utf-8')
    (ART/'real-editor-diagnostics.txt').write_text('URL: '+page.url+'\nJS errors: '+repr(errors)+'\n',encoding='utf-8')
   except Exception as e:print('Diagnostic capture failed:',e)
   raise
  finally:
   await context.close();await browser.close()
 print('PASS Chromium + PostgreSQL editor: real cookie auth, canvas group editing, actual database PATCH/reload, concurrent revision conflict, safe three-way merge, explicit field resolution, preserved draft, v2 JSON backup/import and stale-backup three-way recovery')

if __name__=='__main__':asyncio.run(main())
