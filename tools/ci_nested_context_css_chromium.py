#!/usr/bin/env python3
"""Real Chromium CSS hit-test for nested canvas context commands.

Offline/standalone visual fixture: loads the actual production stylesheet,
checks closed/open CSS and mouse/touch interaction, never bypassing pointer
interception. The separate ci_browser_editor.py tests the complete React app.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect

CSS = (Path(__file__).resolve().parents[1] / 'apps/web/src/style.css').read_text(encoding='utf-8')
HTML = '''<!doctype html><html lang="it"><head><meta charset="utf-8"></head><body>
<div class="editor-ux-v2" style="min-height:800px">
 <div class="canvas-editor-group" data-tools-open="false" style="min-height:700px">
  <button type="button" id="toggle" aria-label="Apri menu contestuale canvas, sfondi e proprietà pagina"
   onclick="document.querySelector('.canvas-editor-group').dataset.toolsOpen =
     document.querySelector('.canvas-editor-group').dataset.toolsOpen === 'true' ? 'false' : 'true'">Menu</button>
  <div class="canvas-editor-tools" role="group" aria-label="Appunti widget">
   <button type="button">Copia selezione</button><button type="button">Incolla selezione</button>
  </div>
  <div class="canvas-editor-tools" role="group" aria-label="Allineamento widget selezionati">
   <strong>2 selezionati</strong>
   <button type="button">Sinistra</button><button type="button">Centro orizzontale</button>
   <button type="button">Destra</button><button type="button">Alto</button>
   <button type="button">Centro verticale</button><button type="button">Basso</button>
   <button type="button">Stessa larghezza</button><button type="button">Stessa altezza</button>
   <button type="button">Distribuisci orizzontalmente</button>
   <button type="button">Distribuisci verticalmente</button>
   <button type="button">Spazi orizzontali uguali</button>
   <button type="button">Spazi verticali uguali</button>
   <button type="button">Centra selezione nel canvas orizzontalmente</button>
   <button type="button">Centra selezione nel canvas verticalmente</button>
   <button type="button">Deseleziona</button>
   <div class="canvas-editor-tools" role="group" aria-label="Ordine e spostamento widget selezionati">
    <button type="button" onclick="document.getElementById('result').textContent='front'">Porta selezione davanti</button>
    <button type="button">Porta selezione dietro</button>
    <button type="button">Un livello avanti</button>
    <button type="button">Un livello indietro</button>
    <button type="button">Sposta selezione a sinistra</button>
    <button type="button">Sposta selezione a destra</button>
    <button type="button">Sposta selezione in alto</button>
    <button type="button">Sposta selezione in basso</button>
   </div>
  </div>
 </div>
</div><output id="result" aria-live="polite"></output>
</body></html>'''


async def verify(browser, *, width, height, touch):
    page = await browser.new_page(viewport={'width':width, 'height':height},
                                  is_mobile=touch, has_touch=touch)
    await page.set_content(HTML)
    await page.add_style_tag(content=CSS)
    toggle = page.get_by_role('button', name='Apri menu contestuale canvas, sfondi e proprietà pagina')
    outer = page.get_by_role('group',name='Allineamento widget selezionati')
    nested = page.get_by_role('group',name='Ordine e spostamento widget selezionati')
    front = nested.get_by_role('button',name='Porta selezione davanti')
    await expect(outer).to_be_hidden()
    await expect(nested).to_be_hidden()
    await (toggle.tap() if touch else toggle.click())
    await expect(outer).to_be_visible()
    await expect(nested).to_be_visible()
    await expect(front).to_be_visible()
    await (front.tap() if touch else front.click())
    await expect(page.locator('#result')).to_have_text('front')
    await (toggle.tap() if touch else toggle.click())
    await expect(outer).to_be_hidden()
    await expect(nested).to_be_hidden()
    await expect(front).to_be_hidden()
    await page.close()


async def main():
    async with async_playwright() as pw:
        kw={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.getenv('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'],**kw)
        try:
            await verify(browser,width=1440,height=1000,touch=False)
            await verify(browser,width=390,height=844,touch=True)
        finally:
            await browser.close()
    print('PASS nested canvas context CSS: desktop+mobile real pointer, open/click/close')


if __name__=='__main__':
    asyncio.run(main())
