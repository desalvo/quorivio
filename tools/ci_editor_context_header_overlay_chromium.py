#!/usr/bin/env python3
"""Offline real-Chromium regression for an editor popover under the fixed header.

Checks both contextual popovers using real pointer clicks (no DOM clicks/force).
Run 40589103128 failed because editor-mock-header covered the selection entry.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from ci_editor_context_tools import click_canvas_tool, open_canvas_context

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
HTML = '''<!doctype html><html><head><style>@CSS@
body{margin:0;background:#0b1b2b}
.editor-ux-v2{width:100vw;height:100dvh;position:relative}
.editor-ux-v2 .editor-mock-header{position:fixed;top:0;left:0;right:0;height:60px;z-index:140;background:#101827}
.editor-ux-v2 .editor-stage{position:absolute;left:clamp(54px,15vw,220px);right:clamp(88px,10vw,158px);top:45px;height:calc(100dvh - 60px);overflow:auto;padding:0!important;display:block;z-index:1}
.editor-ux-v2 .editor-canvas-slot{width:100%;position:relative;margin-top:-90px!important}
.editor-ux-v2 .canvas-editor-group{position:relative;width:100%}
.editor-ux-v2 .widget-canvas{height:450px!important;min-height:0!important;aspect-ratio:auto!important;background:#fafafa}
.canvas-background-context{display:none}
.canvas-context-test-spacer{height:800px}
</style></head><body><div class="editor-ux-v2">
<header class="editor-mock-header" aria-label="Intestazione editor">Quorivio editor</header>
<main class="editor-stage"><div class="editor-canvas-slot"><div class="canvas-editor-group" data-tools-open="false">
<div class="canvas-editor-tools"><button type="button">Copia selezione</button></div>
<div class="canvas-editor-tools" role="group" aria-label="Allineamento widget selezionati">
  <button>Allinea</button><div class="canvas-editor-tools" role="group" aria-label="Ordine e spostamento widget selezionati">
  <button id="nudge">Sposta selezione a destra</button></div>
</div>
<div class="canvas-with-rulers"><div class="widget-canvas" role="group" aria-label="Canvas grafico widget">
 <div class="canvas-background-context" role="group" aria-label="Menu contestuale sfondo canvas">
  <button id="tools">Strumenti di selezione e allineamento</button><button id="close">Chiudi menu</button>
 </div>
</div></div></div></div><div class="canvas-context-test-spacer"></div></main></div>
<script>
const menu=document.querySelector('.canvas-background-context'),group=document.querySelector('.canvas-editor-group');
document.querySelector('.widget-canvas').addEventListener('contextmenu',event=>{
 event.preventDefault();menu.style.display='grid';group.dataset.toolsOpen='false';
});
document.querySelector('#tools').addEventListener('click',()=>{menu.style.display='none';group.dataset.toolsOpen='true'});
document.querySelector('#close').addEventListener('click',()=>{menu.style.display='none'});
document.querySelector('#nudge').addEventListener('click',()=>{document.body.dataset.nudges=String(1+Number(document.body.dataset.nudges||0))});
</script></body></html>'''.replace('@CSS@',CSS)

async def assert_hit(page,locator):
    await expect(locator).to_be_visible()
    bounds=await locator.bounding_box()
    assert bounds, 'Expected visible contextual action'
    assert bounds['y'] >= 60, ('Menu entered editor header area', bounds)
    hit=await locator.evaluate('el => {const b=el.getBoundingClientRect(),e=document.elementFromPoint(b.left+b.width/2,b.top+b.height/2); return Boolean(e && (e===el || el.contains(e)))}')
    assert hit, ('Pointer intercepted before real click',bounds)

async def verify(browser,w,h,touch):
    page=await browser.new_page(viewport={'width':w,'height':h},has_touch=touch,is_mobile=touch)
    page.set_default_timeout(5000)
    try:
        await page.set_content(HTML)
        # Expanded responsive content can place the artboard top behind the
        # header. This deliberate overlap reproduces the failing geometry.
        await page.evaluate("document.querySelector('.editor-stage').scrollTop=22")
        await open_canvas_context(page)
        entry=page.get_by_role('button',name='Strumenti di selezione e allineamento')
        await assert_hit(page,entry)
        await click_canvas_tool(page,'Sposta selezione a destra')
        assert await page.evaluate('document.body.dataset.nudges')=='1'
        # Menu reopens with a real right click even after scrolling and one
        # arrangement command. Previously the header intercepted this entry.
        await open_canvas_context(page)
        await assert_hit(page,entry)
        await click_canvas_tool(page,'Sposta selezione a destra')
        assert await page.evaluate('document.body.dataset.nudges')=='2'
    finally:
        await page.close()

async def main():
    async with async_playwright() as pw:
        launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'],**launch)
        try:
            await verify(browser,1440,940,False)
            await verify(browser,390,844,True)
        finally:
            await browser.close()
    print('PASS fixed editor header contextual popover and arrangement panel: desktop+mobile genuine Chromium clicks')

if __name__=='__main__':asyncio.run(main())
