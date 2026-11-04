#!/usr/bin/env python3
"""Real Chromium layout for RC160: authored controls only, footer last, white comment."""
from pathlib import Path
import os
import shutil
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
HTML='''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>
<div class="audience-widget-layout stage-reading" id="reading">
 <div class="page-widget" data-widget-kind="footer"><div class="projection-slide-footer"><span class="slide-footer-center">Footer della prova</span></div></div>
 <div class="page-widget" data-widget-kind="title"><h2>Titolo della presentazione</h2></div>
 <div class="page-widget" data-widget-kind="rating"><label class="rating-comment-field">Commento facoltativo<textarea class="rating-comment-input" rows="2" aria-label="Commento facoltativo"></textarea></label></div>
 <span class="slide-canvas-page-number">1</span>
</div>
<div class="audience-widget-layout stage-phone" id="phone" style="height:720px!important;width:390px!important">
 <div class="page-widget" data-widget-kind="footer" style="--stage-x:4%;--stage-y:87.777%;--stage-width:92%;--stage-height:8.889%">Footer smartphone</div>
 <div class="page-widget" data-widget-kind="title" style="--stage-x:4%;--stage-y:3.333%;--stage-width:92%;--stage-height:12.5%">Titolo smartphone</div>
 <div class="page-widget" data-widget-kind="rating" style="--stage-x:4%;--stage-y:30%;--stage-width:92%;--stage-height:31%"><label class="rating-comment-field">Commento facoltativo<textarea class="rating-comment-input"></textarea></label></div>
</div>
<div class="widget-canvas-item" data-widget-kind="rating"><label class="rating-comment-field">Commento facoltativo<textarea class="rating-comment-input" readonly></textarea></label></div>
<div class="rehearsal-widget" data-widget-kind="rating"><label class="rating-comment-field">Commento facoltativo<textarea class="rating-comment-input" readonly></textarea></label></div>
<div class="projection-widget" data-widget-kind="rating"><label class="rating-comment-field">Commento facoltativo<textarea class="rating-comment-input" readonly></textarea></label></div>
</body></html>'''

def run():
 browser_path=os.environ.get('QUORIVIO_CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
 if not browser_path: raise RuntimeError('Chromium required for RC160 geometry regression')
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=browser_path,headless=True,args=['--no-sandbox'])
  try:
   for width in (1440,390):
    page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
    page.set_content(HTML)
    page.add_style_tag(content=CSS)
    result=page.evaluate('''() => {
     const rect = el => {const r=el.getBoundingClientRect();return {top:r.top,bottom:r.bottom}};
     const reading=document.querySelector('#reading'),phone=document.querySelector('#phone');
     const colors=[...document.querySelectorAll('textarea.rating-comment-input')].map(el=>({background:getComputedStyle(el).backgroundColor,color:getComputedStyle(el).color,visible:getComputedStyle(el).visibility}));
     return {readingTitle:rect(reading.querySelector('[data-widget-kind="title"]')),
       readingRating:rect(reading.querySelector('[data-widget-kind="rating"]')),
       readingFooter:rect(reading.querySelector('[data-widget-kind="footer"]')),
       readingNumber:rect(reading.querySelector('.slide-canvas-page-number')),
       phoneTitle:rect(phone.querySelector('[data-widget-kind="title"]')),
       phoneRating:rect(phone.querySelector('[data-widget-kind="rating"]')),
       phoneFooter:rect(phone.querySelector('[data-widget-kind="footer"]')),
       colors};
    }''')
    assert result['readingFooter']['top']>=result['readingRating']['bottom']-1,(width,result)
    assert result['readingNumber']['top']>=result['readingFooter']['bottom']-1,(width,result)
    assert result['phoneFooter']['top']>=result['phoneRating']['bottom']-1,(width,result)
    assert all(x['background']=='rgb(255, 255, 255)' and x['color']=='rgb(20, 43, 68)' and x['visible']=='visible' for x in result['colors']),(width,result)
    print(f'PASS RC160 Chromium {width}px: footer last in reading/phone; {len(result["colors"])} shared rating fields white and legible')
    page.close()
  finally:browser.close()

if __name__=='__main__':run()
