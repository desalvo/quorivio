#!/usr/bin/env python3
"""Chromium UI acceptance with deterministic API fixture; no production database needed."""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect

SESSION='11111111-1111-4111-8111-111111111111'
ACTIVITY='22222222-2222-4222-8222-222222222222'
WIDGETS=[{'id':'widget-a','kind':'text','label':'First','position':{'x':10,'y':10,'width':20,'height':20}}, {'id':'widget-b','kind':'text','label':'Second','position':{'x':40,'y':35,'width':15,'height':15}}, {'id':'widget-c','kind':'text','label':'Third','position':{'x':75,'y':70,'width':15,'height':10}}]
ACT={'id':ACTIVITY,'title':'Slide browser','type':'poll','status':'draft','options':[],'page_design':{'widgets':WIDGETS},'result_design':{}}
SES={'id':SESSION,'title':'Browser acceptance','reference_date':'2026-10-25','status':'draft','join_code':'ABCDEF','join_url':'/join/ABCDEF','current_activity_id':None,'retention_days':90,'allow_anonymous':True,'show_results':False}
SNAP={'session':SES,'activities':[ACT],'results':[],'connected_participants':0}
async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(**({'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}),headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1440,'height':1000})
  page.set_default_timeout(10000)
  errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  async def mock(route):
   from urllib.parse import urlparse
   path=urlparse(route.request.url).path
   if path=='/api/auth/me':data={'id':'user-test','email':'test@example.org','nickname':'Test','role':'presenter'}
   elif path=='/api/auth/oidc/providers':data={'providers':[]}
   elif path=='/api/sessions':data={'items':[SES],'total':1}
   elif path==f'/api/sessions/{SESSION}':data=SNAP
   elif path.endswith('/assets') or path.endswith('/presenter-profiles') or path.endswith('/appointments') or path.endswith('/schedule'):data=[]
   elif path=='/api/calendar':data=[]
   else:data=[]
   await route.fulfill(status=200,content_type='application/json',json=data)
  await page.route('**/api/**',mock)
  try:
    await page.goto(os.environ.get('QUORIVIO_WEB_URL','http://127.0.0.1:5173/'),wait_until='domcontentloaded')
    await page.get_by_role('button',name='Apri sessione').first.click()
    await page.get_by_text('Browser acceptance',exact=True).wait_for()
    # Expanding the session summary is not the same as opening its dashboard.
    session_card=page.locator('details').filter(has=page.get_by_text('Browser acceptance',exact=True))
    await session_card.locator('summary').click()
    await session_card.get_by_role('button',name='Apri sessione').click()
    await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
    await page.get_by_role('group',name='Canvas grafico widget').wait_for()
    await page.locator('.widget-canvas-item').first.click()
    await page.locator('.widget-canvas-item').nth(1).click(modifiers=['Shift'])
    assert await page.get_by_role('group',name='Allineamento widget selezionati').get_by_text('2 selezionati').count()==1
    await page.get_by_role('button',name='Sinistra',exact=True).click()
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[10,10],coords
    await page.keyboard.press('Control+z')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[10,40],coords
    await page.keyboard.press('Control+y')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[10,10],coords
    # A group paste must preserve both selected widgets, their spacing, and unique IDs.
    await page.get_by_role('button',name='Copia selezione').click()
    await page.get_by_role('button',name='Incolla selezione').click()
    assert await page.locator('.widget-canvas-item').count()==5
    pasted=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.slice(-2).map(e=>parseFloat(e.style.left))')
    assert pasted[1]-pasted[0]==0,pasted
    await page.keyboard.press('Control+z')
    assert await page.locator('.widget-canvas-item').count()==3
    # Undo removes the pasted widgets, so the selection must no longer contain
    # their now-orphaned IDs. Clicking a disabled Deseleziona button is not a
    # valid acceptance check: it waits until Playwright times out.
    selection=page.get_by_role('group',name='Allineamento widget selezionati')
    deselect=selection.get_by_role('button',name='Deseleziona')
    await expect(selection.get_by_text('0 selezionati')).to_be_visible()  # Undo clears orphaned IDs
    await expect(deselect).to_be_disabled()
    # Exercise the accessible widget list, then verify the real clear action.
    accessible=page.get_by_role('region',name='Organizzazione accessibile dei widget')
    checks=accessible.get_by_role('checkbox',name='Seleziona')
    assert await checks.count()==3
    await checks.nth(0).check()
    await checks.nth(1).check()
    await expect(selection.get_by_text('2 selezionati')).to_be_visible()
    await expect(deselect).to_be_enabled()
    await deselect.click()
    await expect(selection.get_by_text('0 selezionati')).to_be_visible()
    await expect(checks.nth(0)).not_to_be_checked()
    await expect(checks.nth(1)).not_to_be_checked()
    await expect(deselect).to_be_disabled()
    assert not errors,errors
  except Exception:
   # Disposable CI fixture only: capture enough context to diagnose failures
   # without guessing from a generic Playwright 30-second timeout.
   directory=Path(os.environ.get('QUORIVIO_BROWSER_ARTIFACT_DIR','/tmp/quorivio-browser-artifacts'))
   directory.mkdir(parents=True,exist_ok=True)
   try:
    await page.screenshot(path=str(directory/'failure.png'),full_page=True,timeout=5000)
    (directory/'failure.html').write_text(await page.content(),encoding='utf-8')
    (directory/'diagnostics.txt').write_text('URL: '+page.url+'\nPage errors: '+repr(errors)+'\n',encoding='utf-8')
   except Exception as capture_error:
    print('Browser diagnostic capture failed:',capture_error)
   print('Chromium acceptance failed at URL:',page.url,'page errors:',errors)
   raise
  finally:
   await browser.close()
  print('PASS Chromium editor: multi-selection, alignment, undo, redo, group paste, orphan cleanup, accessible selection, clear selection; no page errors')
if __name__=='__main__':asyncio.run(main())
