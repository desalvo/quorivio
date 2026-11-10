#!/usr/bin/env python3
"""RC296: Chromium CSS/DOM geometry for responsive mobile pie legends.

This verifies the shipped stylesheet on representative authored markup, not
real device, WebKit, running-app or PostgreSQL end-to-end acceptance.
"""
from __future__ import annotations
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
ITEMS=''.join(
 '<div class="linked-results-pie-mobile-item" role="listitem">'
 '<span class="linked-results-pie-mobile-swatch" aria-hidden="true"></span>'
 f'<span class="linked-results-pie-mobile-name">{i}. Risposta troppo lunga per una sola riga</span>'
 '<strong class="linked-results-pie-mobile-percent">8.33%</strong></div>'
 for i in range(1,13)
)

async def run():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(
   executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),
   headless=True,args=['--no-sandbox'])
  cases=[
   ('desktop',1000,'',False),
   ('phone-390',390,'',True),
   ('phone-360',360,'',True),
   ('editor-phone-at-desktop-width',1000,'<div class="editor-ux-v2"><div class="canvas-editor-group" data-canvas-device="phone">',True),
   ('audience-phone-at-desktop-width',1000,'<div class="audience-widget-layout stage-phone">',True),
  ]
  for name,width,wrapper,visible in cases:
   page=await browser.new_page(viewport={'width':width,'height':820})
   suffix='</div>'*wrapper.count('<div')
   markup=(
    '<style>'+CSS+'</style><main style="width:min(100%,340px)">'
    +wrapper
    +'<div class="widget-canvas-item page-widget rehearsal-widget" data-widget-kind="results-button">'
    +'<section class="linked-results result-view-pie" style="width:100%;height:auto;font:18px Arial">'
    +'<svg class="linked-results-pie linked-results-pie-chart" data-mobile-percent-labels="true" viewBox="0 0 500 320">'
    +'<g class="linked-results-pie-callout"><text x="380" y="100">8.33%</text></g></svg>'
    +'<div class="linked-results-pie-mobile-legend" role="list" aria-label="Percentuali delle risposte">'
    +ITEMS+'</div></section></div>'+suffix+'</main>')
   await page.set_content(markup)
   d=await page.evaluate("""() => {
    const legend=document.querySelector('.linked-results-pie-mobile-legend');
    const svg=document.querySelector('.linked-results-pie-chart');
    const labels=[...legend.querySelectorAll('.linked-results-pie-mobile-percent')];
    const callout=document.querySelector('.linked-results-pie-callout');
    const b=svg.getBoundingClientRect();
    return {visible:getComputedStyle(legend).display==='grid' && getComputedStyle(legend).clipPath==='none' && legend.getBoundingClientRect().width>5,
     count:labels.length,
     minFont:Math.min(...labels.map(x=>parseFloat(getComputedStyle(x).fontSize))),
     overflow:legend.scrollWidth>legend.clientWidth+1,
     ratio:b.width/b.height,callout:getComputedStyle(callout).display!=='none'};
   }""")
   assert d['visible'] is visible,(name,d)
   assert d['count']==12 and not d['overflow'],(name,d)
   if visible:
    assert d['minFont']>=14,(name,d)
    assert not d['callout'],(name,d)
    assert abs(d['ratio']-500/320)<0.05,(name,d)
   else:
    assert d['callout'],(name,d)
   print('RC296 Chromium PASS',name,d)
   await page.close()
  await browser.close()

if __name__=='__main__':
 asyncio.run(run())
