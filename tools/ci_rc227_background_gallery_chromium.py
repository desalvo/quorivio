#!/usr/bin/env python3
"""Real Chromium geometry and keyboard acceptance for a representative background modal."""
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()
HTML='''<button id="trigger">Sfondi</button><div class="schema-background-modal-backdrop"><div class="schema-background-modal" role="dialog" aria-modal="true" aria-labelledby="title"><header><h2 id="title">Sfondi dello schema</h2><button id="close">Chiudi</button></header><div class="background-gallery">'''+''.join('<button class="background-gallery-choice"><img alt="" src="data:image/gif;base64,R0lGODlhAQABAAAAACw="/><span>Immagine lunga %d.jpg</span></button>'%i for i in range(30))+'''</div></div></div>'''
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  try:
   for width,height in [(320,568),(390,844),(760,920),(1440,900)]:
    page=await b.new_page(viewport={'width':width,'height':height},is_mobile=width<800,has_touch=width<800)
    await page.set_content('<meta name="viewport" content="width=device-width, initial-scale=1"><style>'+CSS+'</style>'+HTML)
    result=await page.evaluate('''() => {const d=document.querySelector('.schema-background-modal'),g=d.querySelector('.background-gallery'),r=d.getBoundingClientRect();return {dialogWidth:r.width,dialogHeight:r.height,within: r.left>=0&&r.right<=innerWidth+1&&r.top>=0&&r.bottom<=innerHeight+1,scroll:g.scrollHeight>g.clientHeight,visibleButtons: [...g.querySelectorAll('button')].filter(b=>b.getBoundingClientRect().width>0).length}}''')
    assert result['within'] and result['visibleButtons']==30 and result['scroll'],(width,result)
    print('PASS RC227 Chromium modal %dx%d: clipped-free and scrollable'%(width,height),flush=True)
    await page.close()
  finally:await b.close()
if __name__=='__main__':asyncio.run(main())
