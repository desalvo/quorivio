#!/usr/bin/env python3
"""Isolated Chromium hit-target regression (no backend/network needed).

Reproduces the production readonly input pointer policy and accessible widget
context-menu action. This is NOT a substitute for the real PostgreSQL E2E gate.
"""
import asyncio
import os
from playwright.async_api import async_playwright, expect, TimeoutError as PlaywrightTimeout

HTML = '''<!doctype html><html lang="it"><meta charset="utf-8">
<style>
.widget-canvas-item { position:relative; width:340px; height:140px; padding:9px 23px 9px 9px; background:white; border:1px solid #877cbb; }
.widget-canvas-item input { box-sizing:border-box; height:100%; width:100%; background:transparent; border:0; }
.widget-canvas-item input[readonly] { pointer-events:none; cursor:move; }
.canvas-menu-trigger { position:absolute;right:22px;top:2px;z-index:14;min-width:24px;min-height:24px; }
.canvas-context-menu { position:absolute;left:10px;top:28px;z-index:30;display:flex;flex-direction:column;background:white; }
</style>
<div class="widget-canvas-item" role="group" aria-label="Widget text; frecce spostano">
<input aria-label="Titolo text" readonly value="Remote collaborator">
<button type="button" class="canvas-menu-trigger" aria-label="Menu contestuale text" aria-expanded="false">⋮</button>
<div class="canvas-context-menu" role="group" aria-label="Azioni widget text" hidden>
<button type="button">Modifica titolo</button></div></div>
<script>
const item=document.querySelector('.widget-canvas-item'), input=item.querySelector('input');
const trigger=item.querySelector('.canvas-menu-trigger'), menu=item.querySelector('.canvas-context-menu');
trigger.addEventListener('click',()=>{menu.hidden=false;trigger.setAttribute('aria-expanded','true')});
menu.querySelector('button').addEventListener('click',()=>{input.readOnly=false;menu.hidden=true;trigger.setAttribute('aria-expanded','false')});
input.addEventListener('keydown',e=>{if(e.key==='Enter'){input.readOnly=true;input.blur()}});
</script></html>'''

async def main():
 async with async_playwright() as pw:
  opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**opts,headless=True,args=['--no-sandbox'])
  try:
   page=await browser.new_page()
   await page.set_content(HTML)
   item=page.get_by_role('group',name='Widget text; frecce spostano')
   field=item.get_by_role('textbox',name='Titolo text')
   await expect(field).not_to_be_editable()
   # The regression: a Playwright double-click on the readonly input is not
   # actionable because the parent is the actual pointer hit target.
   try:
    await field.dblclick(timeout=750)
    raise AssertionError('Expected readonly title double-click to be intercepted')
   except PlaywrightTimeout:
    pass
   await item.get_by_role('button',name='Menu contestuale text').click()
   menu=item.get_by_role('group',name='Azioni widget text')
   await expect(menu).to_be_visible()
   await menu.get_by_role('button',name='Modifica titolo').click()
   await expect(field).to_be_editable()
   await field.fill('Local second edit')
   await field.press('Enter')
   await expect(field).to_have_value('Local second edit')
   await expect(field).not_to_be_editable()
   print('PASS isolated Chromium: readonly pointer intercept reproduced; accessible menu edit/Enter succeeds')
  finally:
   await browser.close()

if __name__=='__main__': asyncio.run(main())
