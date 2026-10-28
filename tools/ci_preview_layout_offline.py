#!/usr/bin/env python3
"""Network-free real Chromium geometry preflight for dual 16:9 rehearsal panes.

This checks actual CSS hit targets, not authenticated end-to-end app wiring.
GitHub's database-backed Chromium tests are still required for RC acceptance.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

CSS=Path(__file__).resolve().parents[1].joinpath('apps/web/src/style.css').read_text()
HTML='''<html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>
<div class="rehearsal-backdrop"><div class="rehearsal-shell rehearsal-mode-both" style="height:90vh">
<header class="rehearsal-toolbar">Anteprime affiancate</header><div class="rehearsal-stage">
<div class="rehearsal-panes"><div class="rehearsal-pane"><strong class="rehearsal-pane-heading">Presentatore</strong><section class="rehearsal-slide"><div class="rehearsal-widgets"><div class="rehearsal-widget" style="--stage-x:10%;--stage-y:10%;--stage-width:30%;--stage-height:30%">Risultati</div></div></section></div>
<div class="rehearsal-pane"><strong class="rehearsal-pane-heading">Partecipante</strong><section class="rehearsal-slide"><div class="rehearsal-widgets"><div class="rehearsal-widget" style="--stage-x:10%;--stage-y:10%;--stage-width:30%;--stage-height:30%"><button id="reaction" type="button" aria-pressed="false" onclick="this.setAttribute('aria-pressed','true')">❤️</button></div></div></section></div></div>
</div><footer class="rehearsal-footer">Prova locale</footer></div></div></body></html>'''
async def main():
 async with async_playwright() as playwright:
  opts={'headless':True,'args':['--no-sandbox']}
  binary=os.environ.get('QUORIVIO_CHROMIUM_PATH') or '/usr/bin/chromium'
  if Path(binary).exists():opts['executable_path']=binary
  browser=await playwright.chromium.launch(**opts)
  try:
   for width,height in [(1440,900),(390,844)]:
    page=await browser.new_page(viewport={'width':width,'height':height})
    await page.set_content(HTML)
    await page.add_style_tag(content=CSS)
    result=await page.evaluate('''() => {
      const slides=[...document.querySelectorAll('.rehearsal-pane>.rehearsal-slide')];
      const widgets=[...document.querySelectorAll('.rehearsal-widgets>.rehearsal-widget')];
      return {slides:slides.map(s=>{const r=s.getBoundingClientRect();return {w:r.width,h:r.height}}),widgets:widgets.map(w=>{const p=w.parentElement.getBoundingClientRect(),r=w.getBoundingClientRect();return {x:(r.left-p.left)/p.width*100,y:(r.top-p.top)/p.height*100,w:r.width/p.width*100,h:r.height/p.height*100}}),columns:document.querySelectorAll('.rehearsal-pane').length};
    }''')
    assert result['columns']==2,result
    for slide in result['slides']:
     assert abs(slide['w']/slide['h']-16/9)<.04,(width,result)
    for widget in result['widgets']:
     for key,expected in [('x',10),('y',10),('w',30),('h',30)]:assert abs(widget[key]-expected)<1,(width,key,widget)
    await page.get_by_role('button',name='❤️').click()
    assert await page.get_by_role('button',name='❤️').get_attribute('aria-pressed')=='true'
    await page.close()
   print('PASS offline Chromium dual presenter/participant 16:9 layout, widget geometry and real reaction pointer: desktop+mobile')
  finally:await browser.close()
if __name__=='__main__':asyncio.run(main())
