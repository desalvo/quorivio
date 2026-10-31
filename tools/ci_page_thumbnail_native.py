#!/usr/bin/env python3
"""Native browser acceptance for actual bundled React page-thumbnail reorder.

Three distinct pages are moved by genuine HTML DragEvent on Chromium, Firefox
and WebKit, and by keyboard fallback. A disposable in-memory fetch fixture
simulates lost acknowledgements AFTER committed writes, rejected PUTs and
reconciliation to the canonical order. No external HTTP or real data.

This is NOT physical touchscreen, manual pixel comparison or a PostgreSQL
multi-editor acceptance and must not be promoted as those release gates.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from ci_browser_editor import ACT, SES

ROOT=Path(__file__).resolve().parents[1]
ACTIVITIES=[{**ACT,'id':f'{i:08d}-0000-4000-8000-000000000001','title':f'RC69 page {i}'} for i in range(1,4)]
SNAPSHOT={'session':{**SES,'current_activity_id':None},'activities':ACTIVITIES,'results':[],'connected_participants':0}

# Local Response and fetch are mocked; all of the actual UI, event handlers,
# compiled React and browser native drag behavior remain production code.
FETCH='''() => {
 const state={snapshot:__SNAP__, writes:0, commitThenLose:true, rejectNext:false};
 window.__rc69=state;
 const values=new Map();
 Object.defineProperty(document,'cookie',{configurable:true,
  get:()=>values.get('cookie')||'',set:v=>values.set('cookie',String(v))});
 const storage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,String(v)),
  removeItem:k=>values.delete(k),clear:()=>values.clear()};
 Object.defineProperty(window,'localStorage',{configurable:true,get:()=>storage});
 Object.defineProperty(window,'sessionStorage',{configurable:true,get:()=>storage});
 const send=(data,status=200)=>new Response(JSON.stringify(data),
  {status,headers:{'Content-Type':'application/json'}});
 window.fetch=async (url,opts={})=>{
  const path=new URL(String(url),'https://fixture.invalid').pathname;
  const method=(opts.method||'GET').toUpperCase();
  if(path==='/api/auth/me')return send({id:'user-test',email:'test@example.org',nickname:'Test',role:'presenter'});
  if(path==='/api/auth/oidc/providers')return send({providers:[]});
  if(path==='/api/sessions')return send({items:[state.snapshot.session],total:1});
  if(path==='/api/sessions/'+state.snapshot.session.id+'/pages/order'&&method==='PUT'){
    state.writes++;
    if(state.rejectNext){state.rejectNext=false;return send({error:'conflict'},409)}
    const ids=JSON.parse(opts.body).activity_ids;
    if(ids.length!==3||new Set(ids).size!==3||ids.some(id=>!state.snapshot.activities.some(a=>a.id===id)))
      return send({error:'invalid'},422);
    state.snapshot.activities=ids.map(id=>state.snapshot.activities.find(a=>a.id===id));
    if(state.commitThenLose){state.commitThenLose=false;throw Error('CI synthetic committed response loss')}
    return send({ok:true});
  }
  if(path==='/api/sessions/'+state.snapshot.session.id)return send(state.snapshot);
  if(path==='/api/calendar'||path.endsWith('/assets')||path.endsWith('/presenter-profiles')||
    path.endsWith('/appointments')||path.endsWith('/schedule'))return send([]);
  return send([]);
 };
}'''.replace('__SNAP__',json.dumps(SNAPSHOT))

async def check(browser,engine:str,width:int,js:str,css:str)->None:
 page=await browser.new_page(viewport={'width':width,'height':940 if width>500 else 844})
 page.set_default_timeout(16000)
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 try:
  await page.set_content('<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><div id="root"></div></body></html>')
  await page.evaluate(FETCH)
  await page.add_style_tag(content=css)
  await page.add_script_tag(content=js,type='module')
  notice=page.get_by_role('dialog',name='Informativa cookie funzionali')
  await expect(notice).to_be_visible()
  await notice.get_by_role('button',name='Ho capito').click()
  await page.get_by_role('button',name='Apri sessione').first.click()
  card=page.locator('details').filter(has=page.get_by_text('Browser acceptance',exact=True))
  await card.locator('summary').click()
  await card.get_by_role('button',name='Apri sessione').click()
  await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
  sidebar=page.get_by_role('complementary',name='Miniature delle pagine')
  await expect(sidebar).to_be_visible()
  rows=sidebar.locator('.page-editor-thumb-row')
  await expect(rows).to_have_count(3)
  titles=lambda:sidebar.locator('.page-editor-preview-title')
  assert await titles().all_text_contents()==['RC69 page 1','RC69 page 2','RC69 page 3']
  # Perform an actual native drag/drop. It commits on the fake server and loses
  # the HTTP acknowledgment. The real React UI must discover the committed order.
  await rows.nth(0).drag_to(rows.nth(2),timeout=12000)
  await expect(sidebar.get_by_text('Ordine salvato e recuperato dal server')).to_be_visible()
  assert await titles().all_text_contents()==['RC69 page 2','RC69 page 3','RC69 page 1']
  assert (await page.evaluate('window.__rc69.writes'))==1
  # A rejected HTTP write must display the untouched canonical order.
  await page.evaluate('window.__rc69.rejectNext=true')
  await rows.nth(0).drag_to(rows.nth(2),timeout=12000)
  await expect(sidebar.get_by_text('Riordino non applicato: mostrato l’ordine effettivo del server')).to_be_visible()
  assert await titles().all_text_contents()==['RC69 page 2','RC69 page 3','RC69 page 1']
  assert (await page.evaluate('window.__rc69.writes'))==2
  # Accessible keyboard fallback moves page 3 ahead of page 2 and persists.
  await rows.nth(1).locator('.page-editor-thumb').focus()
  await page.keyboard.press('Alt+ArrowUp')
  await expect(sidebar.get_by_text('Ordine delle pagine salvato')).to_be_visible()
  assert await titles().all_text_contents()==['RC69 page 3','RC69 page 2','RC69 page 1']
  assert (await page.evaluate('window.__rc69.writes'))==3
  assert await rows.evaluate_all('(nodes)=>nodes.every(n=>n.draggable)')
  assert not errors,errors
  print(f'PASS RC69 {engine} {width}px native thumbnail DnD, lost PUT response reconciliation, rejection and keyboard persistence')
 finally:
  await page.close()

async def main()->None:
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--engines',nargs='+',choices=['chromium','firefox','webkit'],default=['chromium'])
 args=parser.parse_args()
 files=ROOT/'apps/web/dist/assets'
 js=next(files.glob('index-*.js'),None)
 css=next(files.glob('index-*.css'),None)
 if not js or not css:raise RuntimeError('Compile the production frontend with npm run build first')
 async with async_playwright() as pw:
  for engine in args.engines:
   opts={'headless':True}
   if engine=='chromium':opts.update(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
   browser=await getattr(pw,engine).launch(**opts)
   try:
    for width in (1440,390):await check(browser,engine,width,js.read_text(),css.read_text())
   finally:await browser.close()

if __name__=='__main__':asyncio.run(main())
