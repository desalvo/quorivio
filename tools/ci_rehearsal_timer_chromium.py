#!/usr/bin/env python3
"""Offline Chromium deadline acceptance of the actual preview timing module.

The full authenticated UI and Firefox/WebKit remain independent RC requirements.
"""
import asyncio
import os
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = """const fs=require('fs'),esbuild=require('esbuild');
esbuild.transform(fs.readFileSync(process.argv[1],'utf8'),{loader:'ts',format:'iife',globalName:'QuorivioTimer'}).then(r=>process.stdout.write(r.code));"""
HTML = '''<!doctype html><html lang="it"><body>
<div role="group" aria-label="Simulazione quiz a tempo"><output id="time"></output>
<button id="send">Invia risposta di prova</button><button id="reset">Ricomincia prova</button></div>
<div role="group" aria-label="Statistiche presentatore"><output id="total">0</output></div></body></html>'''
DRIVER = '''() => {
 const $=id=>document.getElementById(id);
 let start=100000, now=100000, sent=false, count=0;
 const redraw=()=>{
   $('time').textContent=QuorivioTimer.rehearsalExpired(start,2,now)?'Tempo scaduto':'Tempo disponibile';
   $('send').disabled=!QuorivioTimer.maySubmitTimedRehearsal(start,2,now,sent);
   $('total').textContent=String(count);
 };
 $('send').onclick=()=>{if(!QuorivioTimer.maySubmitTimedRehearsal(start,2,now,sent))return;sent=true;count++;redraw()};
 $('reset').onclick=()=>{start=now;sent=false;count=0;redraw()};
 window.demo={advance:(milliseconds)=>{now+=milliseconds;redraw()},reset:()=>$('reset').click()};
 redraw();
}'''

async def main():
    script = subprocess.check_output(['node','-e',SCRIPT,str(ROOT/'apps/web/src/rehearsal-timer.ts')],cwd=ROOT,text=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for width,height in [(1440,900),(390,844)]:
                page=await browser.new_page(viewport={'width':width,'height':height})
                await page.set_content(HTML)
                await page.add_script_tag(content=script)
                await page.evaluate(DRIVER)
                await page.evaluate('window.demo.advance(1999)')
                assert await page.locator('#send').is_enabled()
                await page.evaluate('window.demo.advance(1)')
                assert await page.locator('#time').inner_text()=='Tempo scaduto'
                assert await page.locator('#send').is_disabled()
                await page.locator('#reset').click()
                assert await page.locator('#send').is_enabled()
                await page.locator('#send').click()
                assert await page.locator('#total').inner_text()=='1'
                assert await page.locator('#send').is_disabled()
                await page.evaluate('window.demo.advance(2000)')
                assert await page.locator('#total').inner_text()=='1','Expired previews must preserve already submitted statistics'
                await page.close()
                print(f'PASS Chromium {width}px: exact deadline, disabled late submissions, reset and stable presenter stats')
        finally:
            await browser.close()

if __name__=='__main__':
    asyncio.run(main())
