#!/usr/bin/env python3
"""RC247 real-Chromium geometry and default-face regression (CSS, not CI fixture overrides)."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
KINDS=('rating','reactions','text','shape','line','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count','title','footer')

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  try:
   for width,height in ((390,844),(760,820),(1440,900)):
    page=await browser.new_page(viewport={'width':width,'height':height})
    widget=''.join(f'<div class="widget-canvas-item" data-widget-kind="{kind}" style="font-size:20px"><div class="widget-fit-content"><h3 data-default="true">Titolo</h3><div class="widget-rich-inline"><span data-default="true">Nuova domanda</span></div><div class="canvas-widget-answer-preview" data-answer-mode="multiple"><div class="widget-answer-option"><div class="widget-rich-inline"><span data-default="true">Opzione A</span></div></div></div><button data-default="true" class="canvas-widget-submit-preview">Invia</button><strong data-custom="true" style="font-family:Georgia">Personalizzato</strong></div></div>' for kind in KINDS)
    await page.set_content(f'<div class="app"><section class="editor-ux-v2 powerpoint-editor"><div class="editor-mock-header">Toolbar</div><div class="editor-stage"><div class="editor-canvas-slot"><div class="canvas-with-rulers"><div class="widget-canvas">{widget}</div></div></div></div></section><section class="slide-scheme-workspace">{widget}</section></div>')
    await page.add_style_tag(content=CSS)
    for ui in (80,100,120):
     f=ui*.008
     await page.evaluate('''f=>{document.documentElement.style.zoom=`${f*100}%`;document.documentElement.style.setProperty('--quorivio-ui-scale',String(f));}''',f)
     data=await page.evaluate('''()=>{const box=document.querySelector('.editor-ux-v2').getBoundingClientRect();return {rect:[box.left,box.top,box.width,box.height],fonts:[...document.querySelectorAll('[data-default]')].map(x=>getComputedStyle(x).fontFamily),custom:[...document.querySelectorAll('[data-custom]')].map(x=>getComputedStyle(x).fontFamily)};}''')
     assert abs(data['rect'][0])<2 and abs(data['rect'][1])<2 and abs(data['rect'][2]-width)<3 and abs(data['rect'][3]-height)<3,(width,ui,data['rect'])
     assert len(data['fonts'])==len(KINDS)*2*4 and all('Arial' in f for f in data['fonts']),(width,ui,[f for f in data['fonts'] if 'Arial' not in f][:6])
     assert all('Georgia' in f for f in data['custom']),(width,ui)
     print(f'PASS RC247 Chromium {width}×{height}, UI {ui}%: fullscreen viewport, Arial widget defaults, authored fonts retained')
    await page.close()
  finally:
   await browser.close()

if __name__=='__main__':asyncio.run(main())
