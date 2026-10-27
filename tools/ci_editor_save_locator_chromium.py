#!/usr/bin/env python3
"""Isolated real-Chromium regression for the duplicate accessible Save labels.

Runs before full React acceptance. No network, credentials or production data.
"""
import asyncio
import os
from playwright.async_api import async_playwright, expect
from ci_editor_context_tools import editor_save_button

HTML = """<!doctype html><html lang="it"><body>
<button aria-label="Salva layout" id="outside">Unrelated dashboard save</button>
<section role="region" aria-label="Editor grafico delle pagine">
  <button aria-label="Salva layout della pagina" id="icon">✓</button>
  <button aria-label="Salva layout" id="save">Salva layout</button>
</section>
<script>
  document.querySelectorAll('button').forEach(btn => btn.onclick = () =>
    document.body.dataset.clicked = btn.id);
</script></body></html>"""

async def verify(browser, *, touch):
    page=await browser.new_page(viewport={'width':390 if touch else 1440,'height':844 if touch else 900},
                                has_touch=touch,is_mobile=touch)
    try:
        await page.set_content(HTML)
        # A non-exact role locator is intentionally ambiguous, including
        # the icon label, and must not be reintroduced in browser E2E.
        assert await page.get_by_role('region',name='Editor grafico delle pagine').get_by_role(
            'button',name='Salva layout').count()==2
        target=editor_save_button(page)
        await expect(target).to_have_count(1)
        await expect(target).to_be_visible()
        await (target.tap() if touch else target.click())
        assert await page.locator('body').get_attribute('data-clicked')=='save'
        await target.evaluate('button => button.disabled = true')
        await expect(editor_save_button(page)).to_be_disabled()
    finally:
        await page.close()

async def main():
    async with async_playwright() as pw:
        opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await pw.chromium.launch(headless=True,args=['--no-sandbox'],**opts)
        try:
            await verify(browser,touch=False)
            await verify(browser,touch=True)
        finally:
            await browser.close()
    print('PASS Chromium exact editor Save locator: 2 colliding labels, dashboard isolation, desktop+touch and disabled state')

if __name__=='__main__':
    asyncio.run(main())
