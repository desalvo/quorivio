#!/usr/bin/env python3
"""Isolated Chromium check for the autosave-only editor shell (no backend)."""
import asyncio
import os
from playwright.async_api import async_playwright, expect

HTML='''<!doctype html><html lang="it"><body>
<button aria-label="Salva layout" id="dashboard">Legacy dashboard save</button>
<section role="region" aria-label="Editor grafico delle pagine">
<header><img alt="Quorivio" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E">
 <span role="status">Salvato automaticamente</span><button id="exit">Esci</button></header>
<div role="group" aria-label="Canvas grafico widget" id="canvas" style="height:250px;border:1px solid gray;touch-action:pan-y"></div>
<aside aria-label="Aggiungi widget">Widget</aside>
</section>
<script>
 const canvas=document.getElementById('canvas');
 canvas.addEventListener('contextmenu',e=>{e.preventDefault();canvas.innerHTML='<button id="manual-save">Salva ora</button>';});
</script></body></html>'''

async def verify(browser, *, touch):
 page=await browser.new_page(viewport={'width':390 if touch else 1440,'height':844 if touch else 900},has_touch=touch,is_mobile=touch)
 try:
  await page.set_content(HTML)
  editor=page.get_by_role('region',name='Editor grafico delle pagine')
  assert await editor.get_by_role('button',name='Salva layout').count()==0
  assert await editor.get_by_role('button',name='Salva layout della pagina').count()==0
  await expect(editor.get_by_role('status')).to_have_text('Salvato automaticamente')
  await expect(editor.get_by_role('button',name='Esci')).to_be_visible()
  if touch:
   await page.locator('#canvas').dispatch_event('contextmenu')  # Synthetic long-press fallback in the isolated fixture only.
  else:
   await page.locator('#canvas').click(button='right',position={'x':7,'y':7})
  await expect(editor.get_by_role('button',name='Salva ora')).to_be_visible()
 finally:await page.close()

async def main():
 async with async_playwright() as pw:
  opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'],**opts)
  try:
   await verify(browser,touch=False)
   await verify(browser,touch=True)
  finally:await browser.close()
 print('PASS Chromium autosave-only editor: no redundant Save buttons, labelled sync state and contextual manual save desktop+touch fixture')

if __name__=='__main__':asyncio.run(main())
