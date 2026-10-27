#!/usr/bin/env python3
"""Chromium UI acceptance with deterministic API fixture; no production database needed."""
import asyncio
import copy
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from ci_editor_context_tools import ensure_canvas_tools_open, click_canvas_tool
from ci_editor_context_tools import editor_save_button

SESSION='11111111-1111-4111-8111-111111111111'
ACTIVITY='22222222-2222-4222-8222-222222222222'
WIDGETS=[{'id':'widget-a','kind':'text','label':'First','position':{'x':10,'y':10,'width':20,'height':20}}, {'id':'widget-b','kind':'text','label':'Second','position':{'x':40,'y':35,'width':15,'height':15}}, {'id':'widget-c','kind':'text','label':'Third','position':{'x':75,'y':70,'width':15,'height':10}}]
ACT={'id':ACTIVITY,'title':'Slide browser','type':'poll','status':'draft','options':[],'page_design':{'widgets':WIDGETS},'result_design':{}}
SES={'id':SESSION,'title':'Browser acceptance','reference_date':'2026-10-25','status':'draft','join_code':'ABCDEF','join_url':'/join/ABCDEF','current_activity_id':None,'retention_days':90,'allow_anonymous':True,'show_results':False}
SNAP={'session':SES,'activities':[ACT],'results':[],'connected_participants':0}
async def acknowledge_functional_cookie_notice(page):
    """Dismiss the real accessible notice, without bypassing pointer checks.

    A fresh browser context has no q_cookie_notice cookie; the fixed-position
    notice can overlap editor controls after the canvas has been opened.
    """
    notice=page.get_by_role('dialog',name='Informativa cookie funzionali')
    await expect(notice).to_be_visible()
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

