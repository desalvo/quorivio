#!/usr/bin/env python3
"""Chromium UI acceptance with deterministic API fixture; no production database needed."""
import asyncio
import copy
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from ci_editor_context_tools import ensure_canvas_tools_open, click_canvas_tool, open_canvas_context, canvas_background_point
from ci_editor_context_tools import wait_for_editor_sync, uncovered_widget_context_point

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

async def await_frontend_mount(page, errors=None):
    """Check the compiled React bundle, not a Vite optimizer/HMR race.

    Asset status and failure *counts* are safe in public GitHub logs; URLs,
    cookies, session IDs, request bodies and contents are never printed.
    """
    try:
        await page.locator('#root .app').wait_for(state='visible', timeout=25000)
    except Exception:
        root_children = await page.locator('#root > *').count()
        asset_http = await page.evaluate("""() => performance.getEntriesByType('resource')
            .filter(e=>new URL(e.name).pathname.startsWith('/assets/'))
            .map(e=>({kind:new URL(e.name).pathname.endsWith('.js')?'JS':'other',
                       responseStatus:e.responseStatus||0}))""")
        print(f'FAIL Chromium compiled frontend startup: root_children={root_children}, '
              f'asset_http={asset_http}, page_error_count={len(errors or [])}; '
              'React did not mount. Inspect the built asset probe before editor actions.', flush=True)
        raise

async def select_exact_widget_pair(page):
    """Select exactly two via genuine accessible controls and check both UI layers.

    The previous CI only checked two boxes; it did not uncheck a third box
    retained across undo or context operations (run 41328071305).
    """
    await expect(page.locator('.widget-canvas-item')).to_have_count(3)
    rows=page.locator('.canvas-accessible-row')
    await expect(rows).to_have_count(3)
    wanted={'First','Second'}
    observed=set()
    for row in await rows.all():
        description=(await row.locator('strong').inner_text()).strip()
        label=description.split('. ',1)[-1]
        if label in wanted:
            observed.add(label)
        checkbox=row.locator('input[type="checkbox"]')
        await checkbox.set_checked(label in wanted)
    assert observed==wanted, f'Unexpected fixture row labels: {sorted(observed)}'
    checked_rows=await rows.evaluate_all("elements => elements.filter(e=>e.querySelector('input[type=checkbox]')?.checked).map(e=>e.querySelector('strong')?.textContent)")
    selected_ids=await page.locator('.widget-canvas-item[data-selected="true"]').evaluate_all('nodes => nodes.map(n=>n.dataset.widgetId)')
    assert len(checked_rows)==2 and set(selected_ids)=={'widget-a','widget-b'}, (
        f'Explicit selection mismatch: checked={checked_rows}, canvas_ids={selected_ids}'
    )
    await expect(page.locator('.widget-canvas-item[data-selected="true"]')).to_have_count(2)

