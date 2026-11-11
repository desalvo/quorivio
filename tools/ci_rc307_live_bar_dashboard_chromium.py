#!/usr/bin/env python3
"""RC307: genuine PostgreSQL + React + Chromium results-bar parity and reload."""
from __future__ import annotations
import asyncio
import os
from playwright.async_api import async_playwright, expect
from ci_browser_editor_postgres import BASE, call, open_editor
from ci_browser_participant import validate_disposable_origin
from ci_rc298_real_pie_pg_chromium import persisted_case, CHART

TITLE = 'RC307 real bars and presenter recovery'

async def run():
    validate_disposable_origin(BASE)
    for key in ('QUORIVIO_CI_ADMIN_EMAIL','QUORIVIO_CI_NEW_PASSWORD','QUORIVIO_CI_LOAD_TOKEN'):
        if not os.getenv(key):
            raise RuntimeError('Missing disposable CI secret: '+key)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),
            headless=True,args=['--no-sandbox'])
        context = await browser.new_context(
            viewport={'width':1440,'height':940},locale='it-IT',
            extra_http_headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']})
        try:
            await call(context,'POST','/api/auth/login',{
                'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
                'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
            sid,aid = await persisted_case(context,TITLE,True)
            snapshot = await call(context,'GET',f'/api/sessions/{sid}')
            page = next(p for p in snapshot['activities'] if p['id']==aid)
            widgets = list(page['page_design']['widgets'])
            result = next(w for w in widgets if w['id']==CHART)
            result.update({
                'label':'Titolo widget risultati RC307','resultsView':'bars',
                'resultsOnly':False,'showTitle':True,
                'showSourceTitle':False,'showSourceAnswers':False,
                'resultSortOrder':'index-desc','resultTopCount':3,
                'autoFit':True})
            await call(context,'PATCH',f'/api/sessions/{sid}/activities/{aid}/design',{
                'page_design':{**page['page_design'],'widgets':widgets},
                'result_design':page.get('result_design') or {},
                'expected_design_revision':page['design_revision']})
            errors=[]
            editor = await context.new_page()
            editor.on('pageerror',lambda exc:errors.append(str(exc)))
            await open_editor(editor,TITLE)
            canvas = editor.locator('.widget-canvas-item[data-widget-kind="results-button"]')
            await expect(canvas).to_have_count(1,timeout=20000)
            await expect(canvas.locator('.linked-results.result-view-bars')).to_have_count(1)
            await expect(canvas.get_by_text('Titolo widget risultati RC307')).to_be_visible()
            await expect(canvas.locator('.widget-fit-frame[data-fit-mode="scroll"]')).to_have_count(1)
            assert await canvas.locator('.canvas-widget-results-native').count()==1
            print('RC307 PASS: editor title visible, no auto-fit shrink')
            await editor.locator('button.editor-preview-open.preview-presenter[aria-haspopup="dialog"]').click()
            dialog = editor.get_by_role('dialog',name='Anteprima interattiva della sessione')
            await expect(dialog).to_be_visible()
            preview = dialog.locator('.rehearsal-pane .rehearsal-widget[data-widget-kind="results-button"]')
            await expect(preview).to_have_count(1)
            await expect(preview.locator('.widget-fit-frame[data-fit-mode="scroll"]')).to_have_count(1)
            await expect(preview.get_by_text('Titolo widget risultati RC307')).to_be_visible()
            await dialog.get_by_role('button',name='Chiudi anteprima').click()
            print('RC307 PASS: preview title and no-fit renderer')
            await call(context,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
            await call(context,'POST',f'/api/sessions/{sid}/activities/{aid}/open',{})
            screen = await context.new_page()
            screen.on('pageerror',lambda exc:errors.append(str(exc)))
            await screen.goto(BASE+'/screen/'+sid,wait_until='domcontentloaded')
            live = screen.locator('.projection-widget[data-widget-kind="results-button"]')
            await expect(live).to_have_count(1,timeout=20000)
            await expect(live.locator('.linked-results.result-view-bars')).to_have_count(1)
            await expect(live.get_by_text('Titolo widget risultati RC307')).to_be_visible()
            await expect(live.locator('.widget-fit-frame[data-fit-mode="scroll"]')).to_have_count(1)
            await expect(screen.locator('.session-restore-error')).to_have_count(0)
            await screen.reload(wait_until='domcontentloaded')
            await expect(screen.locator('.projection-widget[data-widget-kind="results-button"] .linked-results.result-view-bars')).to_have_count(1,timeout=20000)
            await expect(screen.locator('.session-restore-error')).to_have_count(0)
            assert not errors, 'React errors: '+'; '.join(errors[:3])
            current = await call(context,'GET',f'/api/sessions/{sid}')
            assert current['session']['status']=='active'
            print('RC307 PASS: live bars survive reload, session remains active')
        finally:
            await context.close()
            await browser.close()

if __name__=='__main__':
    asyncio.run(run())