async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(**({'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}),headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1440,'height':1000})
  page.set_default_timeout(10000)
  errors=[]
  state={'widgets':copy.deepcopy(WIDGETS),'saves':0}
  page.on('pageerror',lambda error:errors.append(str(error)))
  async def mock(route):
   from urllib.parse import urlparse
   path=urlparse(route.request.url).path
   if path==f'/api/sessions/{SESSION}/activities/{ACTIVITY}/design' and route.request.method=='PATCH':
    payload=route.request.post_data_json
    state['widgets']=copy.deepcopy(payload['page_design']['widgets'])
    state['saves']+=1
    data={'ok':True}
   elif path=='/api/auth/me':data={'id':'user-test','email':'test@example.org','nickname':'Test','role':'presenter'}
   elif path=='/api/auth/oidc/providers':data={'providers':[]}
   elif path=='/api/sessions':data={'items':[SES],'total':1}
   elif path==f'/api/sessions/{SESSION}':data={**SNAP,'activities':[{**ACT,'page_design':{'widgets':copy.deepcopy(state['widgets'])}}]}
   elif path.endswith('/assets') or path.endswith('/presenter-profiles') or path.endswith('/appointments') or path.endswith('/schedule'):data=[]
   elif path=='/api/calendar':data=[]
   else:data=[]
   await route.fulfill(status=200,content_type='application/json',json=data)
  await page.route('**/api/**',mock)
  try:
    await page.goto(os.environ.get('QUORIVIO_WEB_URL','http://127.0.0.1:5173/'),wait_until='domcontentloaded')
    await page.get_by_role('button',name='Apri sessione').first.wait_for()
    await acknowledge_functional_cookie_notice(page)
    await page.get_by_role('button',name='Apri sessione').first.click()
    await page.get_by_text('Browser acceptance',exact=True).wait_for()
    # Expanding the session summary is not the same as opening its dashboard.
    session_card=page.locator('details').filter(has=page.get_by_text('Browser acceptance',exact=True))
    await session_card.locator('summary').click()
    await session_card.get_by_role('button',name='Apri sessione').click()
    await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
    await page.get_by_role('group',name='Canvas grafico widget').wait_for()
    # Thumbnail context actions are available with mouse, keyboard and touch, without a permanent action strip.
    thumb_menu=page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta')
    await thumb_menu.click()
    actions=page.get_by_role('group',name='Azioni pagina 1')
    await expect(actions.get_by_role('button',name='Nuova pagina prima')).to_be_visible()
    await expect(actions.get_by_role('button',name='Nuova pagina dopo')).to_be_visible()
    await expect(actions.get_by_role('button',name='Duplica pagina')).to_be_visible()
    await expect(actions.get_by_role('button',name='Elimina pagina')).to_be_visible()
    # Regression from CI 40382686414: with only one slide the last-row CSS
    # must not place the contextual menu over its own toggle button.
    # Assert the browser's real hit target, not merely an accessible locator.
    can_close=await thumb_menu.evaluate("""button => {
      const r=button.getBoundingClientRect();
      const hit=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
      return hit===button || button.contains(hit);
    }""")
    assert can_close, 'Open thumbnail menu intercepts its own trigger in Chromium'
    await thumb_menu.click()
    await expect(actions).to_have_count(0)
    icon=page.get_by_role('button',name='Aggiungi widget: Testo')
    await icon.hover()
    await expect(page.get_by_role('tooltip').filter(has_text='Aggiungi widget: Testo')).to_be_visible()
    # The ribbon was removed: arrangement tools are available only via the canvas context.
    await page.locator('.canvas-accessible-controls > summary').click()
    await page.locator('.widget-canvas-item').first.click()
    await page.locator('.widget-canvas-item').nth(1).click(modifiers=['Shift'])
    await ensure_canvas_tools_open(page)
    assert await page.get_by_role('group',name='Allineamento widget selezionati').get_by_text('2 selezionati').count()==1
    await click_canvas_tool(page,'Sinistra')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[10,10],coords
    await page.keyboard.press('Control+z')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[10,40],coords
    await page.keyboard.press('Control+y')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[10,10],coords
    # A group paste must preserve both selected widgets, their spacing, and unique IDs.
    await click_canvas_tool(page,'Copia selezione')
    await click_canvas_tool(page,'Incolla selezione')
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
    await ensure_canvas_tools_open(page)
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
    await ensure_canvas_tools_open(page)
    await deselect.click()
    await expect(selection.get_by_text('0 selezionati')).to_be_visible()
    await expect(checks.nth(0)).not_to_be_checked()
    await expect(checks.nth(1)).not_to_be_checked()
    await expect(deselect).to_be_disabled()
    # A dismissed canvas menu hides commands, but the same selection remains
    # available after reopening it. Never depend on accidental persistent menus.
    await ensure_canvas_tools_open(page)
    context_trigger=page.get_by_role('button',name='Apri menu contestuale canvas, sfondi e proprietà pagina')
    await context_trigger.click()
    await expect(selection).to_be_hidden()
    await ensure_canvas_tools_open(page)
    # Regression CI 40392423273: nested layering controls must be exposed
    # when the canvas context opens, not suppressed by the parent's CSS.
    layer_group=page.get_by_role('group',name='Ordine e spostamento widget selezionati')
    await expect(layer_group).to_be_visible()
    await expect(layer_group.get_by_role('button',name='Porta selezione davanti')).to_be_visible()
    # Stable z-order operations must preserve selected relative order and undo.
    await checks.nth(0).check()
    await checks.nth(1).check()
    await click_canvas_tool(page,'Porta selezione davanti')
    order=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>e.querySelector("input")?.value)')
    assert order==['Third','First','Second'],order
    await page.keyboard.press('Control+z')
    order=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>e.querySelector("input")?.value)')
    assert order==['First','Second','Third'],order
    # Accessible toolbar group nudging, duplication, deletion and undo.
    await checks.nth(0).check()
    await checks.nth(1).check()
    await click_canvas_tool(page,'Sposta selezione a destra')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[11,11],coords  # Earlier redo aligned these two widgets.
    await page.keyboard.press('Control+z')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[10,10],coords
    await checks.nth(0).check()
    await checks.nth(1).check()
    await click_canvas_tool(page,'Duplica selezione')
    assert await page.locator('.widget-canvas-item').count()==5
    await page.keyboard.press('Control+z')
    assert await page.locator('.widget-canvas-item').count()==3
    await ensure_canvas_tools_open(page)
    await expect(selection.get_by_text('0 selezionati')).to_be_visible()
    await checks.nth(0).check()
    await checks.nth(1).check()
    await click_canvas_tool(page,'Elimina selezione')
    assert await page.locator('.widget-canvas-item').count()==1
    await page.keyboard.press('Control+z')
    assert await page.locator('.widget-canvas-item').count()==3
    # Browser-to-API persistence contract: PATCH stores the layout; reload restores it.
    await checks.nth(0).check()
    await checks.nth(1).check()
    await click_canvas_tool(page,'Sposta selezione a destra')
    await editor_save_button(page).click()
    await expect(page.get_by_text('Layout domanda e risultati aggiornato')).to_be_visible()
    await expect(editor_save_button(page)).to_be_disabled()
    assert state['saves']==1,state
    assert [w['position']['x'] for w in state['widgets'][:2]]==[11,11],state['widgets']
    await page.reload(wait_until='domcontentloaded')
    await expect(page.get_by_role('dialog',name='Informativa cookie funzionali')).to_have_count(0)
    await page.get_by_role('button',name='Apri sessione').first.click()
    session_card=page.locator('details').filter(has=page.get_by_text('Browser acceptance',exact=True))
    await session_card.locator('summary').click()
    await session_card.get_by_role('button',name='Apri sessione').click()
    await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[11,11],coords
    # Keyboard-only editing on the saved document: multi-selection is retained
    # while arrows move the group; Delete removes it; both operations undo.
    await page.locator('.canvas-accessible-controls > summary').click()
    accessible=page.get_by_role('region',name='Organizzazione accessibile dei widget')
    checks=accessible.get_by_role('checkbox',name='Seleziona')
    await checks.nth(0).check()
    await checks.nth(1).check()
    await page.locator('.widget-canvas-item').first.focus()
    await page.keyboard.press('ArrowRight')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[12,12],coords
    await page.keyboard.press('Control+z')
    coords=await page.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
    assert coords[:2]==[11,11],coords
    await page.locator('.widget-canvas-item').first.focus()
    await page.keyboard.press('Delete')
    assert await page.locator('.widget-canvas-item').count()==1
    await page.keyboard.press('Control+z')
    assert await page.locator('.widget-canvas-item').count()==3
    # Responsive/touch-capable viewport smoke: accessible selection and toolbar
    # remain usable on a phone-sized Chromium viewport (not a device lab).
    mobile=await browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    mobile.set_default_timeout(10000)
    await mobile.route('**/api/**',mock)
    try:
     await mobile.goto(os.environ.get('QUORIVIO_WEB_URL','http://127.0.0.1:5173/'),wait_until='domcontentloaded')
     await mobile.get_by_role('button',name='Apri sessione').first.wait_for()
     await acknowledge_functional_cookie_notice(mobile)
     await mobile.get_by_role('button',name='Apri sessione').first.click()
     card=mobile.locator('details').filter(has=mobile.get_by_text('Browser acceptance',exact=True))
     await card.locator('summary').click()
     await card.get_by_role('button',name='Apri sessione').click()
     await mobile.get_by_role('button',name='✎ Modifica le pagine').first.click()
     await expect(mobile.get_by_role('group',name='Canvas grafico widget')).to_be_visible()
     # The thumbnail menu must open AND close on touch without covering its trigger.
     mobile_thumb=mobile.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta')
     await mobile_thumb.tap()
     mobile_actions=mobile.get_by_role('group',name='Azioni pagina 1')
     await expect(mobile_actions.get_by_role('button',name='Nuova pagina dopo')).to_be_visible()
     assert await mobile_thumb.evaluate("""b=>{const r=b.getBoundingClientRect();const h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return h===b||b.contains(h)}"""), 'Touch thumbnail menu overlays its own trigger'
     await mobile_thumb.tap()
     await expect(mobile_actions).to_have_count(0)
     await ensure_canvas_tools_open(mobile)
     # CI 40510491774: at phone width the open alignment popover extended
     # beyond the 16:9 canvas and intercepted the accessibility disclosure.
     # A real pointer must be able to open the disclosure even while the
     # context menu is visible; opening it must dismiss that menu.
     summary=mobile.locator('.canvas-accessible-controls > summary')
     assert await summary.evaluate('el=>{const r=el.getBoundingClientRect();const hit=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);return hit===el||el.contains(hit)}'), 'Mobile accessibility summary covered by canvas context actions'
     await summary.tap()
     await expect(mobile.get_by_role('group',name='Allineamento widget selezionati')).to_be_hidden()
     mchecks=mobile.get_by_role('region',name='Organizzazione accessibile dei widget').get_by_role('checkbox',name='Seleziona')
     await mchecks.nth(0).check()
     await mchecks.nth(1).check()
     await click_canvas_tool(mobile,'Sposta selezione a sinistra')
     mcoords=await mobile.locator('.widget-canvas-item').evaluate_all('(els)=>els.map(e=>parseFloat(e.style.left))')
     assert mcoords[:2]==[10,10],mcoords
    except Exception:
     directory=Path(os.environ.get('QUORIVIO_BROWSER_ARTIFACT_DIR','/tmp/quorivio-browser-artifacts'))
     directory.mkdir(parents=True,exist_ok=True)
     try:
      await mobile.screenshot(path=str(directory/'mobile-failure.png'),full_page=True,timeout=5000)
      (directory/'mobile-failure.html').write_text(await mobile.content(),encoding='utf-8')
     except Exception as capture_error:
      print('Mobile diagnostic capture failed:',capture_error)
     raise
    finally:
     await mobile.close()
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
  print('PASS Chromium editor: multi-selection, alignment, undo/redo, group paste, accessible selection, layer order, group nudge/duplicate/delete, PATCH persistence/reload and keyboard group editing and mobile/touch viewport; no page errors')
if __name__=='__main__':asyncio.run(main())
