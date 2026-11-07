#!/usr/bin/env python3
"""RC250: real Chromium hit-test after expanded thumbnail menu at actual root CSS zoom.

An unzoomed static fixture incorrectly passed RC249.  Here the browser first
calculates a real DOMRect under root zoom; the production TS geometry helper
then returns CSS layout coordinates for a body-portal popup.  Clicking the
button a second time must really close the expanded menu without force=True.
The full compiled-React editor acceptance remains mandatory in the CI.
"""
import asyncio
import json
import os
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
CASES=[(320,240,.8,195,65),(390,844,.8,225,100),(760,720,.8,330,100),
       (960,760,.64,360,135),(1440,940,.8,320,140),(1440,940,1,320,140),
       (1440,940,1.2,320,140),(390,844,1.2,225,100)]

def positions(items):
    source='''import {thumbnailMenuPosition} from './apps/web/src/thumbnail-menu-layout.ts';
    const cases=JSON.parse(process.argv[1]);
    process.stdout.write(JSON.stringify(cases.map(({box,vw,vh,zoom}) =>
       thumbnailMenuPosition(box.right+8,box.top,vw,vh,box,zoom))));'''
    return json.loads(subprocess.run(
        ['node','--experimental-strip-types','--input-type=module','-e',source,json.dumps(items)],
        cwd=ROOT,check=True,capture_output=True,text=True).stdout)

async def verify(browser,vw,vh,zoom,x,y):
    page=await browser.new_page(viewport={'width':vw,'height':vh})
    try:
        await page.set_content(f'''<!doctype html><html style="zoom:{zoom*100}%"><head>
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <style>{CSS}</style></head><body>
        <div class="editor-ux-v2"><button type="button" class="page-editor-thumb-menu-trigger"
            style="position:fixed;left:{x}px;top:{y}px;right:auto;width:34px;height:34px"
            aria-label="Menu pagina 1: crea, duplica, elimina, sposta" aria-expanded="false"
            onclick="this.setAttribute('aria-expanded',this.getAttribute('aria-expanded')==='true'?'false':'true');if(this.getAttribute('aria-expanded')==='false')document.querySelector('.page-editor-thumb-menu-floating')?.remove()">…</button></div>
        </body></html>''')
        trigger=page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta')
        await trigger.click(timeout=2500)
        box=await trigger.evaluate('(n)=>n.getBoundingClientRect().toJSON()')
        actual_zoom=await page.evaluate('Number.parseFloat(getComputedStyle(document.documentElement).zoom)')
        assert abs(actual_zoom-zoom)<.001,(actual_zoom,zoom)
        pos=positions([{'box':box,'vw':vw,'vh':vh,'zoom':zoom}])[0]
        await page.evaluate('''p=>{
          const menu=document.createElement('div');
          menu.className='page-editor-thumb-menu page-editor-thumb-menu-floating';
          menu.setAttribute('role','group');menu.setAttribute('aria-label','Azioni pagina 1');
          menu.style.position='fixed';menu.style.left=p.left+'px';menu.style.top=p.top+'px';
          menu.style.maxHeight=p.maxHeight+'px';
          menu.style.setProperty('--thumbnail-menu-width',p.width+'px');
          menu.style.setProperty('--thumbnail-menu-max-height',p.maxHeight+'px');
          menu.innerHTML='<button>Apri pagina</button><button>Rinomina pagina (R)</button><button>Duplica pagina (D)</button><details class="page-editor-thumb-submenu"><summary>Crea e importa pagine</summary><div class="page-editor-thumb-submenu-items"><button>Nuova pagina prima</button><button>Nuova pagina dopo</button></div></details><details class="page-editor-thumb-submenu"><summary>Esporta e dati</summary><div class="page-editor-thumb-submenu-items"><button>Esporta layout JSON</button></div></details>';
          document.body.appendChild(menu);
        }''',pos)
        group=page.get_by_role('group',name='Azioni pagina 1')
        await group.get_by_text('Crea e importa pagine').click()
        await group.get_by_text('Esporta e dati').click()
        actual=await page.evaluate('''()=>{
            const trigger=document.querySelector('.page-editor-thumb-menu-trigger'),menu=document.querySelector('.page-editor-thumb-menu-floating');
            const a=trigger.getBoundingClientRect(),m=menu.getBoundingClientRect();
            const hit=document.elementFromPoint(a.x+a.width/2,a.y+a.height/2);
            const intersects=a.left<m.right&&a.right>m.left&&a.top<m.bottom&&a.bottom>m.top;
            return {hit:hit===trigger,intersects,button:a.toJSON(),menu:m.toJSON()};
        }''')
        assert actual['hit'] and not actual['intersects'],(vw,vh,zoom,actual)
        assert actual['menu']['left']>=-1 and actual['menu']['right']<=vw+1,(vw,vh,zoom,actual)
        await trigger.click(timeout=2500)
        assert await trigger.get_attribute('aria-expanded')=='false'
        assert await group.count()==0
        print(f'PASS RC250 zoomed Chromium {vw}x{vh} rootZoom={zoom}: expanded menu off trigger; native pointer close')
    finally:
        await page.close()

async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(headless=True,args=['--no-sandbox'],executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'))
        try:
            for case in CASES:
                await verify(b,*case)
        finally:
            await b.close()

if __name__=='__main__':asyncio.run(main())
