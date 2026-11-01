#!/usr/bin/env python3
"""Standalone, network-free Chromium regression for mobile visual/layout viewport mismatch.

Run locally with QUORIVIO_CHROMIUM_PATH=/usr/bin/chromium python3 tools/ci_cookie_viewport.py.
The full CI already exercises the real application via ci_browser_editor.py.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

CSS=(Path(__file__).resolve().parents[1]/'apps/web/src/style.css').read_text(encoding='utf-8')


def fixture(width):
    # width=574 emulates the observed mobile layout viewport (574x1243)
    # while the Playwright device's visual viewport is 390x844.
    return f'''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style></head>
    <body><div id="root" style="min-width:{width}px"><main class="dashboard"><div class="welcome">Welcome</div></main></div>
    <dialog class="panel functional-cookie-dialog" aria-label="Informativa cookie funzionali">
    <h3>Cookie funzionali</h3><p>Quorivio utilizza cookie tecnici necessari per autenticazione, sessioni e sicurezza.
    Non sono utilizzati cookie di profilazione da questa funzione.</p>
    <button class="primary small" onclick="this.dataset.acknowledged='yes'">Ho capito</button></dialog>
    </body></html>'''


async def check(browser, *, mobile):
    context=await browser.new_context(viewport={'width':390,'height':844} if mobile else {'width':1440,'height':1000},
                                      is_mobile=mobile,has_touch=mobile)
    page=await context.new_page()
    await page.set_content(fixture(574 if mobile else 1440))
    await page.evaluate("document.querySelector('dialog').showModal()")
    result=await page.evaluate('''() => {
      const dialog=document.querySelector('dialog'),button=dialog.querySelector('button');
      const box=button.getBoundingClientRect(),viewport=window.visualViewport;
      const cx=box.left+box.width/2,cy=box.top+box.height/2;
      return {modal:dialog.matches(':modal'),layoutHeight:window.innerHeight,
        visualHeight:viewport.height,buttonY:Math.round(cy),
        inViewport:cx>=viewport.offsetLeft && cx<viewport.offsetLeft+viewport.width &&
          cy>=viewport.offsetTop && cy<viewport.offsetTop+viewport.height};
    }''')
    assert result['modal'] and result['inViewport'],result
    if mobile:
        assert result['layoutHeight']>result['visualHeight'],result
    await page.get_by_role('dialog',name='Informativa cookie funzionali').get_by_role('button',name='Ho capito').click(timeout=3000)
    assert await page.locator('dialog button').get_attribute('data-acknowledged')=='yes',result
    await context.close()
    print('PASS', 'mobile' if mobile else 'desktop',result)


async def main():
    async with async_playwright() as pw:
        launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
        try:
            await check(browser,mobile=False)
            await check(browser,mobile=True)
        finally:
            await browser.close()


if __name__=='__main__':
    asyncio.run(main())
