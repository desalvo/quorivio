#!/usr/bin/env python3
"""Real Chromium pointer/keyboard acceptance of the *actual* preview focus module.

Runs without localhost or fake credentials. Does not substitute a screen reader,
physical mobile device or authenticated PostgreSQL application E2E acceptance.
"""
import asyncio
import os
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
ESBUILD = '''const fs=require('fs'),esbuild=require('esbuild');
const code=fs.readFileSync(process.argv[1],'utf8');
esbuild.transform(code,{loader:'ts',format:'iife',globalName:'QuorivioRehearsal'}).then(result=>process.stdout.write(result.code)).catch(e=>{console.error(e);process.exit(1)});'''

async def main():
    js = subprocess.check_output(['node','-e',ESBUILD,str(ROOT/'apps/web/src/rehearsal-dialog.ts')],cwd=ROOT,text=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for width,height in [(1440,900),(390,844)]:
                page=await browser.new_page(viewport={'width':width,'height':height})
                await page.set_content('''<!doctype html><html lang="it"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>
                #overlay{position:fixed;inset:0;background:#dde9f2;display:none;align-items:center;justify-content:center;}
                #overlay.open{display:flex}#shell{background:#fff;padding:20px;border-radius:12px;display:grid;gap:12px;min-width:240px}
                button,input{min-height:44px}
                </style></head><body><aside id="other-app" aria-hidden="false">Widget esterno</aside><div id="react-root"><main id="dashboard"><button id="launcher">Apri anteprima</button><button id="outside">Pulsante pagina</button><button id="previous-inert" inert>Già disabilitato</button></main>
                <div role="dialog" aria-modal="true" aria-label="Anteprima interattiva della sessione" id="overlay"><div id="shell" tabindex="-1">
                <button id="presenter">Presentatore</button><button disabled>Non selezionabile</button>
                <input id="response" aria-label="Risposta simulata"><button id="participant">Partecipante</button>
                <button id="close" aria-label="Chiudi anteprima">Chiudi</button>
                </div></div></div></body></html>''')
                await page.add_script_tag(content=js)
                await page.evaluate('''() => {
                    const overlay=document.querySelector('#overlay'),shell=document.querySelector('#shell');
                    let cleanup;
                    const close=()=>{cleanup?.();cleanup=undefined;overlay.classList.remove('open')};
                    document.querySelector('#launcher').addEventListener('click',()=>{
                        overlay.classList.add('open');cleanup=QuorivioRehearsal.activateRehearsalDialog(shell,close);
                    });
                    document.querySelector('#close').addEventListener('click',close);
                }''')
                await page.locator('#launcher').click()
                assert await page.evaluate('document.activeElement?.id') == 'close','Close button must receive initial focus'
                assert await page.evaluate('document.body.style.overflow') == 'hidden','Background scroll must be locked'
                assert await page.locator('#dashboard').evaluate('(node)=>node.inert'),'Application background should be inert'
                assert await page.locator('#other-app').evaluate('(node)=>node.inert'),'Other body content should be inert'
                assert await page.locator('#dashboard').get_attribute('aria-hidden') == 'true','Dashboard not hidden from assistive tech'
                assert await page.locator('#other-app').get_attribute('aria-hidden') == 'true','External UI not hidden from assistive tech'
                assert not await page.locator('#overlay').evaluate('(node)=>node.inert'),'Modal must remain interactive'
                assert await page.get_by_role('button',name='Pulsante pagina').count() == 0,'Background button leaked into accessible modal view'
                assert await page.locator('#previous-inert').evaluate('(node)=>node.inert'),'Existing inert controls must remain inert'
                await page.keyboard.press('Tab')
                assert await page.evaluate('document.activeElement?.id') == 'presenter','Tab must wrap from last to first'
                await page.keyboard.press('Shift+Tab')
                assert await page.evaluate('document.activeElement?.id') == 'close','Shift+Tab must wrap from first to last'
                await page.locator('#outside').focus()
                await page.keyboard.press('Tab')
                assert await page.evaluate('document.activeElement?.id') == 'presenter','Tab must recover escaped focus'
                # Simulate programmatic/AT focusin outside the modal even when
                # inert background controls would normally refuse .focus().
                await page.evaluate('''() => document.querySelector('#outside').dispatchEvent(
                    new FocusEvent('focusin',{bubbles:true}))''')
                assert await page.evaluate('document.activeElement?.id') == 'presenter', 'Programmatic outside focus must be contained immediately'
                await page.locator('#response').fill('Risposta privata di prova')
                # IME Escape cancels a composed character, not the entire modal.
                await page.locator('#response').evaluate("node=>node.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',isComposing:true,bubbles:true}))")
                assert await page.locator('#overlay').evaluate('node=>node.classList.contains("open")'),'IME Escape incorrectly closed preview'
                await page.keyboard.press('Escape')
                assert await page.evaluate('document.activeElement?.id') == 'launcher','Escape must restore the invoker'
                assert await page.evaluate('document.body.style.overflow') == '','Original background scroll must be restored'
                assert not await page.locator('#dashboard').evaluate('(node)=>node.inert'),'Application must be available after close'
                assert not await page.locator('#other-app').evaluate('(node)=>node.inert'),'External body content must be restored'
                assert await page.locator('#dashboard').get_attribute('aria-hidden') is None,'Dashboard aria-hidden was not restored'
                assert await page.locator('#other-app').get_attribute('aria-hidden') == 'false','Explicit prior aria-hidden value must be preserved'
                assert await page.locator('#previous-inert').evaluate('(node)=>node.inert'),'Pre-existing inert state must remain unchanged'
                assert await page.get_by_role('button',name='Pulsante pagina').count() == 1,'Background button not restored to accessibility tree'
                assert not await page.locator('#overlay').evaluate('(node)=>node.classList.contains("open")')
                # Match production's body-level React portal after the nested
                # compatibility case. The real dialog must be discoverable by
                # its accessible role even though the application becomes inert.
                await page.locator('#overlay').evaluate('(node)=>document.body.appendChild(node)')
                await page.locator('#launcher').click()
                await page.get_by_role('dialog',name='Anteprima interattiva della sessione').wait_for(state='visible')
                assert await page.locator('#react-root').evaluate('(node)=>node.inert'), 'Portal failed to isolate the editor root'
                assert await page.locator('#overlay').evaluate('(node)=>node.parentElement===document.body&&!node.closest("[inert],[aria-hidden=true]")'), 'Portal must not be hidden from the accessibility tree'
                await page.locator('#close').click()
                assert not await page.locator('#react-root').evaluate('(node)=>node.inert'), 'Closing portal must restore the app root'
                # Reopening must not leave stale key handlers, and explicit close restores focus.
                await page.locator('#launcher').click()
                await page.locator('#close').click()
                assert await page.evaluate('document.activeElement?.id') == 'launcher'
                await page.close()
                print(f'PASS Chromium {width}px: real rehearsal module initial focus, cyclic Tab, outside-focus recovery, Escape and close restoration')
        finally:
            await browser.close()

if __name__=='__main__':asyncio.run(main())
