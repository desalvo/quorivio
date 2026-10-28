#!/usr/bin/env python3
"""Offline Chromium exercise of the actual TypeScript rehearsal answer state.

Checks that presenter totals update only upon a one-shot participant submit,
that duplicate reaction widgets cannot submit twice on the same page, and
that resetting the rehearsal permits fresh answers. It does not call APIs.
"""
import asyncio
import os
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
BUNDLE="""const fs=require('fs'),esbuild=require('esbuild'); esbuild.transform(fs.readFileSync(process.argv[1],'utf8'),{loader:'ts',format:'iife',globalName:'Demo'}).then(x=>process.stdout.write(x.code));"""
HTML='''<!doctype html><html lang="it"><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>
<div role="group" aria-label="Anteprima partecipante">
 <button id="select-a">A</button><button id="select-b">B</button><button id="submit" disabled>Invia risposta di prova</button>
 <button id="reaction-1">👍</button><button id="reaction-2">❤️</button><button id="reset">Ricomincia prova</button>
</div><div role="group" aria-label="Anteprima presentatore"><output id="total">0</output><output id="reactions">0</output></div></body></html>'''
DRIVER="""() => {
 const $=(id)=>document.getElementById(id);
 let draft='',sent={};
 const update=()=>{$('submit').disabled=!!sent['q1']||!Demo.canSubmitRehearsalAnswer('single',draft);
 $('total').textContent=String(sent['q1']===undefined?0:1);
 $('reactions').textContent=String(sent['reaction-page:activity1']===undefined?0:1);
 for(const id of ['reaction-1','reaction-2'])$(id).disabled=sent['reaction-page:activity1']!==undefined;};
 $('select-a').onclick=()=>{draft='a';update()};$('select-b').onclick=()=>{draft='b';update()};
 $('submit').onclick=()=>{sent=Demo.commitRehearsalAnswer(sent,'q1',draft,'single');update()};
 for(const [id,emoji] of [['reaction-1','👍'],['reaction-2','❤️']])$(id).onclick=()=>{
  sent=Demo.commitRehearsalAnswer(sent,'reaction-page:activity1',emoji,'reaction');update()};
 $('reset').onclick=()=>{draft='';sent={};update()};update();
} """
async def main():
 js=subprocess.check_output(['node','-e',BUNDLE,str(ROOT/'apps/web/src/rehearsal-responses.ts')],cwd=ROOT,text=True)
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  try:
   for width,height in [(1440,900),(390,844)]:
    page=await browser.new_page(viewport={'width':width,'height':height})
    await page.set_content(HTML)
    await page.add_script_tag(content=js)
    await page.evaluate(DRIVER)
    assert await page.locator('#total').inner_text()=='0'
    assert await page.locator('#submit').is_disabled()
    await page.locator('#select-a').click()
    assert await page.locator('#total').inner_text()=='0','Draft must not increment presenter statistics'
    await page.locator('#select-b').click()
    await page.locator('#submit').click()
    assert await page.locator('#total').inner_text()=='1'
    assert await page.locator('#submit').is_disabled(),'Duplicate answer must be rejected'
    await page.locator('#reaction-1').click()
    assert await page.locator('#reactions').inner_text()=='1'
    assert await page.locator('#reaction-2').is_disabled(),'One reaction per page across all widgets'
    await page.locator('#reset').click()
    assert await page.locator('#total').inner_text()=='0'
    assert await page.locator('#reactions').inner_text()=='0'
    assert not await page.locator('#reaction-2').is_disabled()
    await page.close()
    print(f'PASS offline Chromium {width}px: draft/submit, presenter stats, one-shot reactions and rehearsal reset')
  finally: await browser.close()
if __name__=='__main__':asyncio.run(main())
