#!/usr/bin/env python3
"""No-network Chromium layout preflight for mock-fidelity three-column editor."""
import asyncio
import base64
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()
LOGO='data:image/svg+xml;base64,'+base64.b64encode((ROOT/'apps/web/public/editor-quorivio-logo.svg').read_bytes()).decode()
HTML='''<!doctype html><html lang="it"><head><style>@CSS@</style></head><body>
<section class="panel powerpoint-editor editor-ux-v2" aria-label="Editor grafico delle pagine">
<header class="editor-mock-header"><div class="editor-mock-brand"><img alt="Quorivio" src="@LOGO@"><span>Workshop 2024</span><span class="editor-online-chip">Editor</span></div><div class="editor-mock-actions"><span class="editor-autosave-indicator" role="status">Salvato automaticamente</span><button class="editor-exit">Esci</button></div></header>
<aside class="page-editor-sidebar" aria-label="Miniature delle pagine"><header>Pagine</header><div class="page-editor-thumbnails"><div class="page-editor-thumb-row is-active"><button class="page-editor-thumb"><span class="page-editor-preview">Benvenuti</span></button></div><div class="page-editor-thumb-row"><button class="page-editor-thumb"><span class="page-editor-preview">Programma</span></button></div></div></aside>
<div class="editor-stage"><div class="editor-canvas-slot"><div class="canvas-editor-group"><div class="canvas-with-rulers"><div class="widget-canvas" role="group" aria-label="Canvas grafico widget"><div class="widget-canvas-item" style="left:15%;top:20%;width:36%;height:25%">Benvenuti</div></div></div></div></div></div>
<aside class="editor-widget-rail" aria-label="Aggiungi widget"><header>Widget</header><div class="editor-widget-grid"><button class="editor-icon-tool">T</button><button class="editor-icon-tool">◈</button><button class="editor-icon-tool">◉</button><button class="editor-icon-tool">□</button></div></aside>
</section></body></html>'''.replace('@CSS@',CSS).replace('@LOGO@',LOGO)
async def verify(browser,width,height,mobile):
 page=await browser.new_page(viewport={'width':width,'height':height},has_touch=mobile,is_mobile=mobile)
 try:
  await page.set_content(HTML,wait_until='load')
  editor=page.get_by_role('region',name='Editor grafico delle pagine')
  header=editor.locator('.editor-mock-header');thumb=editor.get_by_role('complementary',name='Miniature delle pagine');stage=editor.locator('.editor-stage');rail=editor.get_by_role('complementary',name='Aggiungi widget');canvas=editor.get_by_role('group',name='Canvas grafico widget')
  await expect(header).to_be_visible();await expect(thumb).to_be_visible();await expect(stage).to_be_visible();await expect(rail).to_be_visible();await expect(canvas).to_be_visible()
  hb,tb,sb,rb,cb=await asyncio.gather(*(x.bounding_box() for x in (header,thumb,stage,rail,canvas)))
  assert all(v for v in (hb,tb,sb,rb,cb))
  assert hb['y']<tb['y']+2 and hb['y']<rb['y']+2
  assert tb['x']+tb['width']<=sb['x']+5,(tb,sb)
  assert sb['x']+sb['width']<=rb['x']+5,(sb,rb)
  assert cb['width']>=sb['width']*.60,(cb,sb)
  assert abs(cb['width']/cb['height']-16/9)<.035,(cb,width,height)
  assert await editor.locator('.editor-bottom-controls').count()==0
  assert await editor.locator('.canvas-blank-menu-trigger').count()==0
  await expect(editor.get_by_role('button',name='Esci')).to_be_visible()
  await expect(editor.get_by_role('img',name='Quorivio')).to_be_visible()
  # Optional diagnostic screenshot for CI failure/artifact review.
  if os.environ.get('QUORIVIO_EDITOR_MOCK_SCREENSHOT')=='1':
   path=Path('/tmp')/f'quorivio-editor-mock-{width}.png';await page.screenshot(path=str(path))
 finally:await page.close()
async def main():
 async with async_playwright() as pw:
  opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(headless=True,args=['--no-sandbox','--allow-file-access-from-files'],**opts)
  try:
   await verify(browser,1440,900,False)
   await verify(browser,390,844,True)
  finally:await browser.close()
 print('PASS mock-fidelity editor: branded header, left thumbnails, responsive 16:9 canvas, right widget rail, Exit only; desktop and mobile Chromium')
if __name__=='__main__':asyncio.run(main())
