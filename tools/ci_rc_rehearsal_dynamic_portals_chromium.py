#!/usr/bin/env python3
"""Real Chromium focus/inert test of the actual TS module, no server or fake auth."""
import asyncio
import os
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
NODE=r'''const fs=require('fs'),ts=require('typescript');
const result=ts.transpileModule(fs.readFileSync(process.argv[1],'utf8'),{fileName:'rehearsal-dialog.ts',compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ESNext}});
process.stdout.write(result.outputText.replace(/^export /gm,'')+'\nvar QuorivioRehearsal={activateRehearsalDialog};');'''

async def main():
    env=dict(os.environ)
    if not env.get('NODE_PATH'):
        env['NODE_PATH']=subprocess.check_output(['npm','root','-g'],text=True).strip()
    js=subprocess.check_output(['node','-e',NODE,str(ROOT/'apps/web/src/rehearsal-dialog.ts')],cwd=ROOT,env=env,text=True)
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        try:
            for width in (1440,390):
                page=await browser.new_page(viewport={'width':width,'height':844})
                await page.set_content('''<html lang="it"><body><div id="app"><button id="launch">Apri</button></div><aside id="existing" aria-hidden="false">Altro servizio</aside><div role="dialog" aria-modal="true" aria-label="Anteprima interattiva della sessione" id="modal"><div id="shell" tabindex="-1"><button id="one">Uno</button><button aria-hidden="true" id="hidden">Non visibile</button><button id="close" aria-label="Chiudi anteprima">Chiudi</button></div></div></body></html>''')
                await page.add_script_tag(content=js)
                await page.evaluate('''() => {let cleanup;const modal=document.querySelector('#modal');modal.hidden=true;
                 const close=()=>{cleanup?.();cleanup=null;modal.hidden=true};
                 document.querySelector('#launch').onclick=()=>{modal.hidden=false;cleanup=QuorivioRehearsal.activateRehearsalDialog(document.querySelector('#shell'),close)};
                 document.querySelector('#close').onclick=close}''')
                await page.locator('#launch').click()
                assert await page.evaluate('document.activeElement?.id')=='close'
                await page.evaluate('''() => {const portal=document.createElement('aside');portal.id='late-portal';portal.setAttribute('aria-hidden','false');portal.innerHTML='<button>New background button</button>';document.body.appendChild(portal)}''')
                await page.wait_for_function("document.querySelector('#late-portal')?.inert===true")
                assert await page.locator('#late-portal').get_attribute('aria-hidden')=='true'
                assert await page.get_by_role('button',name='New background button').count()==0
                await page.keyboard.press('Tab')
                assert await page.evaluate('document.activeElement?.id')=='one','Tab should skip aria-hidden button'
                await page.keyboard.press('Shift+Tab')
                assert await page.evaluate('document.activeElement?.id')=='close'
                await page.keyboard.press('Escape')
                assert await page.evaluate('document.activeElement?.id')=='launch'
                assert not await page.locator('#late-portal').evaluate('(node)=>node.inert')
                assert await page.locator('#late-portal').get_attribute('aria-hidden')=='false'
                assert await page.locator('#existing').get_attribute('aria-hidden')=='false'
                assert await page.evaluate('document.body.style.overflow')==''
                print(f'PASS actual TS rehearsal focus Chromium {width}px: dynamic portals, focus trap, accessibility and restore')
                await page.close()
        finally: await browser.close()
if __name__=='__main__':asyncio.run(main())
