#!/usr/bin/env python3
"""Test real *built React* second factor, Enter vs button on desktop/mobile.

All MFA challenges/codes are disposable in-memory fixtures, not real credentials.
The network is replaced before mounting the production JS bundle. This checks
client behavior and does not claim to test a real authenticator/SMTP service.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
HTML = '<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><div id="root"></div></body></html>'
API = r"""() => {
  window.mfaProbe = {calls: [], signedIn: false, failOnce: false};
  window.fetch = async (url, options={}) => {
    const path = new URL(String(url), 'https://fixture.invalid').pathname;
    const reply = (data, status=200) => new Response(JSON.stringify(data),
      {status, headers: {'Content-Type': 'application/json'}});
    if(path==='/api/auth/oidc/providers') return reply({providers: []});
    if(path==='/api/auth/me') return window.mfaProbe.signedIn
      ? reply({id:'fixture-user',email:'fixture@example.invalid',role:'presenter',approved:true})
      : reply({error:'unauthenticated'}, 401);
    if(path==='/api/auth/login') return reply({mfa_required:true,challenge_id:'fixture-only',methods:['totp','email']});
    if(path==='/api/auth/mfa/challenge/email') return reply({ok:true});
    if(path==='/api/auth/mfa/challenge/verify'||path==='/api/auth/email-mfa/verify'){
      const body=JSON.parse(options.body||'{}');
      window.mfaProbe.calls.push({path,body});
      await new Promise(resolve=>setTimeout(resolve,220));
      if(window.mfaProbe.failOnce){window.mfaProbe.failOnce=false;return reply({error:'invalid_mfa_code'},401);}
      window.mfaProbe.signedIn=true;
      return reply({ok:true});
    }
    return reply({items:[],activities:[],sessions:[],total:0});
  };
}"""


async def prepare(browser, js, css, width, height):
    context = await browser.new_context(viewport={'width':width,'height':height})
    page = await context.new_page()
    errors=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    await page.set_content(HTML)
    await page.evaluate(API)
    await page.add_style_tag(content=css.read_text(encoding='utf-8'))
    await page.add_script_tag(content=js.read_text(encoding='utf-8'),type='module')
    cookie=page.get_by_role('dialog',name='Informativa cookie funzionali')
    await expect(cookie).to_be_visible(timeout=10000)
    await cookie.get_by_role('button',name='Ho capito').click()
    await expect(cookie).not_to_be_visible()
    await page.get_by_label('Email o nickname').fill('fixture@example.invalid')
    await page.get_by_label('Password', exact=True).fill('fixture-only-password')
    await page.get_by_role('button',name='Accedi').click()
    mfa=page.get_by_role('form',name='Secondo fattore')
    await expect(mfa).to_be_visible(timeout=10000)
    return context,page,mfa,errors


async def verify_totp(browser, js, css, width, height):
    context,page,mfa,errors=await prepare(browser,js,css,width,height)
    try:
        field=mfa.get_by_label('Codice autenticatore')
        await field.fill('12345')
        await field.press('Enter')
        assert await page.evaluate('window.mfaProbe.calls.length')==0, 'short TOTP must not submit'
        await field.fill('123456')
        await page.evaluate('window.mfaProbe.failOnce=true')
        # Two rapid Enter events must result in a single POST.
        await field.press('Enter')
        await field.press('Enter')
        await page.wait_for_function('window.mfaProbe.calls.length===1')
        await expect(page.get_by_text('invalid_mfa_code')).to_be_visible(timeout=5000)
        await expect(mfa.get_by_role('button',name='Verifica / Verify')).to_be_enabled()
        # Error recovery: the same form remains keyboard-submittable.
        await field.press('Enter')
        await page.wait_for_function('window.mfaProbe.calls.length===2')
        await expect(mfa).to_have_count(0, timeout=10000)
        calls=await page.evaluate('window.mfaProbe.calls')
        assert [x['body']['method'] for x in calls]==['totp','totp'],calls
        assert all(x['body']['code']=='123456' for x in calls)
        assert not errors,errors
    finally:
        await context.close()
    print(f'PASS real React Chromium {width}px: TOTP Enter, invalid length, duplicate lock, failed-code retry')


async def verify_variants(browser, js, css, width, height):
    for mode in ('email','recovery','button'):
        context,page,mfa,errors=await prepare(browser,js,css,width,height)
        try:
            if mode=='email':
                await mfa.get_by_role('button',name='Email').click()
                await mfa.get_by_label('Codice email').fill('654321')
                await mfa.get_by_label('Codice email').press('Enter')
            elif mode=='recovery':
                await mfa.get_by_role('button',name='Usa codice di recupero').click()
                await mfa.get_by_label('Codice di recupero').fill('fixture-recovery-code')
                await mfa.get_by_label('Codice di recupero').press('Enter')
            else:
                await mfa.get_by_label('Codice autenticatore').fill('123456')
                await mfa.get_by_role('button',name='Verifica / Verify').click()
            await page.wait_for_function('window.mfaProbe.calls.length===1')
            await expect(mfa).to_have_count(0, timeout=10000)
            calls=await page.evaluate('window.mfaProbe.calls')
            assert len(calls)==1
            expected='email' if mode=='email' else 'recovery' if mode=='recovery' else 'totp'
            if mode=='email':assert calls[0]['path']=='/api/auth/email-mfa/verify'
            else:assert calls[0]['body']['method']==expected
            assert not errors,errors
        finally:
            await context.close()
    print(f'PASS real React Chromium {width}px: email/recovery Enter and existing verify button')


async def main():
    js=next((ROOT/'apps/web/dist/assets').glob('index-*.js'),None)
    css=next((ROOT/'apps/web/dist/assets').glob('index-*.css'),None)
    assert js and css, 'Build Vite frontend before RC186 real React test'
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        try:
            for width,height in ((1440,900),(390,844)):
                await verify_totp(browser,js,css,width,height)
                await verify_variants(browser,js,css,width,height)
        finally:
            await browser.close()

if __name__=='__main__':
    asyncio.run(main())
