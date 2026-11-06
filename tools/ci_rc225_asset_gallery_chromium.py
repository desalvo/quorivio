#!/usr/bin/env python3
"""RC225 actual CSS: master background image and thumbnail library remain usable on narrow screens."""
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()
HTML='''<main class="slide-scheme-canvas"><div class="canvas-with-rulers"><div class="widget-canvas" style="--editor-page-background: url(\'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%223%22 height=%223%22%3E%3Crect width=%223%22 height=%223%22 fill=%22%23f00%22/%3E%3C/svg%3E\')"></div></div></main><div class="background-gallery" role="group" aria-label="Scegli sfondo">'''+''.join('<button type="button" class="background-gallery-choice" aria-pressed="false"><img alt="" src="data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs="/><span>Foto molto lunga numero '+str(n)+'.jpg</span></button>' for n in range(25))+'</div>'

async def run():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for width,height in [(320,240),(390,844),(1440,900)]:
    page=await browser.new_page(viewport={'width':width,'height':height})
    await page.set_content('<html><head><style>'+CSS+'</style></head><body>'+HTML+'</body></html>')
    gallery=page.get_by_role('group',name='Scegli sfondo')
    summary=await page.evaluate('''() => {
      const c=document.querySelector('.slide-scheme-canvas .widget-canvas');
      const g=document.querySelector('.background-gallery');
      const last=g.lastElementChild;g.scrollTop=g.scrollHeight;
      return {background:getComputedStyle(c).backgroundImage,scrollable:g.scrollHeight>g.clientHeight,
      lastVisible:last.getBoundingClientRect().bottom<=g.getBoundingClientRect().bottom+2,
      fits:g.getBoundingClientRect().right<=window.innerWidth+1,
      filename:!!last.querySelector('span')?.textContent.includes('.jpg')};
    }''')
    assert 'data:image/svg+xml' in summary['background'],summary
    assert all(summary[k] for k in ['scrollable','lastVisible','fits','filename']),summary
    print(f'PASS RC225 Chromium {width}x{height}: master background and scrollable named thumbnails')
    await page.close()
  finally:await browser.close()
if __name__=='__main__':asyncio.run(run())
