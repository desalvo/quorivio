#!/usr/bin/env python3
"""Offline real-Chromium regression: canvas context popup must not block mobile disclosure.

CI 40510491774: the open alignment popup extended beyond the 16:9 artboard
and intercepted clicks intended for the alternative keyboard/touch disclosure.
Use the application's actual CSS; never force clicks or mutate pointer handling.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect

CSS = (Path(__file__).resolve().parents[1] / 'apps/web/src/style.css').read_text(encoding='utf-8')
HTML = '''<!doctype html><html lang="it"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>
<div class="editor-ux-v2" style="max-width:390px;padding:0 8px">
 <div class="canvas-editor-group" data-tools-open="false">
  <button type="button" id="context-toggle" onclick="document.querySelector('.canvas-editor-group').dataset.toolsOpen = document.querySelector('.canvas-editor-group').dataset.toolsOpen === 'true' ? 'false' : 'true'">Menu canvas</button>
  <div class="canvas-editor-tools" role="group" aria-label="Appunti widget"><button type="button">Copia selezione</button></div>
  <div class="canvas-editor-tools" role="group" aria-label="Allineamento widget selezionati">
   <strong>2 selezionati</strong><button type="button">Sinistra</button><button type="button">Centro orizzontale</button>
   <button type="button">Destra</button><button type="button">Alto</button><button type="button">Centro verticale</button>
   <button type="button">Basso</button><button type="button">Stessa larghezza</button><button type="button" disabled>Stessa altezza</button>
   <button type="button">Distribuisci orizzontalmente</button><button type="button">Distribuisci verticalmente</button>
   <div class="canvas-editor-tools" role="group" aria-label="Ordine e spostamento widget selezionati">
    <button type="button" id="layer" onclick="document.querySelector('#result').textContent='edited'">Porta selezione davanti</button>
   </div>
  </div>
  <div class="canvas-with-rulers" style="height:190px;background:#ccc"></div>
  <details class="canvas-accessible-controls" role="region" aria-label="Organizzazione accessibile dei widget"
   ontoggle="if(this.open)document.querySelector('.canvas-editor-group').dataset.toolsOpen='false'">
   <summary>Controlli accessibili per tastiera e touchscreen</summary>
   <div class="canvas-accessible-list"><label><input type="checkbox" aria-label="Seleziona"> Seleziona</label></div>
  </details>
 </div><output id="result"></output>
</div></body></html>'''

async def verify(browser, width, height, touch):
    page=await browser.new_page(viewport={'width':width,'height':height},is_mobile=touch,has_touch=touch)
    try:
        await page.set_content(HTML)
        await page.add_style_tag(content=CSS)
        toggle=page.locator('#context-toggle')
        group=page.get_by_role('group',name='Allineamento widget selezionati')
        summary=page.locator('.canvas-accessible-controls > summary')
        await (toggle.tap() if touch else toggle.click())
        await expect(group).to_be_visible()
        # The exact overlap from the failed CI: the second floating toolbar
        # extends across the collapsed accessible summary at narrow widths.
        overlap=await page.evaluate('''() => {
          const toolbar=document.querySelectorAll('.canvas-editor-group > .canvas-editor-tools')[1].getBoundingClientRect();
          const summary=document.querySelector('.canvas-accessible-controls > summary').getBoundingClientRect();
          return toolbar.top < summary.bottom && toolbar.bottom > summary.top;
        }''')
        assert overlap, 'Fixture must intentionally reproduce the mobile toolbar/disclosure overlap'
        hit=await summary.evaluate('''el=>{
          const r=el.getBoundingClientRect(), h=document.elementFromPoint(r.left+r.width/2,r.top+r.height/2);
          return h===el || el.contains(h);
        }''')
        assert hit, 'Canvas overlay intercepts pointer meant for accessibility disclosure'
        await (summary.tap() if touch else summary.click())
        await expect(page.locator('.canvas-accessible-controls')).to_have_attribute('open','')
        await expect(group).to_be_hidden()
        check=page.get_by_role('checkbox',name='Seleziona')
        await check.check()
        await expect(check).to_be_checked()
        # Both contextual and accessible modes remain usable after switching.
        await (toggle.tap() if touch else toggle.click())
        await expect(group).to_be_visible()
        layer=page.locator('#layer')
        await (layer.tap() if touch else layer.click())
        await expect(page.locator('#result')).to_have_text('edited')
    finally:
        await page.close()

async def main():
    async with async_playwright() as pw:
        kw={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.getenv('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'],**kw)
        try:
            await verify(browser,390,844,True)
            await verify(browser,1440,1000,False)
        finally:
            await browser.close()
    print('PASS real Chromium: overlapping mobile/desktop contextual toolbar, accessible disclosure opens, closes popup and remains interactive')

if __name__=='__main__':
    asyncio.run(main())
