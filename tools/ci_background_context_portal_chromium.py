#!/usr/bin/env python3
"""RC102: viewport clickability of the real floating-background-menu CSS.

The fixture models the clipping/transform of a 16:9 editor stage. It verifies
native pointer hit-testing for a popover moved to document.body. This does not
replace the full built-React browser acceptance run in CI.
"""
from __future__ import annotations
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
HTML = '''<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>
@CSS@
body{margin:0}.editor-ux-v2{height:100dvh}.editor-mock-header{position:fixed;z-index:200;top:0;left:0;right:0;height:64px;background:#10253d}
.editor-stage{position:absolute;inset:80px 10px 10px;overflow:hidden;transform:translateZ(0);background:#eef2f7}
.widget-canvas{height:600px;background:white}.editor-mock-cover{position:fixed;top:64px;left:0;right:0;height:6px;z-index:9999}
</style></head><body>
<div class="editor-ux-v2"><header class="editor-mock-header">Editor</header>
<main class="editor-stage"><div class="widget-canvas" role="group" aria-label="Canvas grafico widget">Canvas</div></main></div>
<div class="canvas-background-context canvas-background-context-floating" role="group" aria-label="Menu contestuale sfondo canvas"><strong>Menu della pagina</strong>
<button id="tools">Strumenti di selezione e allineamento</button><button id="close">Chiudi menu</button></div>
<script>
window.clicked=0;
document.querySelector('#tools').addEventListener('click',()=>window.clicked++);
document.querySelector('#close').addEventListener('click',()=>document.querySelector('.canvas-background-context-floating').remove());
</script></body></html>'''.replace('@CSS@', CSS)

async def verify(browser, width:int, height:int, touch:bool)->None:
    page=await browser.new_page(viewport={'width':width,'height':height},has_touch=touch,is_mobile=touch)
    page.set_default_timeout(5000)
    try:
        await page.set_content(HTML)
        button=page.get_by_role('button',name='Strumenti di selezione e allineamento')
        await expect(button).to_be_visible()
        metrics=await button.evaluate('''el=>{
          const r=el.getBoundingClientRect(),m=el.closest('.canvas-background-context-floating');
          const b=m.getBoundingClientRect(), hit=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
          return {x:r.left,y:r.top,right:r.right,bottom:r.bottom,menuTop:b.top,menuBottom:b.bottom,
            menuRight:b.right,parentBody:m.parentElement===document.body,
            hit:hit===el||el.contains(hit),height:innerHeight,width:innerWidth};
        }''')
        assert metrics['parentBody'], metrics
        assert metrics['hit'] and metrics['y']>=64 and metrics['bottom']<=height+1, metrics
        assert metrics['menuTop']>=64 and metrics['menuRight']<=width+1 and metrics['menuBottom']<=height+1, metrics
        if touch:
            await button.tap()
        else:
            await button.click()
        assert await page.evaluate('window.clicked')==1
        await page.get_by_role('button',name='Chiudi menu').click()
        await expect(page.get_by_role('group',name='Menu contestuale sfondo canvas')).to_have_count(0)
    finally:
        await page.close()

async def main()->None:
    async with async_playwright() as pw:
        launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'],**launch)
        try:
            await verify(browser,1440,900,False)
            await verify(browser,390,844,True)
        finally:
            await browser.close()
    print('PASS RC102 floating canvas context menu: viewport geometry and real desktop/touch pointer')

if __name__=='__main__':asyncio.run(main())
