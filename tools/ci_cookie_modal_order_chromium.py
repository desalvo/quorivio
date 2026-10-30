#!/usr/bin/env python3
"""Check that native modal hides underlying buttons until an actual click."""
import asyncio
import os
from playwright.async_api import async_playwright, expect, TimeoutError as PlaywrightTimeout

async def main():
 async with async_playwright() as pw:
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
  try:
   for viewport in ({'width':1440,'height':940},{'width':390,'height':844}):
    page=await browser.new_page(viewport=viewport)
    await page.set_content('''''''''<button>Apri sessione</button><dialog aria-label="Informativa cookie funzionali"><button>Ho capito</button></dialog><script>document.querySelector("dialog").showModal();document.querySelector("dialog button").addEventListener("click",()=>document.querySelector("dialog").close())</script>''''''''' )
    notice=page.get_by_role('dialog',name='Informativa cookie funzionali')
    assert await notice.evaluate("node=>node.matches(':modal')")
    underlying=page.get_by_role('button',name='Apri sessione')
    await expect(underlying).to_be_visible()
    try:
     await underlying.click(timeout=800)
    except PlaywrightTimeout:
     pass
    else:
     raise AssertionError('Native modal must intercept pointer events until acknowledgement')
    await notice.get_by_role('button',name='Ho capito').click()
    await expect(notice).not_to_be_visible()
    await underlying.click(timeout=2000)
    await page.close()
   print('PASS real Chromium native modal: presenter navigation hidden until cookie acknowledgement on desktop and mobile')
  finally:
   await browser.close()

if __name__=='__main__':asyncio.run(main())
