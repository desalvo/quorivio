#!/usr/bin/env python3
"""Real Chromium preflight: fixed mock-layout header stays actionable during autosave.

The editor no longer has persistent Save controls beneath the artboard. This
checks its actual new CSS, a visible auto-save status, expanded accessibility
rows, and the sole Exit button on desktop and touch using normal pointer input.
No production database/network access is needed.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect

CSS=(Path(__file__).resolve().parents[1]/'apps/web/src/style.css').read_text(encoding='utf-8')

def fixture():
 entries=''.join(f'<div class="canvas-accessible-row"><strong>{name}</strong><button>Porta in primo piano {name}</button></div>' for name in ('First','Second','Third'))
 return '''<!doctype html><html lang="it"><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>
<section class="panel powerpoint-editor editor-ux-v2" role="region" aria-label="Editor grafico delle pagine">
<header class="editor-mock-header"><div class="editor-mock-brand"><span>Quorivio</span><span>Workshop 2024</span></div>
<div class="editor-mock-actions"><span role="status" class="editor-autosave-indicator">Salvataggio automatico…</span><button type="button" class="editor-exit" onclick="document.querySelector('#result').textContent='exited'">Esci</button></div></header>
<aside class="page-editor-sidebar" aria-label="Miniature delle pagine"></aside>
<div class="editor-stage"><div class="editor-canvas-slot"><div class="canvas-editor-group"><div class="canvas-with-rulers"><div class="widget-canvas" role="group" aria-label="Canvas grafico widget"><div class="widget-canvas-item" style="left:75%;top:70%;width:15%;height:10%">Third</div></div></div>
<details class="canvas-accessible-controls" open role="region" aria-label="Organizzazione accessibile dei widget"><summary>Controlli accessibili per tastiera e touchscreen</summary><div class="canvas-accessible-list">''' + entries + '''</div></details></div></div></div>
<aside class="editor-widget-rail" aria-label="Aggiungi widget"></aside>
</section><output id="result"></output><script>
setTimeout(()=>document.querySelector('.editor-autosave-indicator').textContent='Salvato automaticamente',70)
</script></body></html>'''

async def verify(browser,width,height,touch):
 page=await browser.new_page(viewport={'width':width,'height':height},is_mobile=touch,has_touch=touch)
 try:
  await page.set_content(fixture(),wait_until='load')
  await page.add_style_tag(content=CSS)
  editor=page.get_by_role('region',name='Editor grafico delle pagine')
  assert await editor.locator('.editor-bottom-controls').count()==0,'Legacy explicit Save toolbar still present'
  assert await editor.get_by_role('button',name='Salva layout',exact=True).count()==0
  assert await editor.get_by_role('button',name='Salva layout della pagina').count()==0
  await expect(editor.get_by_role('status')).to_have_text('Salvato automaticamente')
  save_status=editor.get_by_role('status');await expect(save_status).to_be_visible()
  exit_button=editor.get_by_role('button',name='Esci',exact=True)
  await expect(exit_button).to_be_visible()
  hit=await exit_button.evaluate('''e=>{const b=e.getBoundingClientRect(),t=document.elementFromPoint(b.left+b.width/2,b.top+b.height/2);return t===e||e.contains(t)}''')
  assert hit,'Expanded canvas accessibility controls intercept the Exit button'
  if touch:await exit_button.tap()
  else:await exit_button.click()
  await expect(page.locator('#result')).to_have_text('exited')
  # Expanded accessible controls must remain readable and operable alongside the header.
  control=editor.get_by_role('button',name='Porta in primo piano Third')
  await expect(control).to_be_visible()
  if touch:await control.tap()
  else:await control.click()
  await expect(editor.locator('.canvas-accessible-controls')).to_have_attribute('open','')
 finally:await page.close()

async def main():
 async with async_playwright() as pw:
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'],**launch)
  try:
   await verify(browser,1440,1000,False)
   await verify(browser,390,844,True)
  finally:await browser.close()
 print('PASS Chromium autosave and editor Exit: responsive header, expanded accessible controls, desktop+mobile real clicks')

if __name__=='__main__':asyncio.run(main())
