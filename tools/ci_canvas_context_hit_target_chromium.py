#!/usr/bin/env python3
"""Actual browser regression for the editor canvas/context hit target after scroll.

Reproduces run 40549836288: the fixed editor header overlaps the top-left
canvas pixels, while the rest of the artboard is clickable. No synthetic DOM
clicks, Playwright force options, or removed visible trigger buttons are used.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect, TimeoutError as PlaywrightTimeoutError
from ci_editor_context_tools import open_canvas_context, click_canvas_tool, close_canvas_tools, canvas_background_point

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
HTML='''<!doctype html><html><head><style>@CSS@
body { margin:0; background:#102034; }
.fixed-overlay { position:fixed; z-index:9999; top:0; left:0; right:0; height:110px; background:#122539; color:white; }
.editor-stage { position:absolute; top:45px; left:clamp(95px,18vw,258px); right:clamp(60px,11vw,170px); height:720px; overflow:auto; }
.widget-canvas { position:relative!important; width:100%!important; height:480px!important; min-height:0!important; aspect-ratio:auto!important; background:#f2f6ff; }
.widget-canvas-item { position:absolute; background:#dfebf6; }
.canvas-background-context { display:none; position:absolute; left:5%; top:25%; background:white; z-index:4; padding:10px; }
.canvas-editor-tools { display:none; background:#d7ecfd; color:#162537; }
.canvas-editor-tools[data-open="true"] { display:block; }
</style></head><body>
<header class="fixed-overlay editor-mock-header"><div class="editor-mock-brand">Quorivio editor header covers top of canvas</div></header>
<main class="editor-stage"><div class="widget-canvas" role="group" aria-label="Canvas grafico widget">
<div class="widget-canvas-item" style="left:14%;top:28%;width:20%;height:22%">Widget A</div>
<div class="widget-canvas-item" style="left:44%;top:36%;width:19%;height:23%">Widget B</div>
<div class="widget-canvas-item" style="left:78%;top:60%;width:20%;height:18%">Widget C</div>
<div class="canvas-background-context" role="group" aria-label="Menu contestuale sfondo canvas"><button id="open-tools">Strumenti di selezione e allineamento</button></div>
</div><div class="canvas-editor-tools" role="group" aria-label="Allineamento widget selezionati" data-open="false">
<div role="group" aria-label="Ordine e spostamento widget selezionati"><button id="move">Sposta selezione a destra</button></div></div>
</main>
<script>
const canvas=document.querySelector('.widget-canvas'), menu=document.querySelector('.canvas-background-context');
const tools=document.querySelector('[aria-label="Allineamento widget selezionati"]');
canvas.addEventListener('contextmenu',e=>{e.preventDefault();if(e.target.closest('.widget-canvas-item'))return;
  menu.style.display='block';tools.dataset.open='false';});
document.querySelector('#open-tools').onclick=()=>{menu.style.display='none';tools.dataset.open='true';};
document.querySelector('#move').onclick=()=>{document.body.dataset.moved=String(1+Number(document.body.dataset.moved||0));};
</script></body></html>'''.replace('@CSS@',CSS)

async def verify(browser,w,h,touch):
    page=await browser.new_page(viewport={'width':w,'height':h},has_touch=touch,is_mobile=touch)
    page.set_default_timeout(1700)
    try:
        await page.set_content(HTML,wait_until='load')
        canvas=page.get_by_role('group',name='Canvas grafico widget')
        await expect(canvas).to_be_visible()
        # The former fixed corner is physically covered by a real header.
        old=await canvas.evaluate('el => { const r=el.getBoundingClientRect(); return document.elementFromPoint(r.left+7,r.top+7)?.closest("header")!==null }')
        assert old, 'Regression setup must physically cover the former 7px canvas corner'
        try:
            await canvas.click(button='right',position={'x':7,'y':7},timeout=800)
        except PlaywrightTimeoutError:
            pass
        else:
            raise AssertionError('Obstructed 7px canvas corner unexpectedly accepted a real browser click')
        point=await canvas_background_point(page)
        assert point['y']>110,('Selected point under fixed header',point)
        await open_canvas_context(page)
        await expect(page.get_by_role('button',name='Strumenti di selezione e allineamento')).to_be_visible()
        await click_canvas_tool(page,'Sposta selezione a destra')
        assert await page.evaluate('document.body.dataset.moved')=='1'
        await close_canvas_tools(page)
        await expect(page.get_by_role('group',name='Allineamento widget selezionati')).to_be_hidden()
        # Verify the menu can be reentered after a previous action and close.
        await click_canvas_tool(page,'Sposta selezione a destra')
        assert await page.evaluate('document.body.dataset.moved')=='2'
    finally:
        await page.close()

async def main():
    async with async_playwright() as pw:
        opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'],**opts)
        try:
            await verify(browser,1440,900,False)
            await verify(browser,390,844,True)
        finally:
            await browser.close()
    print('PASS Chromium fixed-header obscured canvas corner: actual background hit-target, right-click, contextual tools, close/reopen, desktop+touch viewport')

if __name__=='__main__':asyncio.run(main())
