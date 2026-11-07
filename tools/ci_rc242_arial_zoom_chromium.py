#!/usr/bin/env python3
"""Real Chromium fixture for RC242 Arial inheritance, compact master ribbon and root zoom."""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
KINDS=('rating','reactions','text','shape','line','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count','title','footer')
HTML='''<!doctype html><html><body><main class="slide-scheme-workspace">
 <div class="slide-scheme-ribbon" role="toolbar" aria-label="Barra multifunzione schemi">
  <div class="slide-scheme-ribbon-group"><strong>Inserisci</strong><div class="slide-scheme-ribbon-actions">
   <button class="slide-scheme-ribbon-tool"><span class="slide-scheme-ribbon-icon">A</span><span class="slide-scheme-ribbon-caption">Titolo</span></button>
   <button class="slide-scheme-ribbon-tool"><span class="slide-scheme-ribbon-icon">B</span><span class="slide-scheme-ribbon-caption">Footer</span></button>
  </div></div><div class="slide-scheme-ribbon-group"><strong>Allinea</strong><div class="slide-scheme-ribbon-actions">
   <button class="slide-scheme-ribbon-tool">Sinistra</button><button class="slide-scheme-ribbon-tool">Centro</button><button class="slide-scheme-ribbon-tool">Destra</button>
   <button class="slide-scheme-ribbon-tool">In alto</button><button class="slide-scheme-ribbon-tool">In basso</button></div></div>
  <div class="slide-scheme-ribbon-group slide-scheme-ribbon-save"><strong>Schema</strong><div class="slide-scheme-ribbon-actions">
   <button class="slide-scheme-ribbon-tool primary" aria-label="Salva schema">Salva schema</button>
   <span role="status">Modifiche non salvate</span></div></div>
 </div>
 <div class="widget-canvas-item" id="default-widget" style="font-family:Arial,sans-serif;width:140px">
  <div class="widget-fit-content"><h2 id="default-title">Titolo widget</h2><strong id="default-strong">Opzioni</strong>
  <label id="default-label">Risposta<input id="default-input" value="Testo"/></label>
  <span id="custom-font" style="font-family:Georgia">Personalizzato</span></div>
 </div>
 <div class="widget-canvas-item" id="custom-widget" style="font-family:Verdana,sans-serif"><h2 id="custom-title">Personalizzato</h2></div>
 </main></body></html>'''

async def run():
 async with async_playwright() as playwright:
  browser=await playwright.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for width in (390,760,1440):
    page=await browser.new_page(viewport={'width':width,'height':880})
    # Both real editor containers, for all 20 insertable widget kinds.
    audit=''.join(f'<div class="widget-canvas-item" data-widget-kind="{kind}" style="font-family:Arial,sans-serif"><div class="widget-fit-content"><h3 data-q242-font="true">Titolo</h3><strong data-q242-font="true">Risposta</strong><label data-q242-font="true">Etichetta<input data-q242-font="true" value="Testo"/></label></div></div>' for kind in KINDS)
    content=HTML.replace('</main>',f'<section class="editor-ux-v2" aria-label="Editor pagine">{audit}</section><section class="slide-scheme-workspace" aria-label="Editor schemi">{audit}</section></main>')
    await page.set_content(content)
    await page.add_style_tag(content=CSS)
    data=await page.evaluate('''() => {
      const face=id=>getComputedStyle(document.getElementById(id)).fontFamily;
      const ribbon=document.querySelector('.slide-scheme-ribbon').getBoundingClientRect();
      const save=document.querySelector('.slide-scheme-ribbon-save').getBoundingClientRect();
      const line=Array.from(document.querySelectorAll('.slide-scheme-ribbon-group'))
        .map(x=>x.getBoundingClientRect());
      return {allWidgetFonts:Array.from(document.querySelectorAll('[data-q242-font]')).map(x=>getComputedStyle(x).fontFamily),fonts:['default-title','default-strong','default-label','default-input','custom-font','custom-title'].map(face),
         ribbon:{width:ribbon.width,height:ribbon.height,left:ribbon.left,right:ribbon.right},
         save:{height:save.height,top:save.top,right:save.right},
         rows:line.map(x=>x.top), buttons:Array.from(document.querySelectorAll('.slide-scheme-ribbon-tool'))
           .map(x=>x.getBoundingClientRect().height)};
    }''')
    assert len(data['allWidgetFonts'])==len(KINDS)*2*4 and all('Arial' in x for x in data['allWidgetFonts']), (width,data)
    assert all('Arial' in x for x in data['fonts'][:4]), (width,data)
    assert 'Georgia' in data['fonts'][4] and 'Verdana' in data['fonts'][5],(width,data)
    assert max(data['rows'])-min(data['rows'])<10,(width,data)
    assert max(data['buttons'])<=44 and data['ribbon']['height']<75,(width,data)
    assert data['save']['right']<=width+5,(width,data)
    before=await page.locator('#default-widget').bounding_box()
    await page.evaluate("document.documentElement.style.setProperty('zoom','120%')")
    after=await page.locator('#default-widget').bounding_box()
    assert before and after and after['width']>before['width']*1.1,(width,before,after)
    await page.evaluate("document.documentElement.style.removeProperty('zoom')")
    restored=await page.locator('#default-widget').bounding_box()
    assert restored and abs(restored['width']-before['width'])<2,(width,before,restored)
    print(f'PASS RC242 Chromium {width}px: Arial default on 20 widget types in both editors, custom fonts retained, compact master save, zoom reset')
    await page.close()
  finally:await browser.close()

if __name__=='__main__':asyncio.run(run())
