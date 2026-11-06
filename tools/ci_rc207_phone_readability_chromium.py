#!/usr/bin/env python3
"""RC207 real Chromium typography check across editor, rehearsal and public phone.

Uses source CSS and a deterministic DOM fixture. No session credentials, network,
server or personal information. Fails if 1280-cqw inline answer styles ever leak
into the 390px phone stage again.
"""
from __future__ import annotations
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')

answer = 'font-family:Arial;font-size:1.25000cqw;--q-answer-font-family:Arial;--q-answer-font-size:1.25000cqw;--q-phone-answer-font-size:18px'
button = 'font-size:1.25000cqw;min-height:2.81250cqw;--q-phone-submit-font-size:18px;--q-phone-submit-min-height:44px;--q-phone-submit-padding:7px 15px'
input_style = answer + ';height:7.50000cqw;--q-phone-answer-height:96px'
mark = 'font-size:2.10938cqw;--q-inline-phone-font-size:27px'

fixture = f'''<!doctype html><html><head><style>{CSS}</style></head><body>
<div class="editor-ux-v2"><div class="canvas-editor-group" data-canvas-device="phone" style="width:390px;container-type:inline-size">
 <div class="widget-canvas-item" data-widget-kind="question" style="position:relative!important;font-size:22px;--mobile-widget-font-size:22px;width:360px;min-height:480px">
  <div class="widget-fit-frame"><div class="widget-fit-content">
   <div class="widget-rich-inline" id="editor-title">Una domanda in Arial</div>
   <div class="canvas-widget-answer-preview" data-answer-mode="multiple" style="{answer}">
    <label class="widget-answer-option" style="{answer}"><input type="checkbox"><div id="editor-choice" class="widget-rich-inline">Una risposta molto lunga che deve poter andare a capo senza diventare illeggibile.</div></label>
   </div>
   <textarea id="editor-field" class="widget-free-answer-field" style="{input_style}"></textarea>
   <button id="editor-button" class="canvas-widget-submit-preview" style="{button}">Invia risposta</button>
   <div class="widget-rich-inline"><span id="editor-mark" style="{mark}">Testo personalizzato</span></div>
  </div></div></div></div></div>
<div class="rehearsal-phone-stage" style="width:390px;position:relative;height:490px;transform:none">
 <div class="rehearsal-widget" data-widget-kind="question" style="--mobile-widget-font-size:22px;--stage-x:0%;--stage-y:0%;--stage-width:100%;--stage-height:100%">
  <section class="projection-interactive-widget">
   <strong id="rehearsal-title">Una domanda in Arial</strong>
   <label class="widget-answer-option" style="{answer}"><input type="radio"><span id="rehearsal-choice">Risposta che rimane leggibile</span></label>
   <textarea id="rehearsal-field" class="widget-free-answer-field" style="{input_style}"></textarea>
   <button id="rehearsal-button" class="outline small" style="{button}">Invia risposta</button>
  </section>
 </div>
</div>
<div class="audience-widget-layout stage-phone" style="width:390px;position:relative;height:490px">
 <div class="page-widget" data-widget-kind="question" style="--mobile-widget-font-size:22px;--stage-x:0%;--stage-y:0%;--stage-width:100%;--stage-height:100%">
  <section class="widget-question">
   <strong id="public-title">Una domanda in Arial</strong>
   <label class="widget-answer-option" style="{answer}"><input type="checkbox"><span id="public-choice">Risposta che rimane leggibile</span></label>
   <textarea id="public-field" class="widget-free-answer-field" style="{input_style}"></textarea>
   <button id="public-button" class="outline small" style="{button}">Invia risposta</button>
   <label class="widget-answer-option" style="{answer.replace('18px', '26px')}"><input type="checkbox"><span id="public-custom">Dimensione personalizzata 26</span></label>
  </section>
 </div>
</div></body></html>'''

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        try:
            page=await browser.new_page(viewport={'width':1440,'height':900})
            await page.set_content(fixture)
            for surface in ('editor','rehearsal','public'):
                for kind,minimum in (('title',20),('choice',18),('field',18),('button',18)):
                    size=await page.locator(f'#{surface}-{kind}').evaluate('(el)=>parseFloat(getComputedStyle(el).fontSize)')
                    assert size >= minimum-.15,(surface,kind,size,minimum)
                height=await page.locator(f'#{surface}-button').evaluate('(el)=>el.getBoundingClientRect().height')
                assert height >= 43.5,(surface,'button-height',height)
                area=await page.locator(f'#{surface}-field').evaluate('(el)=>el.getBoundingClientRect().height')
                assert area >= 75,(surface,'field-height',area)
            mark_size=await page.locator('#editor-mark').evaluate('(el)=>parseFloat(getComputedStyle(el).fontSize)')
            assert abs(mark_size-27)<.2,('explicit inline font size',mark_size)
            custom=await page.locator('#public-custom').evaluate('(el)=>parseFloat(getComputedStyle(el).fontSize)')
            assert abs(custom-26)<.2,('explicit answer override',custom)
            print('PASS RC207 real Chromium: editor, rehearsal and public phone title >=20px, answer/input/button >=18px, button >=44px, inline mark 27px, custom answer 26px')
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(verify())
