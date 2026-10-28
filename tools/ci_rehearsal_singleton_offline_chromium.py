#!/usr/bin/env python3
"""Actual built React application + deterministic fixture, served without HTTP.

This isolated Chromium preflight avoids restricted localhost networking. It
checks dashboard/editor coexistence, one and only one accessible rehearsal,
unsaved editor geometry and background restoration. The authenticated network,
PostgreSQL and physical screen reader gates remain independent.
"""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from ci_browser_editor import SESSION, ACTIVITY, ACT, SES, SNAP

ROOT = Path(__file__).resolve().parents[1]

async def main():
    assets = ROOT / 'apps/web/dist/assets'
    js = next(assets.glob('index-*.js'), None)
    css = next(assets.glob('index-*.css'), None)
    if not js or not css:
        raise RuntimeError('Build web assets first: npm run build')
    fixture = {'session': SES, 'activities': [ACT], 'results': [], 'connected_participants': 0}
    # Use a realistic /api router in memory, never send fixture data externally.
    api = '''() => {
      const values = new Map();
      Object.defineProperty(document, 'cookie', {configurable:true,
        get:()=>values.get('cookie')||'',set:v=>values.set('cookie',String(v))});
      const storage={getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,String(v)),
        removeItem:k=>values.delete(k),clear:()=>values.clear()};
      Object.defineProperty(window,'localStorage',{configurable:true,get:()=>storage});
      Object.defineProperty(window,'sessionStorage',{configurable:true,get:()=>storage});
      const snapshot=__SNAP__,session=__SESSION__;
      window.fetch = async (url, options={}) => {
        const path=new URL(String(url),'https://fixture.invalid').pathname;
        const send = (data,status=200)=>new Response(JSON.stringify(data),
          {status,headers:{'Content-Type':'application/json'}});
        if(path==='/api/auth/me')return send({id:'user-test',email:'test@example.org',nickname:'Test',role:'presenter'});
        if(path==='/api/auth/oidc/providers')return send({providers:[]});
        if(path==='/api/sessions')return send({items:[session],total:1});
        if(path==='/api/sessions/'+session.id)return send(snapshot);
        if(path==='/api/calendar'||path.endsWith('/assets')||path.endsWith('/presenter-profiles')||path.endsWith('/appointments')||path.endsWith('/schedule'))return send([]);
        return send([]);
      };
    }'''.replace('__SNAP__',json.dumps(fixture)).replace('__SESSION__',json.dumps(SES))
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        try:
            for width,height in [(1440,940),(390,844)]:
                page=await browser.new_page(viewport={'width':width,'height':height})
                page.set_default_timeout(12000)
                errors=[]
                page.on('pageerror',lambda error: errors.append(str(error)))
                await page.set_content('<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><div id="root"></div></body></html>')
                await page.evaluate(api)
                await page.add_style_tag(content=css.read_text(encoding='utf8'))
                await page.add_script_tag(content=js.read_text(encoding='utf8'),type='module')
                cookie=page.get_by_role('dialog',name='Informativa cookie funzionali')
                await expect(cookie).to_be_visible()
                await cookie.get_by_role('button',name='Ho capito').click()
                await page.get_by_role('button',name='Apri sessione').first.click()
                card=page.locator('details').filter(has=page.get_by_text('Browser acceptance',exact=True))
                await card.locator('summary').click()
                await card.get_by_role('button',name='Apri sessione').click()
                # Open from the session dashboard first. It must also have exactly
                # one body portal and return focus before the editor is opened.
                dashboard_open=page.get_by_role('group',name='Anteprime della sessione').get_by_role('button',name='▣ Anteprime affiancate')
                await dashboard_open.click()
                dashboard_overlay=page.locator('.rehearsal-backdrop')
                await expect(dashboard_overlay).to_have_count(1)
                await expect(page.get_by_role('dialog',name='Anteprima interattiva della sessione')).to_be_visible()
                await page.get_by_role('button',name='Chiudi anteprima').click()
                await expect(dashboard_overlay).to_have_count(0)
                assert await dashboard_open.evaluate('(node)=>document.activeElement===node')
                await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
                editor=page.get_by_role('region',name='Editor grafico delle pagine')
                await expect(editor).to_be_visible()
                invoker=editor.locator('.editor-preview-open.preview-both')
                await invoker.click()
                overlay=page.locator('.rehearsal-backdrop')
                await expect(overlay).to_have_count(1)
                await expect(overlay).to_be_visible()
                assert await overlay.evaluate('(node)=>node.parentElement===document.body&&!node.inert&&!node.closest("[inert],[aria-hidden=true]")'), 'Portal hidden or not body-owned'
                dlg=page.get_by_role('dialog',name='Anteprima interattiva della sessione')
                await expect(dlg).to_be_visible()
                await expect(dlg.locator('.rehearsal-pane')).to_have_count(2)
                assert await page.locator('.powerpoint-editor.editor-ux-v2 .editor-exit').evaluate('(node)=>!!node.closest("[inert]")')
                await dlg.get_by_role('button',name='Partecipante',exact=True).click()
                await expect(dlg.locator('.rehearsal-pane')).to_have_count(1)
                await dlg.get_by_role('button',name='Affiancate').click()
                await expect(dlg.locator('.rehearsal-pane')).to_have_count(2)
                await page.keyboard.press('Escape')
                await expect(overlay).to_have_count(0)
                assert await invoker.evaluate('(node)=>document.activeElement===node'), 'Focus not returned to invoker'
                assert not await editor.locator('.editor-exit').evaluate('(node)=>!!node.closest("[inert]")')
                assert not errors, errors
                print(f'PASS offline built React Chromium {width}px: one accessible dual preview, inert background and restored focus')
                await page.close()
        finally:
            await browser.close()

if __name__=='__main__':
    asyncio.run(main())
