#!/usr/bin/env python3
"""Real Chromium computed-layout regression for compact QR with optional text.

A local inert fixture uses the same style.css as editor/rehearsal/live. No API,
logins, participant addresses or external domains are contacted.
"""
from __future__ import annotations
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()
SVG='<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300"><rect width="300" height="300" fill="white"/><rect x="50" y="50" width="200" height="200" fill="black"/></svg>'

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   page=await browser.new_page()
   await page.set_content('<style>'+CSS+'</style><div id="slot" style="width:160px;height:130px;padding:2px;background:#ffffee"><div class="projection-sample-qr participant-access-qr" data-qr-target="participants" data-qr-show-url="true" data-qr-show-title="false"><img id="symbol" alt="QR" src="data:image/svg+xml,'+SVG.replace('#','%23').replace('<','%3C').replace('>','%3E').replace('"','%22').replace(' ','%20')+'"/><span class="participant-qr-url" aria-label="URL di accesso dei partecipanti">https://example.invalid/join/a-rather-long-identifier</span></div></div>')
   for width,height in [(160,130),(110,95),(75,90),(290,220)]:
    await page.locator('#slot').evaluate('(el,box)=>{el.style.width=box.w+"px";el.style.height=box.h+"px"}',{'w':width,'h':height})
    info=await page.locator('.participant-access-qr').evaluate('''el=>{const img=el.querySelector('img').getBoundingClientRect(),url=el.querySelector('.participant-qr-url').getBoundingClientRect(),r=el.getBoundingClientRect();return {imgH:img.height,urlH:url.height,urlTop:url.top,imgBottom:img.bottom,inside:url.bottom<=r.bottom+1,display:getComputedStyle(el.querySelector('.participant-qr-url')).display}}''')
    assert info['urlH']>=15 and info['inside'] and info['imgH']>0 and info['urlTop']>=info['imgBottom']-1, (width,height,info)
    print(f'PASS RC162 QR {width}x{height}: code and destination visible')
   await page.locator('.participant-access-qr').evaluate('el=>{el.dataset.qrShowUrl="false";el.querySelector(".participant-qr-url").remove()}')
   assert await page.locator('.participant-qr-url').count()==0
   grid=await page.locator('.participant-access-qr').evaluate('el=>getComputedStyle(el).gridTemplateRows')
   assert len(grid.split())==1,grid
   print('PASS RC162 QR URL off: code expands without hidden layout row')
  finally:await browser.close()
if __name__=='__main__':asyncio.run(main())
