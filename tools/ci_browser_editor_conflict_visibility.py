#!/usr/bin/env python3
"""RC120: fail closed if a real editor revision conflict is visually clipped.

Uses the production editor stylesheet, the exact header/toolbar structure and
Chromium layout rather than source-only assertions. No backend or credentials.
"""
import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf-8')


def fixture(title: str = 'CI real PostgreSQL editor autosave acceptance', status: str = 'Conflitto di revisione') -> str:
    return f'''<!doctype html><html lang="it"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>{CSS}</style>
<section class="panel powerpoint-editor editor-ux-v2" aria-label="Editor grafico delle pagine">
<header class="editor-mock-header">
 <div class="editor-mock-brand"><img alt="Quorivio" src="/editor-quorivio-logo.svg">
  <span>{title}</span><div class="editor-presenter-identities" aria-label="Proprietario e collaboratori della sessione"><span class="editor-owner-chip">Owner: CI Presenter Profile</span></div>
 </div>
 <div class="editor-mock-actions">
 <span role="status" aria-live="polite" class="editor-autosave-indicator has-error">{status}</span>
 <button type="button" class="editor-preview-open editor-schemes-open">▤ Schemi</button>
 <button type="button" class="editor-preview-open preview-presenter">▶ Presentatore</button>
 <button type="button" class="editor-preview-open preview-participant">▶ Partecipante</button>
 <button type="button" class="editor-preview-open preview-both">▣ Affiancate</button>
 <button type="button" class="editor-exit">Esci</button></div></header>
</section></html>'''


async def verify():
    launch = {'executable_path': os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(**launch, headless=True, args=['--no-sandbox'])
        try:
            for width in (1440, 1100, 960, 390):
                page = await browser.new_page(viewport={'width': width, 'height': 900})
                try:
                    await page.set_content(fixture())
                    # Use the same exact locator that detected the RC119 failure.
                    status = page.get_by_role('region', name='Editor grafico delle pagine').get_by_text('Conflitto di revisione', exact=True)
                    await expect(status).to_be_visible()
                    values = await status.evaluate('''e => {
                      const b = e.getBoundingClientRect(), h = e.closest('.editor-mock-header').getBoundingClientRect();
                      return { x:b.x, y:b.y, w:b.width, h:b.height, scroll:e.scrollWidth,
                        headerWidth:h.width, visible:getComputedStyle(e).visibility, overflow:getComputedStyle(e).overflow }
                    }''')
                    assert values['w'] >= 115, f'{width}px: status compressed: {values}'
                    assert values['x'] >= 0 and values['x'] + values['w'] <= width + 1, f'{width}px: status offscreen: {values}'
                    assert values['scroll'] <= values['w'] + 3, f'{width}px: status text clipped: {values}'
                    print(f'PASS RC120 Chromium {width}px: editor revision conflict remains visible ({values["w"]:.1f}px)')
                finally:
                    await page.close()
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(verify())
