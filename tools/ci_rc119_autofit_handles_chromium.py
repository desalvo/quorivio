#!/usr/bin/env python3
"""Real Chromium CSS regression: resize chrome must not cause auto-fit growth.

This isolates the geometry that made the RC118 browser fixture grow to the
canvas edge. It runs before the slower compiled-React acceptance but cannot
replace that end-to-end acceptance.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
STYLE=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
HTML='''<div class="powerpoint-editor editor-ux-v2"><div class="widget-canvas" style="position:relative;width:960px;height:540px;overflow:visible;max-width:none">
<div data-selected="true" data-widget-kind="text" class="widget-canvas-item" style="left:10%;top:10%;width:20%;height:20%">
<div class="widget-fit-frame"><div class="widget-fit-content"><div class="widget-rich-inline">First</div></div></div>
<button class="widget-resize-edge edge-se"></button><button class="widget-resize-edge edge-s"></button>
<button class="widget-resize-edge edge-sw"></button><button class="widget-rotate-handle"></button>
</div></div></div>'''

async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  try:
   for width in (1440,390):
    page=await browser.new_page(viewport={'width':width,'height':940})
    try:
     await page.set_content('<style>'+STYLE+'</style>'+HTML)
     m=await page.evaluate('''() => {
       const node=document.querySelector('.widget-canvas-item');
       const frame=node.querySelector(':scope > .widget-fit-frame');
       const body=frame.querySelector(':scope > .widget-fit-content');
       return {legacy:node.scrollHeight-node.clientHeight,content:body.scrollHeight-frame.clientHeight,
         frameHeight:frame.clientHeight,bodyHeight:body.scrollHeight};
     }''')
     assert m['legacy']>2, f'Expected protruding handles to expose outer scrollHeight bug: {m}'
     assert m['content']<=2, f'Short text falsely overflows its inner frame: {m}'
     print(f'PASS RC119 Chromium {width}px: outer handles generate {m["legacy"]}px false overflow, '
           f'inner text overflow <=2px (measured {m["content"]}px)',flush=True)
    finally:
     await page.close()
  finally:
   await browser.close()

if __name__=='__main__':asyncio.run(main())