async def main():
 async with async_playwright() as pw:
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':1440,'height':940},accept_downloads=True)
  page.set_default_timeout(12000)
  state={'widgets':copy.deepcopy(WIDGETS),'revision':1,'saves':0,'drop_before':False,'drop_after':False,'auth_error':None,'session_error':None,'session_active':False}
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
   elif path=='/api/auth/me':
    if state['auth_error']:
     await route.fulfill(status=state['auth_error'],content_type='application/json',json={'error':'unauthorized'});return
    data={'id':'user-test','email':'test@example.org','nickname':'Test','role':'presenter'}
   elif path=='/api/auth/oidc/providers':data={'providers':[]}
   elif path=='/api/sessions':data={'items':[SES],'total':1}
   elif path==f'/api/sessions/{SESSION}':
    if state['session_error']:
     await route.fulfill(status=state['session_error'],content_type='application/json',json={'error':'temporarily_unavailable'});return
    live_session={**SES,'status':'active' if state['session_active'] else 'draft','join_code':'ROTATED' if state['session_active'] else 'ABCDEF'}
    data={**SNAP,'session':live_session,'activities':[{**ACT,'design_revision':state['revision'],'page_design':{'widgets':copy.deepcopy(state['widgets'])},'result_design':{}}]}
   elif path.endswith('/assets') or path.endswith('/presenter-profiles') or path.endswith('/appointments') or path.endswith('/schedule'):data=[]
   elif path=='/api/calendar':data=[]
   else:data=[]
   await route.fulfill(status=200,content_type='application/json',json=data)
  await page.route('**/api/**',mock)
  try:
   await page.goto(os.environ.get('QUORIVIO_WEB_URL','http://127.0.0.1:5173/'),wait_until='domcontentloaded')
   await await_frontend_mount(page,errors)
   # The native showModal() cookie dialog makes underlying UI inaccessible to
   # get_by_role() until the presenter acknowledges it. Always dismiss first.
   await acknowledge_functional_cookie_notice(page)
   await page.get_by_role('button',name='Apri sessione').first.wait_for()
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
   # Editor and session dashboard coexist in the DOM. Exactly one dialog may
   # mount: otherwise separate focus traps inert/aria-hide each other.
   await expect(backdrop).to_have_count(1)
   await expect(backdrop).to_be_visible()
   assert await backdrop.evaluate('(node)=>node.parentElement===document.body'), 'Rehearsal must use a body-level portal'
   assert await backdrop.evaluate('(node)=>!node.closest("[inert],[aria-hidden=true]")'), 'Rehearsal portal was hidden from assistive technology'
   rehearsal=page.get_by_role('dialog',name='Anteprima interattiva della sessione')
   await expect(rehearsal).to_be_visible()
   await expect(rehearsal.locator('.rehearsal-pane')).to_have_count(2)
   # Role-based queries correctly hide the inert editor; inspect its DOM node instead.
   assert await page.locator('.powerpoint-editor.editor-ux-v2 .editor-exit').evaluate('(node)=>!!node.closest("[inert]")'), 'Editor background must be inert during rehearsal'
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
   # RC37 regression: unstyled text is black on the white slide, and a
   # widget's context commands are in an unclipped body-level portal.
   default_foreground=await page.locator('.widget-canvas-item').first.evaluate('(node)=>getComputedStyle(node).color')
   assert default_foreground=='rgb(0, 0, 0)',default_foreground
   # Close any stale canvas menu before testing an actual right-click.
   # A center click can miss a partially covered widget and invoke the
   # background menu instead; use a viewport/elementFromPoint-verified pixel.
   background_menu=page.get_by_role('group',name='Menu contestuale sfondo canvas')
   if await background_menu.is_visible():
    await background_menu.get_by_role('button',name='Chiudi menu').click()
   first_widget=page.locator('.widget-canvas-item').first
   await expect(first_widget).to_be_visible()
   point=await uncovered_widget_context_point(first_widget)
   # RC81: The page.mouse absolute pixel became stale when the app recentered
   # its stage between hit-test and mousedown. A locator-bound click waits for
   # layout stability and verifies that Chromium can really hit this widget.
   offset={'x':point['offset_x'],'y':point['offset_y']}
   await first_widget.click(button='right',position=offset,trial=True)
   # Capture native dispatch targets without altering the event, its default,
   # selection or React state. Record only element classes (never page text).
   await page.evaluate('''() => {
     window.__qContextTrace=[];
     for(const type of ['pointerdown','contextmenu']){
       document.addEventListener(type, event=>{
         const widget=event.target instanceof Element?event.target.closest('.widget-canvas-item'):null;
         const canvas=event.target instanceof Element?event.target.closest('.widget-canvas'):null;
         if(!canvas)return;
         window.__qContextTrace.push({type,button:event.button,
           targetIsWidget:!!widget,hitWidget:!!document.elementFromPoint(event.clientX,event.clientY)?.closest('.widget-canvas-item')});
       },{capture:true,once:true});
     }
   }''')
   await first_widget.click(button='right',position=offset)
   widget_menu=page.get_by_role('group',name='Azioni widget text',exact=True)
   try:
    await expect(widget_menu).to_be_visible(timeout=4000)
   except AssertionError as error:
    background_open=await background_menu.is_visible()
    trace=await page.evaluate('''() => window.__qContextTrace || []''')
    raise AssertionError('Real widget right-click did not open its menu; '
                         f'canvas_background_menu_open={background_open}; '
                         f'native_target_trace={trace}. '
                         'Check pointerdown/contextmenu ownership and layout reflow.') from error
   await expect(background_menu).to_have_count(0)
   assert await widget_menu.evaluate('''node => {
    const r=node.getBoundingClientRect();
    return node.parentElement===document.body && r.left>=0 && r.top>=0 &&
      r.right<=window.innerWidth+1 && r.bottom<=window.innerHeight+1;
   }'''), 'Widget context menu must be fully visible outside clipping canvas'
   await page.keyboard.press('Escape')
   await expect(widget_menu).to_have_count(0)
   # Canvas's native context menu can only be activated by right-click (long press on touch).
   await open_canvas_context(page)
   await expect(page.get_by_role('group',name='Menu contestuale sfondo canvas')).to_be_visible()
   await expect(page.get_by_role('button',name='Salva ora')).to_be_visible()
   await page.get_by_role('button',name='Chiudi menu',exact=True).click()
   thumb=page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta')
   await thumb.click()
   actions=page.get_by_role('group',name='Azioni pagina 1')
   # RC236: page actions are arranged in native <details> disclosures.
   # The former acceptance test queried hidden descendants of a closed
   # disclosure. Open the actual accessible controls with user clicks instead
   # of forcing CSS visibility or weakening the command assertions.
   for label in ('Apri pagina','Duplica pagina','Elimina pagina'):
    await expect(actions.get_by_role('button',name=label)).to_be_visible()
   create_section=actions.locator('details.page-editor-thumb-submenu').filter(
    has=page.get_by_text('Crea e importa pagine',exact=True))
   await expect(create_section).not_to_have_attribute('open','')
   await create_section.locator('summary').click()
   await expect(create_section).to_have_attribute('open','')
   for label in ('Nuova pagina prima','Nuova pagina dopo'):
    await expect(actions.get_by_role('button',name=label)).to_be_visible()
   await expect(create_section.get_by_text('Importa layout JSON')).to_be_visible()
   await expect(create_section.get_by_text('Importa PDF/PPTX…')).to_be_visible()
   export_section=actions.locator('details.page-editor-thumb-submenu').filter(
    has=page.get_by_text('Esporta e dati',exact=True))
   await export_section.locator('summary').click()
   await expect(export_section).to_have_attribute('open','')
   await expect(actions.get_by_role('button',name='Esporta layout JSON')).to_be_visible()
   await thumb.click()
   # Keyboard and grouped arrangement remain functional through the context menu.
   disclosure=page.locator('.canvas-accessible-controls > summary')
   await disclosure.click()
   checks=page.get_by_role('region',name='Organizzazione accessibile dei widget').get_by_role('checkbox',name='Seleziona')
   await select_exact_widget_pair(page)
   await click_canvas_tool(page,'Sposta selezione a destra')
   await page.keyboard.press('Control+z')
   await click_canvas_tool(page,'Porta selezione davanti')
   await page.keyboard.press('Control+z')
   # Undo and layer operations can retain old selection.
   # Explicitly select exactly two widgets, not merely check two boxes.
   await select_exact_widget_pair(page)
   # RC119: short fixture labels must not repeatedly inflate to the slide edge.
   # The old outer scrollHeight included edge resize handles; this made group
   # placement genuinely impossible without any bug in the group command.
   fixture_geometry=await page.locator('.widget-canvas-item').evaluate_all("""nodes=>
     nodes.map(n=>({id:n.dataset.widgetId,top:parseFloat(n.style.top),height:parseFloat(n.style.height)}))""")
   assert len(fixture_geometry)==3 and all(g['height']<26 for g in fixture_geometry), (
     'AutoFit inflated short fixture widgets before duplication: '+str(fixture_geometry)
   )
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
   # Report a real native no-space rejection before a misleading count timeout.
   assert not duplication_alerts, ('Group duplication rejected: '+str(duplication_alerts)+'; geometry='+str(fixture_geometry))
   await expect(page.locator('.widget-canvas-item')).to_have_count(5)
   page.remove_listener('dialog',observe_duplication_dialog)
   # One undo must revert the user's duplication, not only an auto-fit side effect.
   # Focus a non-editable canvas control so Ctrl+Z is handled by the editor.
   await page.get_by_role('group',name='Allineamento widget selezionati').locator('button:visible').first.focus()
   await page.keyboard.press('Control+z')
   await expect(page.locator('.widget-canvas-item')).to_have_count(3)
   await select_exact_widget_pair(page)
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
   # RC86: widgets grew from 17 to 19 with Title and Footer. A fixed count
   # prevented the browser gate from testing the actual palette semantics.
   # Require every supported kind, one tool per kind, unique icons and
   # accessible names, while allowing future widget families to be added.
   kinds=await buttons.evaluate_all('(els)=>els.map(e=>e.dataset.widgetKind || e.dataset.graphicPalette)')
   required={'rating','reactions','text','shape','line','timer','qr','profile',
             'question','postit','image','video','logo','pdf','topic-question',
             'timed-quiz','results-button','participant-count','title','footer'}
   assert required<=set(kinds),f'Widget palette missing required kinds: {sorted(required-set(kinds))}'
   assert 'divider' not in kinds,'Legacy Separator must not be offered for new pages'
   assert len(kinds)==len(set(kinds)),f'Duplicate widget palette kinds: {kinds}'
   labels=await buttons.evaluate_all('(els)=>els.map(e=>e.getAttribute("aria-label"))')
   assert all(label and label.startswith('Aggiungi widget: ') for label in labels),labels
   assert len(labels)==len(set(labels)),f'Duplicate widget palette labels: {labels}'
   names=await buttons.evaluate_all('(els)=>els.map(e=>e.querySelector("svg")?.getAttribute("class"))')
   assert all(names) and len(set(names))==len(names),names
   # Regular rail tools use a custom floating tooltip; dedicated graphics tools
   # intentionally advertise right-click / long-press via their native hint.
   assert await buttons.evaluate_all('(els)=>els.every(e=>e.dataset.graphicPalette || !e.hasAttribute("title"))')
   graphics=palette.locator('button.editor-icon-tool[data-graphic-palette]')
   assert await graphics.count()==2, 'Linee and Forme must remain distinct graphic rail tools'
   for kind,label in [('line','Linee'),('shape','Forme')]:
    graphic=palette.locator(f'button.editor-icon-tool[data-graphic-palette="{kind}"]')
    await expect(graphic).to_have_attribute('aria-label',f'Aggiungi widget: {label}')
    await graphic.click(button='right')
    popup=page.get_by_role('dialog',name=f'Scegli {label.lower()} da inserire')
    await expect(popup).to_be_visible()
    assert await popup.locator('.graphic-preset-choices button').count()>=2, f'{label} preset choices absent'
    await page.keyboard.press('Escape')
    await expect(popup).to_have_count(0)
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
   await await_frontend_mount(page,errors)
   # RC129: RC128 intentionally restores the authenticated session, selected tab
   # and open page editor after a browser reload. Re-opening from the dashboard
   # is an obsolete action: the restored editor is above the sidebar and must
   # correctly intercept clicks on background controls (GitHub 41389141345).
   # Test the actual restored state; never force-click or disable pointer safety.
   editor=page.get_by_role('region',name='Editor grafico delle pagine')
   await expect(editor).to_be_visible(timeout=30000)
   await expect(editor.get_by_role('button',name='Esci',exact=True)).to_be_visible()
   await expect(editor.locator('.page-editor-thumb-row.is-active')).to_have_count(1)
   await expect(editor.locator('.page-editor-thumb-row.is-active .page-editor-thumb')).to_have_attribute('aria-current','page')
   await expect(editor.locator('.widget-canvas-item')).to_have_count(4)
   recovered=await page.evaluate("() => JSON.parse(sessionStorage.getItem('quorivio.workspace.v1') || '{}')")
   assert recovered.get('sessionId')==SESSION and recovered.get('pageId')==ACTIVITY, (
       'Reload lost the selected authenticated session or editor page')
   # RC208: a restarted/active session with a rotated join code must recover
   # the editor from this tab's stored route, without clearing auth cookies.
   state['session_active']=True
   await page.reload(wait_until='domcontentloaded')
   await await_frontend_mount(page,errors)
   editor=page.get_by_role('region',name='Editor grafico delle pagine')
   await expect(editor).to_be_visible(timeout=30000)
   await expect(editor.locator('.widget-canvas-item')).to_have_count(4)
   assert await page.evaluate("() => JSON.parse(sessionStorage.getItem('quorivio.workspace.v1') || '{}').sessionId") == SESSION

   # A temporary snapshot outage must show a visible recovery UI, not a blank
   # canvas or an instruction to erase cookies. A manual retry restores the editor.
   state['session_error']=503
   await page.reload(wait_until='domcontentloaded')
   await await_frontend_mount(page,errors)
   await expect(page.locator('.session-restore-status')).to_be_visible(timeout=15000)
   state['session_error']=None
   await page.get_by_role('button',name='Riprova ora').click()
   editor=page.get_by_role('region',name='Editor grafico delle pagine')
   await expect(editor).to_be_visible(timeout=30000)

   # An expired presenter cookie causes a normal login view, not a permanent
   # freeze; restoring server authentication permits opening the same workspace.
   state['auth_error']=401
   await page.reload(wait_until='domcontentloaded')
   await await_frontend_mount(page,errors)
   # RC216: the unauthenticated presenter form now lives inside the landing
   # screen, not the removed legacy narrow container. Assert accessible login
   # controls and that the previous protected editor is no longer rendered.
   await expect(page.get_by_role('heading',name='Accedi come presentatore',exact=True)).to_be_visible(timeout=15000)
   await expect(page.get_by_role('textbox',name='Email o nickname')).to_be_visible()
   await expect(page.get_by_role('textbox',name='Password')).to_be_visible()
   await expect(page.get_by_role('button',name='Accedi',exact=True)).to_be_visible()
   await expect(page.get_by_role('region',name='Editor grafico delle pagine')).to_have_count(0)
   state['auth_error']=None
   await page.reload(wait_until='domcontentloaded')
   await await_frontend_mount(page,errors)
   editor=page.get_by_role('region',name='Editor grafico delle pagine')
   await expect(editor).to_be_visible(timeout=30000)
   state['session_active']=False

   # Import/export live only on the relevant thumbnail, never below the artboard.
   await page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta').click()
   # RC236: downloads are under a native collapsed disclosure after reload too.
   export_actions=page.get_by_role('group',name='Azioni pagina 1',exact=True)
   export_details=export_actions.locator('details.page-editor-thumb-submenu').filter(
    has=page.get_by_text('Esporta e dati',exact=True))
   await export_details.locator('summary').click()
   await expect(export_details).to_have_attribute('open','')
   async with page.expect_download() as info:
    await export_actions.get_by_role('button',name='Esporta layout JSON').click()
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
   await await_frontend_mount(mobile)
   await acknowledge_functional_cookie_notice(mobile)
   await mobile.get_by_role('button',name='Apri sessione').first.wait_for()
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
