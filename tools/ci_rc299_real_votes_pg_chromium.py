#!/usr/bin/env python3
"""RC299 mandatory full-app acceptance: real participant votes -> PostgreSQL -> presenter pie.

Unlike rehearsal, all counts come from isolated Chromium clients submitting through
the compiled React frontend and from the authenticated live result projection.
"""
from __future__ import annotations
import asyncio
import os
from playwright.async_api import async_playwright, expect
from ci_browser_editor_postgres import BASE, call
from ci_browser_participant import validate_disposable_origin
from ci_rc298_real_pie_pg_chromium import persisted_case, OPTIONS, TITLE_ON, QUESTION

async def join_vote(browser, code, sid, option, number, headers):
    mobile = number == 2
    context = await browser.new_context(
        viewport={'width': 390 if mobile else 1366, 'height': 844 if mobile else 900},
        is_mobile=mobile, has_touch=mobile, locale='it-IT',
        extra_http_headers=headers)
    try:
        page = await context.new_page()
        await page.goto(BASE+'/join/'+code, wait_until='domcontentloaded')
        cookie = page.get_by_role('button', name='Ho capito')
        if await cookie.count():
            await cookie.click()
        await expect(page.get_by_role('heading', name=TITLE_ON)).to_be_visible()
        await page.get_by_role('textbox', name='Pseudonimo').fill(f'RC299 participant {number}')
        await page.get_by_role('checkbox', name='Accetto i cookie funzionali necessari al servizio').check()
        await page.get_by_role('button', name='Entra').click()
        question = page.locator('[data-widget-kind="question"]')
        await expect(question).to_have_count(1)
        await expect(page.locator('[data-widget-kind="results-button"]')).to_have_count(0)
        await question.get_by_role('radio', name=OPTIONS[option]['label'], exact=True).check()
        await question.get_by_role('button', name='Invia risposta', exact=True).click()
        await expect(question.get_by_role('status')).to_contain_text('Risposta registrata')
        assert (await context.request.get(BASE+f'/api/sessions/{sid}/widget-answers')).status == 401
        print(f'RC299 PASS: independent real Chromium vote {number}')
    finally:
        await context.close()

async def main():
    validate_disposable_origin(BASE)
    for key in ('QUORIVIO_CI_ADMIN_EMAIL','QUORIVIO_CI_NEW_PASSWORD','QUORIVIO_CI_LOAD_TOKEN'):
        if not os.getenv(key):
            raise RuntimeError(f'Disposable CI secret missing: {key}')
    headers = {'X-Quorivio-Load-Token': os.environ['QUORIVIO_CI_LOAD_TOKEN']}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),
            headless=True,args=['--no-sandbox'])
        admin = await browser.new_context(
            viewport={'width':1440,'height':940},locale='it-IT',extra_http_headers=headers)
        try:
            await call(admin,'POST','/api/auth/login',{
                'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
                'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
            sid,aid = await persisted_case(admin,TITLE_ON,True)
            snapshot = await call(admin,'GET',f'/api/sessions/{sid}')
            code = snapshot['session']['join_code']
            assert isinstance(code,str) and code
            await call(admin,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
            await call(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/open',{})
            projection = await admin.new_page()
            errors = []
            projection.on('pageerror',lambda error:errors.append(str(error)))
            await projection.goto(BASE+'/screen/'+sid,wait_until='domcontentloaded')
            linked = projection.locator(
                '.projection-widget[data-widget-kind="results-button"] .presenter-linked-results')
            await expect(linked).to_have_count(1,timeout=20000)
            await expect(linked.locator('.linked-results-no-data')).to_be_visible(timeout=20000)
            for number,option in enumerate((0,1,0),start=1):
                await join_vote(browser,code,sid,option,number,headers)
            report = await call(admin,'GET',f'/api/sessions/{sid}/widget-answers')
            data = next(r for r in report if r['activity_id']==aid and
                        r['widget_id']==QUESTION and r['question_id']=='')
            assert data['responses']==3,data
            legend = linked.get_by_role('list',name='Percentuali delle risposte')
            await expect(legend).to_have_count(1,timeout=30000)
            items = legend.get_by_role('listitem')
            await expect(items).to_have_count(2,timeout=30000)
            await expect(items.nth(0)).to_have_attribute(
                'aria-label',f"{OPTIONS[0]['label']}: 2 risposte, 67%",timeout=30000)
            await expect(items.nth(1)).to_have_attribute(
                'aria-label',f"{OPTIONS[1]['label']}: 1 risposta, 33%",timeout=30000)
            assert await linked.locator('.linked-results-pie-chart path').count()==2
            assert not errors,'Presenter JavaScript errors: '+'; '.join(errors[:3])
            print('RC299 PASS: real PostgreSQL 2/1/0 votes update the live presenter pie')
            # A separate joined observer must still not see any aggregate.
            guest = await browser.new_context(viewport={'width':390,'height':844},
                                               is_mobile=True,has_touch=True,
                                               locale='it-IT',extra_http_headers=headers)
            try:
                page = await guest.new_page()
                await page.goto(BASE+'/join/'+code,wait_until='domcontentloaded')
                cookie = page.get_by_role('button',name='Ho capito')
                if await cookie.count():
                    await cookie.click()
                await page.get_by_role('textbox',name='Pseudonimo').fill('RC299 observer')
                await page.get_by_role('checkbox',name='Accetto i cookie funzionali necessari al servizio').check()
                await page.get_by_role('button',name='Entra').click()
                await expect(page.locator('[data-widget-kind="question"]')).to_have_count(1)
                assert not await page.locator('[data-widget-kind="results-button"]').count()
                assert (await guest.request.get(BASE+f'/api/sessions/{sid}/widget-answers')).status==401
            finally:
                await guest.close()
            print('RC299 PASS: private aggregates remain inaccessible to participants')
        finally:
            await admin.close()
            await browser.close()

if __name__=='__main__':
    asyncio.run(main())
