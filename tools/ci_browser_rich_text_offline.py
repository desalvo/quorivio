#!/usr/bin/env python3
"""Runs Chromium against the real WYSIWYG component with no network or DB.

This is a component-level check. The full authenticated browser/PG flow remains
an independent GitHub opt-in release gate.
"""
import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright, expect

ROOT=Path(__file__).resolve().parent.parent
async def run():
 with tempfile.TemporaryDirectory(prefix='quorivio-rich-editor-') as tmp:
  bundle=Path(tmp)/'harness.js'
  subprocess.run([str(ROOT/'node_modules/.bin/esbuild'),str(ROOT/'tools/fixtures/ci_richtext_harness.tsx'),'--bundle','--platform=browser','--format=iife',f'--outfile={bundle}'],cwd=ROOT,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  async with async_playwright() as pw:
   browser=await pw.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
   for width in (1440,390):
    page=await browser.new_page(viewport={'width':width,'height':820})
    await page.set_content('<!doctype html><html><body><div id="root"></div></body></html>')
    await page.add_script_tag(path=str(bundle))
    editor=page.get_by_role('textbox',name='Titolo widget')
    await expect(editor).to_contain_text('Alpha beta')
    await editor.evaluate("el=>{const selection=window.getSelection();const range=document.createRange();const text=el.firstChild.firstChild;range.setStart(text,6);range.setEnd(text,10);selection.removeAllRanges();selection.addRange(range);el.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}))}")
    await page.locator('[data-test=bold]').click()
    await expect(editor.locator('span').last).to_have_css('font-weight','700')
    await expect(page.locator('[data-test=projection] span').last).to_have_css('font-weight','700')
    await editor.click()
    await editor.evaluate("el=>{const selection=window.getSelection();const range=document.createRange();range.selectNodeContents(el);range.collapse(false);selection.removeAllRanges();selection.addRange(range);el.dispatchEvent(new MouseEvent('mouseup',{bubbles:true}))}")
    await page.locator('[data-test=italic]').click()
    await editor.focus()
    await page.keyboard.type('!')
    await expect(page.locator('[data-test=json]')).to_contain_text('Alpha beta!')
    await expect(page.locator('[data-test=projection] span').last).to_have_css('font-style','italic')
    assert await page.locator('[data-test=json]').evaluate("el=>JSON.parse(el.textContent).value") == 'Alpha beta!', await page.locator('[data-test=json]').inner_text()
    # Do not persist intermediate characters from an IME composition. A final
    # compositionend must commit the resulting Unicode text without losing markup.
    await editor.evaluate("""el=>{
      el.focus();
      el.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true,data:''}));
      el.appendChild(document.createTextNode('あ'));
      el.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertCompositionText',data:'あ'}));
    }""")
    await expect(page.locator('[data-test=json]')).to_contain_text('Alpha beta!')
    await editor.evaluate("el=>el.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:'あ'}))")
    await expect(page.locator('[data-test=json]')).to_contain_text('Alpha beta!あ')
    await expect(page.locator('[data-test=projection]')).to_contain_text('Alpha beta!あ')
    await page.locator('[data-test=finish]').click()
    await expect(page.get_by_role('textbox',name='Titolo widget')).to_have_count(0)
    await expect(page.locator('[data-test=projection]')).to_contain_text('Alpha beta!あ')
    await page.close()
   await browser.close()
   print('PASS production RichWidgetText Chromium: selected formatting, live projection, caret insertion, desktop/mobile')
if __name__=='__main__':asyncio.run(run())
