#!/usr/bin/env python3
"""Real Chromium CSS hit-testing for the RC249 portaled thumbnail toggle.

The full CI also runs ci_browser_editor.py against compiled React/PostgreSQL;
this standalone check isolates the menu geometry without mock/network timing.
"""
import asyncio
import json
import os
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
CASES=[(320,240,10,12),(320,240,276,189),(390,844,70,48),(390,844,340,740),
       (760,820,180,80),(960,760,120,200),(1440,900,65,60),(1440,900,1350,820)]

def positions():
    # Execute the *shipped TypeScript layout helper* in Node, not a Python copy.
    data=[{'vw':w,'vh':h,'anchor':{'left':x,'right':x+34,'top':y,'bottom':y+34}}
          for w,h,x,y in CASES]
    source='''import {thumbnailMenuPosition} from './apps/web/src/thumbnail-menu-layout.ts';
    const cases=JSON.parse(process.argv[1]);
    process.stdout.write(JSON.stringify(cases.map(({vw,vh,anchor}) =>
       thumbnailMenuPosition(anchor.right+8,anchor.top,vw,vh,anchor))));'''
    proc=subprocess.run(['node','--experimental-strip-types','--input-type=module','-e',source,json.dumps(data)],
                        cwd=ROOT,capture_output=True,text=True,check=True)
    return json.loads(proc.stdout)

async def verify(browser,case,position):
    width,height,left,top=case
    page=await browser.new_page(viewport={'width':width,'height':height})
    try:
        styles=f'''position:fixed;left:{left}px;top:{top}px;right:auto;width:34px;height:34px;'''
        menu_style=(f'''position:fixed;left:{position['left']}px;top:{position['top']}px;'''
                    f'''max-height:{position['maxHeight']}px;--thumbnail-menu-width:{position['width']}px;'''
                    f'''--thumbnail-menu-max-height:{position['maxHeight']}px''')
        html=f'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
        <style>{CSS}</style></head><body>
        <div class="editor-ux-v2"><button class="page-editor-thumb-menu-trigger" aria-label="Menu pagina 1: crea, duplica, elimina, sposta" aria-expanded="true" style="{styles}" onclick="this.dataset.clicked='true'">…</button></div>
        <div class="page-editor-thumb-menu page-editor-thumb-menu-floating" role="group" aria-label="Azioni pagina 1" style="{menu_style}">
        <button>Apri pagina</button><button>Rinomina pagina (R)</button><button>Duplica pagina (D)</button>
        <details class="page-editor-thumb-submenu"><summary>Crea e importa pagine</summary><button>Nuova pagina dopo</button></details>
        </div></body></html>'''
        await page.set_content(html)
        state=await page.evaluate('''() => {
          const b=document.querySelector('.page-editor-thumb-menu-trigger'),
                menu=document.querySelector('.page-editor-thumb-menu-floating');
          const a=b.getBoundingClientRect(),m=menu.getBoundingClientRect();
          const hit=document.elementFromPoint(a.x+a.width/2,a.y+a.height/2);
          return {button:a.toJSON(),menu:m.toJSON(),hit:hit===b,
            width:getComputedStyle(menu).width};
        }''')
        a,m=state['button'],state['menu']
        assert state['hit'],(case,state)
        assert m['x']>=7 and m['right']<=width-7 and m['y']>=7 and m['bottom']<=height-7,(case,state)
        assert a['right']<=m['x']+1 or m['right']<=a['x']+1 or a['bottom']<=m['y']+1 or m['bottom']<=a['y']+1,(case,state)
        # Actual pointer targeting, not force=True or synthetic DOM clicks.
        await page.get_by_role('button',name='Menu pagina 1: crea, duplica, elimina, sposta').click(timeout=2000)
        assert await page.locator('.page-editor-thumb-menu-trigger').get_attribute('data-clicked')=='true'
        print(f'PASS RC249 Chromium {width}x{height} anchor=({left},{top}): popup avoids trigger, real click succeeds')
    finally:
        await page.close()

async def main():
    geometry=positions()
    async with async_playwright() as playwright:
        opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {'executable_path':'/usr/bin/chromium'}
        browser=await playwright.chromium.launch(headless=True,args=['--no-sandbox'],**opts)
        try:
            for case,position in zip(CASES,geometry,strict=True):
                await verify(browser,case,position)
        finally:
            await browser.close()

if __name__=='__main__':asyncio.run(main())
