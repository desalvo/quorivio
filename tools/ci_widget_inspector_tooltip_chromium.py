#!/usr/bin/env python3
"""Isolated real-Chromium visual regression for unclipped tooltips/answer option order.

The real React+PostgreSQL end-to-end browser test remains in GitHub CI.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()
HTML='''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>
<div class="editor-ux-v2" style="position:relative!important;width:100vw!important;height:100vh!important;display:flex!important;background:#102235!important">
  <aside class="editor-widget-rail" style="width:130px;position:absolute;right:0;top:60px;bottom:0">
   <div class="editor-widget-grid" style="height:120px;overflow-y:auto;overflow-x:hidden">
    <span class="editor-icon-wrapper"><button class="editor-icon-tool" aria-label="Aggiungi widget: Domanda">?</button></span>
   </div>
  </aside>
  <div class="widget-question" style="position:absolute;left:15px;top:150px;width:250px;color:#eee">
   <label><input type="radio" name="q1"><span>Prima risposta</span></label>
   <label><input type="checkbox"><span>Seconda risposta</span></label>
  </div>
  <ol class="projection-interactive-options" data-answer-mode="multiple" style="position:absolute;left:16px;top:300px;width:250px;color:#eee"><li><i class="widget-choice-marker"></i><span>Scelta a sinistra</span></li></ol>
</div>
<div class="editor-floating-tooltip tooltip-left" role="tooltip" style="left:calc(100% - 145px);top:134px">Aggiungi widget: Domanda</div>
</body></html>'''
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for viewport in ({'width':1440,'height':900},{'width':390,'height':844}):
    page=await browser.new_page(viewport=viewport,is_mobile=viewport['width']<500,has_touch=viewport['width']<500)
    await page.set_content(HTML)
    await page.add_style_tag(content=CSS)
    result=await page.evaluate('''() => {
      const tip=document.querySelector('[role=tooltip]');const t=tip.getBoundingClientRect();
      const ring=document.querySelector('.editor-widget-grid').getBoundingClientRect();
      const radio=document.querySelector('.widget-question input[type=radio]').getBoundingClientRect();
      const text=document.querySelector('.widget-question input[type=radio]+span').getBoundingClientRect();
      const checkbox=document.querySelector('.widget-question input[type=checkbox]').getBoundingClientRect();
      const text2=document.querySelector('.widget-question input[type=checkbox]+span').getBoundingClientRect();
      const mark=document.querySelector('.projection-interactive-options .widget-choice-marker').getBoundingClientRect();
      const projection=document.querySelector('.projection-interactive-options li span').getBoundingClientRect();
      return {tipFixed:getComputedStyle(tip).position==='fixed',tipAbove:getComputedStyle(tip).zIndex==='2147483000',tipOutsideRail:t.left<ring.left,radioLeft:radio.right<text.left,checkboxLeft:checkbox.right<text2.left,projectionLeft:mark.right<projection.left};
    }''')
    assert all(result.values()),f'{viewport}: {result}'
    print('PASS editor floating tooltip and left-of-answer markers:',viewport)
    await page.close()
  finally:await browser.close()
if __name__=='__main__':asyncio.run(main())
