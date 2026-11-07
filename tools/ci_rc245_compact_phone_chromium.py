#!/usr/bin/env python3
"""RC245 real Chromium CSS fixture: compact question, readable touch rows.

This complements (not replaces) the authenticated PostgreSQL/React participant
browser acceptance. No network, account, database or production endpoint.
"""
from __future__ import annotations
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
HTML='''<!doctype html><html><head><style>{css}</style></head><body>
<div class="audience-widget-layout stage-phone" style="height:720px;width:390px">
 <div class="page-widget" data-widget-kind="question" style="--stage-x:4%;--stage-y:16%;--stage-width:92%;--stage-height:33.0556%;--mobile-widget-font-size:20px">
  <section class="widget-question" style="display:flex;flex-direction:column;gap:8px">
   <strong>Una domanda leggibile</strong>
   <label class="widget-answer-option" style="display:flex;--q-phone-answer-font-size:18px"><input type="radio" name="choice"><span>Prima opzione</span></label>
   <label class="widget-answer-option" style="display:flex;--q-phone-answer-font-size:18px"><input type="radio" name="choice"><span>Seconda opzione</span></label>
   <button type="button" class="outline small" style="--q-phone-submit-font-size:18px;--q-phone-submit-min-height:44px">Invia risposta</button>
  </section>
 </div>
</div></body></html>'''

async def verify():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  try:
   for width in (320,390,760):
    page=await browser.new_page(viewport={'width':width,'height':844})
    await page.set_content(HTML.format(css=CSS))
    measurements=await page.locator('.page-widget[data-widget-kind="question"]').evaluate('''el=>{
      const box=el.getBoundingClientRect(), rows=[...el.querySelectorAll('.widget-answer-option')];
      return {height:box.height,rows:rows.map(r=>({height:r.getBoundingClientRect().height,font:parseFloat(getComputedStyle(r).fontSize)})),
      submitHeight:el.querySelector('button').getBoundingClientRect().height};
    }''')
    assert abs(measurements['height']-238)<1.5, (width,measurements)
    assert len(measurements['rows'])==2,(width,measurements)
    assert all(row['height']>=43.5 and row['font']>=17.5 for row in measurements['rows']),(width,measurements)
    assert measurements['submitHeight']>=43.5,(width,measurements)
    print(f'PASS RC245 Chromium {width}px: compact 238px question; two touch rows >=44px, 18px fonts, submit >=44px')
    await page.close()
  finally:
   await browser.close()

if __name__=='__main__':
 asyncio.run(verify())
