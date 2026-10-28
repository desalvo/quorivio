#!/usr/bin/env python3
"""Chromium UI acceptance with deterministic API fixture; no production database needed."""
import asyncio
import copy
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from ci_editor_context_tools import ensure_canvas_tools_open, click_canvas_tool, open_canvas_context, canvas_background_point
from ci_editor_context_tools import wait_for_editor_sync

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
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1440,'height':940},accept_downloads=True)
  page.set_default_timeout(12000)
  state={'widgets':copy.deepcopy(WIDGETS),'revision':1,'saves':0,'drop_before':False,'drop_after':False}
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  async def mock(route):
   from urllib.parse import urlparse
   path=urlparse(route.request.url).path
   if path==f'/api/sessions/{SESSION}/activities/{ACTIVITY}/design' and route.request.method=='PATCH':
    # Exercise both ambiguous transport outcomes against the real React UI:
    # an unsuccessful request, then a committed write with a lost response.
    if state['drop_before']:
     state['drop_before']=False
     await route.abort('failed');return
    payload=route.request.post_data_json
    if payload.get('expected_design_revision')!=state['revision']:
     await route.fulfill(status=409,content_type='application/json',json={'error':'design_revision_conflict'});return
    state['widgets']=copy.deepcopy(payload['page_design']['widgets']);state['revision']+=1;state['saves']+=1
    if state['drop_after']:
     state['drop_after']=False
     await route.abort('failed');return
    data={'ok':True,'design_revision':state['revision']}
   elif path=='/api/auth/me':data={'id':'user-test','email':'test@example.org','nickname':'Test','role':'presenter'}
   elif path=='/api/auth/oidc/providers':data={'providers':[]}
   elif path=='/api/sessions':data={'items':[SES],'total':1}
   elif path==f'/api/sessions/{SESSION}':data={**SNAP,'activities':[{**ACT,'design_revision':state['revision'],'page_design':{'widgets':copy.deepcopy(state['widgets'])},'result_design':{}}]}
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
   card=page.locator('details').filter(has=page.get_by_text('Browser acceptance',exact=True))
   await card.locator('summary').click();await card.get_by_role('button',name='Apri sessione').click()
   await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
   editor=page.get_by_role('region',name='Editor grafico delle pagine')
   await expect(editor.get_by_role('img',name='Quorivio')).to_be_visible()
   await expect(editor.get_by_role('button',name='Esci',exact=True)).to_be_visible()
   assert await editor.locator('.editor-bottom-controls').count()==0,'Obsolete persistent controls are still rendered'
   assert await editor.locator('.canvas-blank-menu-trigger').count()==0,'Obsolete canvas context trigger is still rendered'
   assert await editor.locator('.editor-secondary-workflow').count()==0,'Inactive recovery panel is still rendered'
   canvas=page.get_by_role('group',name='Canvas grafico widget')
   await expect(canvas).to_be_visible()
   # Real authenticated-app rendering, exercised against the API fixture:
   # the editor and its two rehearsal viewers must share the same geometry.
   # The modal must isolate the background and restore the exact invoker.
   preview_trigger=editor.locator('.editor-preview-open.preview-both')
   await preview_trigger.click()
   # Regression: the overlay looked correct in screenshots but was inaccessible
   # to role-based locators when nested under the inert editor/dashboard tree.
   # Verify actual body-portal ownership before checking aria-modal semantics.
   backdrop=page.locator('.rehearsal-backdrop')
   await expect(backdrop).to_be_visible()
   assert await backdrop.evaluate('(node)=>node.parentElement===document.body'), 'Rehearsal must use a body-level portal'
   assert await backdrop.evaluate('(node)=>!node.closest("[inert],[aria-hidden=true]")'), 'Rehearsal portal was hidden from assistive technology'
   rehearsal=page.get_by_role('dialog',name='Anteprima interattiva della sessione')
   await expect(rehearsal).to_be_visible()
   await expect(rehearsal.locator('.rehearsal-pane')).to_have_count(2)
   assert await editor.locator('.editor-exit').evaluate('(node)=>!!node.closest("[inert]")'), 'Editor background must be inert during rehearsal'
   assert not await rehearsal.evaluate('(node)=>node.inert'), 'Rehearsal must remain interactive'
   await expect(rehearsal.get_by_role('button',name='Chiudi anteprima')).to_be_focused()
   layout=await page.evaluate('''() => {
     const rect=s=>document.querySelector(s)?.getBoundingClientRect();
     const art=rect('.editor-ux-v2 .widget-canvas');
     const slide=rect('.rehearsal-pane .rehearsal-slide');
     const widget=rect('.rehearsal-pane .rehearsal-widget');
     if(!art||!slide||!widget)return null;
     return { editorRatio:art.width/art.height, previewRatio:slide.width/slide.height,
       widget:{x:(widget.left-slide.left)/slide.width*100,y:(widget.top-slide.top)/slide.height*100,
               width:widget.width/slide.width*100,height:widget.height/slide.height*100}};
   }''')
   assert layout and abs(layout['editorRatio']-16/9)<.09 and abs(layout['previewRatio']-16/9)<.09, layout
   for coordinate,expected in [('x',10),('y',10),('width',20),('height',20)]:
    assert abs(layout['widget'][coordinate]-expected)<1.1,(layout,coordinate)
   await rehearsal.get_by_role('button',name='Partecipante',exact=True).click()
   await expect(rehearsal.locator('.rehearsal-pane')).to_have_count(1)
   await rehearsal.get_by_role('button',name='Affiancate').click()
   await expect(rehearsal.locator('.rehearsal-pane')).to_have_count(2)
   await page.keyboard.press('Escape')
   await expect(rehearsal).to_have_count(0)
   assert await preview_trigger.evaluate('(node)=>document.activeElement===node'), 'Modal must restore preview trigger focus'
   assert not await editor.locator('.editor-exit').evaluate('(node)=>!!node.closest("[inert]")'), 'Editor must be interactive after rehearsal'
   # Canvas's native context menu can only be activated by right-click (long press on touch).
   await open_canvas_context(page)
   await expect(page.get_by_role('group',name='Menu contestuale sfondo canvas')).to_be_visible()
   await expect(page.get_by_role('button',name='Salva ora')).to_be_visible()
   await page.get_by_role('button',name='Chiudi menu',exact=True).click()
   thumb=page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta')
   await thumb.click()
   actions=page.get_by_role('group',name='Azioni pagina 1')
   for label in ('Nuova pagina prima','Nuova pagina dopo','Duplica pagina','Elimina pagina','Esporta layout JSON'):
    await expect(actions.get_by_role('button',name=label)).to_be_visible()
   await expect(actions.get_by_text('Importa layout JSON')).to_be_visible()
   await thumb.click()
   # Keyboard and grouped arrangement remain functional through the context menu.
   disclosure=page.locator('.canvas-accessible-controls > summary')
   await disclosure.click()
   checks=page.get_by_role('region',name='Organizzazione accessibile dei widget').get_by_role('checkbox',name='Seleziona')
   await checks.nth(0).check();await checks.nth(1).check()
   await click_canvas_tool(page,'Sposta selezione a destra')
   await page.keyboard.press('Control+z')
   await click_canvas_tool(page,'Porta selezione davanti')
   await page.keyboard.press('Control+z')
   await checks.nth(0).check();await checks.nth(1).check()
   # A rejected group duplication raises an alert. Capture it rather than letting
   # Playwright silently dismiss it before the widget-count assertion.
   duplication_alerts=[]
   async def handle_duplication_alert(dialog):
    duplication_alerts.append((dialog.type,dialog.message))
    await dialog.dismiss()
   def observe_duplication_dialog(dialog):
    asyncio.create_task(handle_duplication_alert(dialog))
   page.on('dialog',observe_duplication_dialog)
   await click_canvas_tool(page,'Duplica selezione')
   await expect(page.locator('.widget-canvas-item')).to_have_count(5)
   assert not duplication_alerts,duplication_alerts
   page.remove_listener('dialog',observe_duplication_dialog)
   await page.keyboard.press('Control+z')
   await expect(page.locator('.widget-canvas-item')).to_have_count(3)
   await checks.nth(0).check();await checks.nth(1).check()
   # The product requires an explicit confirmation for every destructive action.
   # Playwright otherwise auto-dismisses native confirm dialogs, making this
   # acceptance test fail even when the UI correctly asks the user.
   deletion_confirmations=[]
   async def accept_deletion(dialog):
    deletion_confirmations.append((dialog.type,dialog.message))
    if dialog.type=='confirm' and dialog.message=='Eliminare 2 widget selezionati?':
     await dialog.accept()
    else:
     await dialog.dismiss()
   def on_delete_dialog(dialog):
    asyncio.create_task(accept_deletion(dialog))
   page.on('dialog',on_delete_dialog)
   await click_canvas_tool(page,'Elimina selezione')
   await expect(page.locator('.widget-canvas-item')).to_have_count(1)
   assert deletion_confirmations==[('confirm','Eliminare 2 widget selezionati?')],deletion_confirmations
   page.remove_listener('dialog',on_delete_dialog)
   await page.keyboard.press('Control+z')
   await expect(page.locator('.widget-canvas-item')).to_have_count(3)
   await page.locator('.widget-canvas-item').first.focus()
   await page.keyboard.press('ArrowRight')
   await page.keyboard.press('Control+z')
   # Verify a real responsive viewport without introducing a hidden mobile toolbar.
   await page.set_viewport_size({'width':420,'height':860})
   await expect(page.get_by_role('complementary',name='Aggiungi widget')).to_be_visible()
   await expect(page.get_by_role('complementary',name='Miniature delle pagine')).to_be_visible()
   await page.set_viewport_size({'width':1440,'height':940})
   # Unique palette icons, no duplicate icon semantics or native title tooltips.
   palette=page.get_by_role('complementary',name='Aggiungi widget')
   buttons=palette.locator('.editor-icon-tool')
   assert await buttons.count()==17
   names=await buttons.evaluate_all('(els)=>els.map(e=>e.querySelector("svg")?.getAttribute("class"))')
   assert len(set(names))==len(names),names
   assert await buttons.evaluate_all('(els)=>els.every(e=>!e.hasAttribute("title"))')
   state['drop_before']=True;state['drop_after']=True
   await page.get_by_role('button',name='Aggiungi widget: Testo').click()
   await expect(page.locator('.widget-canvas-item')).to_have_count(4)
   # Browser->API autosave->server read-back and reload: no Save button.
   for _ in range(95):
    if state['saves']>=1 and await editor.get_by_text('Salvato automaticamente').is_visible():break
    await asyncio.sleep(.15)
   assert state['saves']>=1
   assert state['saves']==1 and len(state['widgets'])==4 and not state['drop_before'] and not state['drop_after'],state
   await expect(editor.get_by_text('Salvato automaticamente')).to_be_visible()
   await page.reload(wait_until='domcontentloaded')
   await page.get_by_role('button',name='Apri sessione').first.click()
   card=page.locator('details').filter(has=page.get_by_text('Browser acceptance',exact=True))
   await card.locator('summary').click();await card.get_by_role('button',name='Apri sessione').click()
   await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
   await expect(page.locator('.widget-canvas-item')).to_have_count(4)
   # Import/export live only on the relevant thumbnail, never below the artboard.
   await page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta').click()
   async with page.expect_download() as info:
    await page.get_by_role('button',name='Esporta layout JSON').click()
   backup=await info.value
   assert Path(await backup.path()).exists()
   await page.get_by_role('button',name='Esci',exact=True).click()
   assert await page.get_by_role('region',name='Editor grafico delle pagine').count()==0
   # Real Chromium touch input: hold on blank canvas 650 ms, then release.
   # This exercises the app's actual PointerEvent timer rather than dispatching fake DOM events.
   touch_context=await browser.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True)
   mobile=await touch_context.new_page()
   await mobile.route('**/api/**',mock)
   await mobile.goto(os.environ.get('QUORIVIO_WEB_URL','http://127.0.0.1:5173/'),wait_until='domcontentloaded')
   await mobile.get_by_role('button',name='Apri sessione').first.wait_for()
   await acknowledge_functional_cookie_notice(mobile)
   await mobile.get_by_role('button',name='Apri sessione').first.click()
   card=mobile.locator('details').filter(has=mobile.get_by_text('Browser acceptance',exact=True))
   await card.locator('summary').click();await card.get_by_role('button',name='Apri sessione').click()
   await mobile.get_by_role('button',name='✎ Modifica le pagine').first.click()
   canvas=mobile.get_by_role('group',name='Canvas grafico widget')
   point=await canvas_background_point(mobile)
   x,y=point['x'],point['y']
   cdp=await touch_context.new_cdp_session(mobile)
   await cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
   await asyncio.sleep(.68)
   await cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
   await expect(mobile.get_by_role('group',name='Menu contestuale sfondo canvas')).to_be_visible()
   await expect(mobile.get_by_role('button',name='Salva ora')).to_be_visible()
   await touch_context.close()
   assert not errors,errors
  except Exception:
   artifact=Path(os.environ.get('QUORIVIO_BROWSER_ARTIFACT_DIR','/tmp/quorivio-browser-artifacts'));artifact.mkdir(parents=True,exist_ok=True)
   try:await page.screenshot(path=str(artifact/'editor-autosave-failure.png'),full_page=True)
   except Exception:pass
   raise
  finally:await browser.close()
 print('PASS Chromium editor mock fidelity, transient network retry, committed response-loss recovery, contextual menus, unique icons, autosave/reload and safe exit')

if __name__=='__main__':asyncio.run(main())
