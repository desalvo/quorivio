#!/usr/bin/env python3
"""Real built React recovery-screen acceptance with an in-memory network.

The fixture has no live credentials and never prints the one-time bearer.
This verifies browser address/referrer hygiene only, not real SMTP/PG E2E.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
TOKEN='fixtureResetBearerNonProduction0000000000000'
HTML='<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="referrer" content="no-referrer"></head><body><div id="root"></div></body></html>'
API="""() => {
  window.confirmCalls=[];
  window.confirmFailuresRemaining=1;
  const values=new Map();
  Object.defineProperty(document,'cookie',{configurable:true,
    get:()=>values.get('cookie')||'',set:v=>values.set('cookie',String(v))});
  const storage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,String(v)),
    removeItem:k=>values.delete(k),clear:()=>values.clear(),length:0,key:()=>null};
  Object.defineProperty(window,'localStorage',{configurable:true,get:()=>storage});
  Object.defineProperty(window,'sessionStorage',{configurable:true,get:()=>storage});
  window.fetch=async (u,options={})=>{
    const path=new URL(String(u),'https://fixture.invalid').pathname;
    const send=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json'}});
    if(path==='/api/auth/me')return send({error:'unauthenticated'},401);
    if(path==='/api/auth/oidc/providers')return send({providers:[]});
    if(path==='/api/auth/password-reset/confirm'){
      window.confirmCalls.push(JSON.parse(options.body||'{}'));
      await new Promise(resolve=>setTimeout(resolve,180));
      if(window.confirmFailuresRemaining-->0)return send({error:'invalid_or_expired_token'},400);
      return send({ok:true});
    }
    return send({items:[],total:0});
  };
}"""

async def main():
    js=next((ROOT/'apps/web/dist/assets').glob('index-*.js'),None)
    css=next((ROOT/'apps/web/dist/assets').glob('index-*.css'),None)
    assert js is not None and css is not None,'npm run build required before browser acceptance'
    await run_browser(js,css)

async def run_browser(js,css):
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        try:
            for width,height in ((1440,900),(390,844)):
                for encoding in ('legacy-query','fragment'):
                    context=await browser.new_context(viewport={'width':width,'height':height})
                    page=await context.new_page()
                    errors=[]
                    page.on('pageerror',lambda err:errors.append(str(err)))
                    await page.goto('about:blank?reset_token='+TOKEN+'&lang=it#recover' if encoding == 'legacy-query' else 'about:blank?lang=it#reset_token='+TOKEN,wait_until='domcontentloaded')
                    await page.set_content(HTML)
                    await page.evaluate(API)
                    await page.add_style_tag(content=css.read_text(encoding='utf8'))
                    await page.add_script_tag(content=js.read_text(encoding='utf8'),type='module')
                    cookie=page.get_by_role('dialog',name='Informativa cookie funzionali')
                    if await cookie.count():
                        await cookie.get_by_role('button',name='Ho capito').click()
                    # Real React consumes token on mount, removing it from address.
                    await expect(page.get_by_role('heading',name='Recupero password / Password reset')).to_be_visible()
                    assert await page.evaluate('location.search')=='?lang=it'
                    assert await page.evaluate('location.hash') == ('#recover' if encoding == 'legacy-query' else '')
                    assert await page.evaluate('document.referrer')==''
                    assert await page.evaluate('document.querySelector("meta[name=referrer]").content')=='no-referrer'
                    assert not await page.evaluate('''() => Object.values(localStorage).concat(Object.values(sessionStorage)).some(v=>String(v).includes('fixtureResetBearer'))''')
                    await page.get_by_label('Nuova password / New password',exact=True).fill('fixture-only-new-password-123')
                    confirm=page.get_by_role('button',name='Conferma / Confirm')
                    await expect(confirm).to_be_disabled()
                    await page.get_by_label('Conferma nuova password / Confirm new password').fill('fixture-only-wrong-password-999')
                    await expect(page.get_by_role('status',name='')).to_contain_text('Password')
                    await expect(confirm).to_be_disabled()
                    assert not await page.evaluate('window.confirmCalls.length'),'mismatch must never submit'
                    await page.get_by_label('Conferma nuova password / Confirm new password').fill('fixture-only-new-password-123')
                    await expect(confirm).to_be_enabled()
                    # Two synchronous click attempts must not issue two reset POSTs.
                    await page.evaluate('''() => {const b=Array.from(document.querySelectorAll('button')).find(x=>x.textContent.includes('Conferma / Confirm'));if(!b)throw new Error('missing confirmation');b.click();b.click();}''')
                    await expect(page.get_by_role('button',name='Verifica in corso… / Verifying…')).to_be_disabled()
                    # Expired/replayed token must keep the form available without
                    # putting the bearer back into history; retry must be possible.
                    await expect(page.get_by_text('invalid_or_expired_token')).to_be_visible()
                    assert TOKEN not in page.url
                    assert await page.evaluate('window.confirmCalls.length')==1,'double submit must be deduplicated'
                    await page.get_by_label('Conferma nuova password / Confirm new password').press('Enter')
                    await expect(page.get_by_role('heading',name='Recupero password / Password reset')).to_have_count(0)
                    calls=await page.evaluate('window.confirmCalls')
                    assert len(calls)==2 and all(c['token']==TOKEN and c['new_password']=='fixture-only-new-password-123' for c in calls)
                    assert TOKEN not in page.url and not errors,errors
                    await context.close()
                    print(f'PASS real React {encoding} recovery URL hygiene Chromium {width}px: one-time bearer removed from history, password confirmation/validation, retry and no storage exposure')
        finally:
            await browser.close()

if __name__=='__main__':asyncio.run(main())
