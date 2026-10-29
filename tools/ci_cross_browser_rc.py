#!/usr/bin/env python3
"""Opt-in native Firefox/WebKit (or Chromium) RC geometry and modal keyboard tests.

Uses the production TypeScript modal module and CSS, not a mock implementation.
On GitHub, install the two real browser engines explicitly in the optional job.
This is automated browser-engine evidence, not NVDA/VoiceOver, real touch, or
independent visual/AGID approval. No credentials or service calls are involved.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright
from ci_rc_public_stage_chromium import HTML as PUBLIC_STAGE_HTML

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path('/tmp/quorivio-cross-browser-artifacts')
TRANSFORM = r'''const fs=require('fs'),esbuild=require('esbuild');
esbuild.transform(fs.readFileSync(process.argv[1],'utf8'),{loader:'ts',format:'iife',globalName:'QuorivioRehearsal'})
.then(out=>process.stdout.write(out.code)).catch(err=>{console.error(err);process.exit(1)});'''
MODAL_HTML = '''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>
<div id="app"><button id="invoker">Apri anteprima</button><button id="background">Sfondo</button></div>
<div id="dialog" role="dialog" aria-modal="true" aria-label="Anteprima interattiva della sessione" hidden>
 <section id="shell"><button id="close" aria-label="Chiudi anteprima">Chiudi</button>
 <button id="not-tab" tabindex="-1">Non ciclabile</button>
 <div id="editor" contenteditable="true" role="textbox" aria-label="Testo modificabile">Modifica</div>
 <button id="last">Ultimo</button></section></div>
</body></html>'''


async def modal_check(page, script: str) -> None:
    await page.set_content(MODAL_HTML)
    await page.add_script_tag(content=script)
    await page.evaluate('''() => {
      const d=document.querySelector('#dialog');let cleanup;
      const close=()=>{cleanup?.();cleanup=undefined;d.hidden=true};
      document.querySelector('#invoker').onclick=()=>{d.hidden=false;cleanup=QuorivioRehearsal.activateRehearsalDialog(document.querySelector('#shell'),close)};
      document.querySelector('#close').onclick=close;
    }''')
    await page.locator('#invoker').click()
    assert await page.evaluate('document.activeElement.id') == 'close'
    assert await page.locator('#app').evaluate('e=>e.inert')
    assert await page.locator('#app').get_attribute('aria-hidden') == 'true'
    await page.keyboard.press('Tab')
    assert await page.evaluate('document.activeElement.id') == 'editor', 'contenteditable must be a keyboard target and tabindex=-1 must be skipped'
    await page.keyboard.press('Tab')
    assert await page.evaluate('document.activeElement.id') == 'last'
    await page.keyboard.press('Tab')
    assert await page.evaluate('document.activeElement.id') == 'close', 'Tab must wrap'
    await page.keyboard.press('Shift+Tab')
    assert await page.evaluate('document.activeElement.id') == 'last', 'Shift+Tab must wrap'
    await page.evaluate('''() => {
      const portal=document.createElement('aside');portal.id='external';portal.setAttribute('aria-hidden','false');
      portal.innerHTML='<button id="external-action">External action</button>';document.body.appendChild(portal);
    }''')
    await page.wait_for_function('document.querySelector("#external")?.inert === true')
    assert await page.locator('#external').get_attribute('aria-hidden') == 'true'
    await page.evaluate("document.querySelector('#shell').appendChild(document.querySelector('#external'))")
    await page.wait_for_function('document.querySelector("#external")?.inert === false')
    assert await page.locator('#external').get_attribute('aria-hidden') == 'false'
    await page.evaluate("document.body.appendChild(document.querySelector('#external'))")
    await page.wait_for_function('document.querySelector("#external")?.inert === true')
    await page.keyboard.press('Escape')
    assert await page.evaluate('document.activeElement.id') == 'invoker', 'Close must restore invoker focus'
    assert not await page.locator('#app').evaluate('e=>e.inert')
    assert await page.locator('#app').get_attribute('aria-hidden') is None
    assert not await page.locator('#external').evaluate('e=>e.inert')
    assert await page.locator('#external').get_attribute('aria-hidden') == 'false'
    assert await page.evaluate('document.body.style.overflow') == ''
    # When the actions disappear asynchronously the shell itself must remain
    # keyboard-focusable and its temporary tabindex must be undone on close.
    await page.locator('#invoker').click()
    await page.evaluate("document.querySelector('#shell').replaceChildren()")
    await page.keyboard.press('Tab')
    assert await page.evaluate('document.activeElement.id') == 'shell', 'Empty modal needs a fallback focus anchor'
    await page.keyboard.press('Escape')
    assert await page.evaluate('document.activeElement.id') == 'invoker'
    assert await page.locator('#shell').get_attribute('tabindex') is None


async def stage_check(page, css: str) -> None:
    await page.set_content(PUBLIC_STAGE_HTML)
    await page.add_style_tag(content=css)
    result=await page.evaluate('''() => {
      const stage=document.querySelector('#public');const w=document.querySelector('#public-widget');
      const s=stage.getBoundingClientRect(),style=getComputedStyle(w);
      return {ratio:s.width/s.height,x:parseFloat(style.left)/s.width,y:parseFloat(style.top)/s.height,
        width:parseFloat(style.width)/s.width,height:parseFloat(style.height)/s.height,
        rotation:style.transform,scroll:document.querySelector('.audience-stage-scroll').scrollWidth,
        client:document.querySelector('.audience-stage-scroll').clientWidth};
    }''')
    assert abs(result['ratio']-16/9)<.025,result
    for key,value in {'x':.16,'y':.23,'width':.37,'height':.26}.items():
        assert abs(result[key]-value)<.012,(key,result)
    assert result['rotation']!='none',result
    await page.locator('#public').evaluate("e=>e.className='audience-widget-layout stage-reading'")
    reading=await page.evaluate('''() => {
      const w=document.querySelector('#public-widget');
      return {position:getComputedStyle(w).position,transform:getComputedStyle(w).transform,
      target:document.querySelector('#answer').getBoundingClientRect().height};
    }''')
    assert reading['position']=='relative' and reading['transform']=='none',reading
    assert reading['target']>=44,reading


async def check_engine(playwright, engine: str, script: str, css: str):
    browser_type=getattr(playwright,engine)
    kwargs={'headless':True}
    if engine == 'chromium':
        kwargs['executable_path']=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium')
        kwargs['args']=['--no-sandbox','--disable-dev-shm-usage']
    # Fail closed when the native engine is unavailable; no silent Chromium
    # substitution when Firefox or WebKit was explicitly requested.
    browser=await browser_type.launch(**kwargs)
    try:
        for width,height in ((1440,900),(390,844)):
            context=await browser.new_context(viewport={'width':width,'height':height})
            page=await context.new_page()
            page.set_default_timeout(10000)
            errors: list[str] = []
            page.on('pageerror',lambda error: errors.append(str(error)))
            try:
                await modal_check(page,script)
                await stage_check(page,css)
                assert not errors, f'Unexpected browser script errors: {errors}'
            except Exception as error:
                ARTIFACTS.mkdir(parents=True,exist_ok=True)
                prefix=ARTIFACTS/f'{engine}-{width}'
                try:
                    await page.screenshot(path=str(prefix)+'.png',full_page=True,timeout=3000)
                except Exception:
                    pass
                (Path(str(prefix)+'.json')).write_text(json.dumps({
                    'engine':engine,'viewport_width':width,'viewport_height':height,
                    'failure':type(error).__name__,'message':str(error)[:500],
                    'script_errors':errors[:5],
                    'note':'Offline fixture; no credentials or personal data.',
                },indent=2),encoding='utf8')
                raise
            finally:
                await context.close()
            print(f'PASS {engine} {width}px: native engine, modal Tab/contenteditable/inert/focus restore + 16:9 stage and 44px reading controls',flush=True)
    finally:
        await browser.close()


async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engines',nargs='+',choices=('chromium','firefox','webkit'),default=['chromium'])
    args=parser.parse_args()
    js=subprocess.check_output(['node','-e',TRANSFORM,str(ROOT/'apps/web/src/rehearsal-dialog.ts')],text=True,cwd=ROOT)
    css=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
    async with async_playwright() as p:
        for engine in args.engines:
            await check_engine(p,engine,js,css)


if __name__=='__main__':
    asyncio.run(main())
