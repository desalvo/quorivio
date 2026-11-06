#!/usr/bin/env python3
"""Representative DOM/CSS Chromium check of the shipped portaled thumbnail menu.

Also checks the default Arial canvas text cascade. This does not replace
full compiled React/editor and PostgreSQL acceptance tests.
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()

async def main():
 async with async_playwright() as pw:
  browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for width,height in ((320,240),(390,380),(390,844),(1440,900)):
    page=await browser.new_page(viewport={'width':width,'height':height})
    # The menu is portaled to document.body; it must never inherit sidebar clipping.
    # Use viewport-clamped placement for a thumbnail at the bottom-right corner.
    pad=8;menu_height=min(340,height-2*pad)
    left=max(pad,min(width-2,width-min(270,width-2*pad)-pad))
    top=max(pad,min(height-2,height-menu_height-pad))
    max_height=height-top-pad
    menu='''<div class="page-editor-thumb-menu page-editor-thumb-menu-floating" role="group" aria-label="Azioni pagina 1" style="position:fixed;left:%spx;top:%spx;max-height:%spx;--thumbnail-menu-max-height:%spx">
    <button>Apri pagina</button><button>Rinomina pagina (R)</button><button>Duplica pagina (D)</button>
    <details class="page-editor-thumb-submenu"><summary>Crea e importa pagine</summary><div class="page-editor-thumb-submenu-items">
    <button>Nuova pagina prima</button><button>Nuova pagina dopo</button><label class="editor-thumb-import">Importa PDF/PPTX…<input type="file" aria-label="Importa PDF o PPTX"/></label><label class="editor-thumb-import">Importa layout JSON<input type="file" aria-label="Importa layout JSON"/></label>
    </div></details>
    <details class="page-editor-thumb-submenu"><summary>Ordina pagine</summary><div class="page-editor-thumb-submenu-items"><button>Sposta su</button><button>Sposta giù</button></div></details>
    <details class="page-editor-thumb-submenu"><summary>Esporta e dati</summary><div class="page-editor-thumb-submenu-items"><button>Esporta layout JSON</button></div></details>
    <button class="editor-delete-action" onclick="document.body.dataset.deleted='true'">Elimina pagina (Backspace)</button>
    </div>''' % (left,top,max_height,max_height)
    css='<style>'+CSS+'</style>'
    fixtures='''<section class="powerpoint-editor"><div class="widget-canvas-item"><span>Arial titolo editor</span><input value="Arial campo editor"/></div></section><section class="slide-scheme-workspace"><div class="widget-canvas-item"><span>Arial titolo schema</span><textarea>Arial footer schema</textarea></div></section>'''
    await page.set_content('<html><head>'+css+'</head><body>'+fixtures+menu+'</body></html>')
    root=page.get_by_role('group',name='Azioni pagina 1')
    for section in ('Crea e importa pagine','Ordina pagine','Esporta e dati'):
     await root.locator('summary',has_text=section).focus()
     await page.keyboard.press('Enter')
     assert await root.locator('details[open]').count()==('Crea e importa pagine','Ordina pagine','Esporta e dati').index(section)+1
    for label in ('Nuova pagina prima','Nuova pagina dopo','Sposta su','Sposta giù','Esporta layout JSON','Elimina pagina (Backspace)'):
     node=root.get_by_role('button',name=label,exact=True)
     await node.scroll_into_view_if_needed()
     b=await node.bounding_box()
     assert b and b['y']>=top-1 and b['y']+b['height']<=height-pad+1,(width,height,label,b,top,await page.evaluate('''() => {const n=document.querySelector('.page-editor-thumb-menu-floating');return {rect:n.getBoundingClientRect().toJSON(),scrollTop:n.scrollTop,scrollHeight:n.scrollHeight,clientHeight:n.clientHeight,overflow:getComputedStyle(n).overflowY}}'''))
    await root.get_by_role('button',name='Elimina pagina (Backspace)').click()
    assert await page.evaluate('document.body.dataset.deleted')=='true'
    stats=await page.evaluate('''() => {
       const root=document.querySelector('.page-editor-thumb-menu-floating');
       const rect=root.getBoundingClientRect();
       return {left:rect.left,right:rect.right,top:rect.top,bottom:rect.bottom,scrollHeight:root.scrollHeight,clientHeight:root.clientHeight,scrollY:root.scrollTop,
        fonts:[...document.querySelectorAll('.widget-canvas-item span,.widget-canvas-item input,.widget-canvas-item textarea')].map(x=>getComputedStyle(x).fontFamily)};
    }''')
    assert stats['left']>=pad-1 and stats['right']<=width-pad+1,(width,height,stats)
    assert stats['top']>=pad-1 and stats['bottom']<=height-pad+1,(width,height,stats)
    assert all('Arial' in font for font in stats['fonts']),(width,height,stats)
    assert stats['scrollHeight']<=stats['clientHeight']+2 or stats['scrollY']>0,(width,height,stats)
    print(f'PASS RC224 Chromium {width}x{height}: all expanded commands reached, Arial defaults')
    await page.close()
  finally:
   await browser.close()

if __name__=='__main__':asyncio.run(main())
