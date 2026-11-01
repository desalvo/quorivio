#!/usr/bin/env python3
"""Isolated Chromium hit-target and WYSIWYG contextual editing regression.

Fixture mirrors both the production document.body menu portal and the current
contentEditable contract. The full authenticated test remains independent.
"""
import asyncio
import os
from playwright.async_api import async_playwright, expect, TimeoutError as PlaywrightTimeout

HTML = '''<!doctype html><html lang="it"><meta charset="utf-8">
<style>
.widget-canvas-item { position:relative; width:340px; height:140px; padding:9px 23px 9px 9px; background:white; border:1px solid #877cbb; }
.widget-rich-inline { width:100%; padding:8px; white-space:pre-wrap; }
.widget-rich-inline[contenteditable="false"] { pointer-events:none; user-select:none; }
.widget-rich-inline[contenteditable="true"] { pointer-events:auto; user-select:text; outline:1px dotted #3470be; }
.canvas-context-menu { position:fixed;left:28px;top:205px;z-index:10020;display:flex;flex-direction:column;background:white; }
.canvas-context-menu[hidden] { display:none; }
</style>
<div class="widget-canvas-item" role="group" tabindex="0" aria-label="Widget text; frecce spostano">
<div class="widget-rich-inline" aria-label="Titolo text" contenteditable="false">Remote collaborator</div>
</div><div class="canvas-context-menu" role="group" aria-label="Azioni widget text" hidden>
<button type="button">Modifica titolo</button></div>
<script>
const item=document.querySelector('.widget-canvas-item');
const field=item.querySelector('.widget-rich-inline');
const menu=document.querySelector('.canvas-context-menu');
const activate=()=>{field.contentEditable='true';menu.hidden=true;field.focus()};
const finish=()=>{field.contentEditable='false';field.blur()};
item.addEventListener('contextmenu',e=>{e.preventDefault();menu.hidden=false});
item.addEventListener('dblclick',e=>{if(!e.target.closest('button'))activate()});
item.addEventListener('keydown',e=>{if(e.key==='ContextMenu'||(e.shiftKey&&e.key==='F10')){e.preventDefault();menu.hidden=false}});
menu.querySelector('button').addEventListener('click',activate);
field.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key==='Escape'){e.preventDefault();finish()}});
</script></html>'''

async def main():
 async with async_playwright() as pw:
  opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**opts,headless=True,args=['--no-sandbox'])
  try:
   for width in (1440,390):
    page=await browser.new_page(viewport={'width':width,'height':820})
    await page.set_content(HTML)
    item=page.get_by_role('group',name='Widget text; frecce spostano')
    field=item.locator('.widget-rich-inline')
    await expect(field).to_have_attribute('contenteditable','false')
    # The inactive title cannot be edited accidentally during dragging.
    try:
     await field.dblclick(timeout=600)
     raise AssertionError('Expected inactive text layer pointer interception')
    except PlaywrightTimeout:
     pass
    await item.click(button='right',position={'x':12,'y':12})
    menu=page.get_by_role('group',name='Azioni widget text',exact=True)
    await expect(menu).to_have_count(1)
    await expect(menu).to_be_visible()
    await menu.get_by_role('button',name='Modifica titolo').click()
    await expect(menu).not_to_be_visible()
    await expect(field).to_have_attribute('contenteditable','true')
    await field.fill('Local second edit')
    await field.press('Enter')
    await expect(field).to_have_text('Local second edit')
    await expect(field).to_have_attribute('contenteditable','false')
    # Double-clicking the widget itself is the second user-supported path.
    await item.dblclick(position={'x':12,'y':12})
    await expect(field).to_have_attribute('contenteditable','true')
    await field.fill('Double click edit')
    await field.press('Enter')
    await expect(field).to_have_text('Double click edit')
    await expect(field).to_have_attribute('contenteditable','false')
    await page.close()
   print('PASS isolated Chromium: WYSIWYG context menu and widget double-click, Enter commits, desktop/mobile')
  finally:
   await browser.close()

if __name__=='__main__': asyncio.run(main())
