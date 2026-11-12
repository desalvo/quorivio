#!/usr/bin/env python3
"""RC307: genuine PostgreSQL + React + Chromium results-bar parity and reload."""
from __future__ import annotations
import asyncio
import os
from playwright.async_api import async_playwright, expect
from ci_browser_editor_postgres import BASE, call, open_editor
from ci_browser_participant import validate_disposable_origin
from ci_rc298_real_pie_pg_chromium import persisted_case, CHART, QUESTION

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
            source = next(w for w in widgets if w['id']==QUESTION)
            source['resultsView'] = 'bars'
            result = next(w for w in widgets if w['id']==CHART)
            result.update({
                'label':'Titolo widget risultati RC307',
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
            await expect(canvas.locator('.widget-fit-frame[data-fit-mode="scale"]')).to_have_count(1)
            # The rendered viewport must contain the *effective scaled content*,
            # including long labels, percentages and answer-key badges.
            async def assert_fitted(widget):
                frame=widget.locator('.widget-fit-frame[data-fit-mode="scale"]')
                return await frame.evaluate('''node => {
                    const content=node.querySelector(':scope > .widget-fit-content');
                    const factor=Number(content?.style.getPropertyValue('--widget-fit-scale')||1);
                    return Number.isFinite(factor)&&factor>0&&
                      content.scrollWidth*factor<=node.clientWidth+4&&
                      content.scrollHeight*factor<=node.clientHeight+4&&
                      getComputedStyle(node).overflowY!=='auto';
                }''')
            async def wait_for_fit(widget):
                for _ in range(45):
                    if await assert_fitted(widget):
                        return
                    await asyncio.sleep(.2)
                assert await assert_fitted(widget), 'Scaled content must fit without a nested scrollbar'
            await wait_for_fit(canvas)
            assert await canvas.locator('.canvas-widget-results-native').count()==1
            print('RC326 PASS: editor title visible, entire results widget uses proportional content fit')
            await editor.locator('button.editor-preview-open.preview-presenter[aria-haspopup="dialog"]').click()
            dialog = editor.get_by_role('dialog',name='Anteprima interattiva della sessione')
            await expect(dialog).to_be_visible()
            preview = dialog.locator('.rehearsal-pane .rehearsal-widget[data-widget-kind="results-button"]')
            await expect(preview).to_have_count(1)
            await expect(preview.locator('.widget-fit-frame[data-fit-mode="scale"]')).to_have_count(1)
            await wait_for_fit(preview)
            await expect(preview.get_by_text('Titolo widget risultati RC307')).to_be_visible()
            await dialog.get_by_role('button',name='Chiudi anteprima').click()
            print('RC326 PASS: rehearsal preview uses the same proportional fit policy')
            await call(context,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
            await call(context,'POST',f'/api/sessions/{sid}/activities/{aid}/open',{})
            screen = await context.new_page()
            screen.on('pageerror',lambda exc:errors.append(str(exc)))
            await screen.goto(BASE+'/screen/'+sid,wait_until='domcontentloaded')
            live = screen.locator('.projection-widget[data-widget-kind="results-button"]')
            await expect(live).to_have_count(1,timeout=20000)
            await expect(live.locator('.linked-results.result-view-bars')).to_have_count(1)
            await expect(live.get_by_text('Titolo widget risultati RC307')).to_be_visible()
            await expect(live.locator('.widget-fit-frame[data-fit-mode="scale"]')).to_have_count(1)
            await wait_for_fit(live)
            await expect(screen.locator('.session-restore-error')).to_have_count(0)
            await screen.reload(wait_until='domcontentloaded')
            await expect(screen.locator('.projection-widget[data-widget-kind="results-button"] .linked-results.result-view-bars')).to_have_count(1,timeout=20000)
            await expect(screen.locator('.session-restore-error')).to_have_count(0)
            # Exercise the *authenticated dashboard*, which the historic RC307
            # test missed: it rendered the separate /screen projection only.
            await editor.get_by_role('region',name='Editor grafico delle pagine').get_by_role('button',name='Esci',exact=True).click()
            await expect(editor.locator('.live-panel')).to_be_visible(timeout=20000)
            await expect(editor.locator('.session-restore-error')).to_have_count(0)
            await editor.reload(wait_until='domcontentloaded')
            await expect(editor.locator('.session-restore-error')).to_have_count(0)
            await expect(editor.locator('.live-panel')).to_be_visible(timeout=20000)
            print('RC309 PASS: authenticated dashboard and reopened session remain usable')
            assert not errors, 'React errors: '+'; '.join(errors[:3])
            current = await call(context,'GET',f'/api/sessions/{sid}')
            assert current['session']['status']=='active'
            print('RC307 PASS: live bars survive reload, session remains active')
        finally:
            await context.close()
            await browser.close()

if __name__=='__main__':
    asyncio.run(run())
