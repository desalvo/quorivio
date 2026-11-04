#!/usr/bin/env python3
"""RC179 regression: Chromium must dispatch a real click to canvas selection tools.

The wrapped widget rail is intentionally a separate CSS grid row. Its stacking
context must never intercept fixed contextual tool buttons (the RC178 CI bug).
No force clicks, synthetic dispatch, or hidden-element shortcuts are allowed.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / 'apps/web/src/style.css'


def fixture() -> str:
    # The real editor groups the palette, canvas and contextual panels in this
    # order. Include enough items to make the palette wrap at desktop widths.
    icons = ''.join(
        f'<button type="button" class="editor-icon-tool" data-widget-kind="fixture{i}" '
        f'aria-label="Aggiungi widget {i}">Widget {i}</button>' for i in range(18)
    )
    return '''<!doctype html><html lang="it"><head><meta charset="utf-8"></head><body>
      <section class="panel powerpoint-editor editor-ux-v2" aria-label="Editor grafico delle pagine">
        <header class="editor-mock-header"><strong>Quorivio · Editor</strong></header>
        <aside class="page-editor-sidebar">Pagine</aside>
        <aside class="editor-widget-rail" aria-label="Aggiungi widget">
          <div class="editor-widget-grid">''' + icons + '''</div>
        </aside>
        <section class="editor-stage">
          <div class="editor-canvas-slot">
            <div class="canvas-editor-group" data-tools-open="true">
              <div class="canvas-editor-tools">
                <button type="button" id="duplicate" onclick="window.clicked = (window.clicked||0)+1">Duplica selezione</button>
              </div>
              <div class="canvas-editor-tools" role="group" aria-label="Allineamento widget selezionati">
                <button type="button" id="align" onclick="window.aligned = (window.aligned||0)+1">Allinea a sinistra</button>
              </div>
              <div class="canvas-with-rulers"><div class="widget-canvas"></div></div>
            </div>
          </div>
        </section>
      </section></body></html>'''


async def verify(browser, width: int, height: int) -> None:
    page = await browser.new_page(viewport={'width': width, 'height': height})
    await page.set_content(fixture())
    await page.add_style_tag(path=str(STYLE))
    rail = page.locator('.editor-widget-rail')
    button = page.get_by_role('button', name='Duplica selezione')
    assert await rail.is_visible() and await button.is_visible(), 'Editor fixture did not render'
    # Verify the actual native pointer hit test, not just DOM visibility.
    await button.scroll_into_view_if_needed()
    top_hit = await button.evaluate('''el => {
      const r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
      const hit=document.elementFromPoint(x,y);
      return {x,y,owner:hit?.closest('.editor-widget-rail')?'palette':
        (hit===el||el.contains(hit))?'tool':hit?.tagName||'none'};
    }''')
    assert top_hit['owner'] == 'tool', f'Palette intercepts selection tool at {width}px: {top_hit}'
    # A real Playwright click rechecks obstructions; no force or JS click.
    await button.click(timeout=3000)
    assert await page.evaluate('window.clicked === 1'), 'Native click did not reach duplicate tool'
    align = page.get_by_role('button', name='Allinea a sinistra')
    await align.click(timeout=3000)
    assert await page.evaluate('window.aligned === 1'), 'Second floating panel is not clickable'
    # The rail still works normally when pointer tools are dismissed.
    await page.locator('.canvas-editor-group').evaluate("el => el.setAttribute('data-tools-open','false')")
    await page.locator('.editor-widget-grid .editor-icon-tool').first.click(timeout=3000)
    print(f'PASS RC179 Chromium {width}x{height}: real contextual duplicate/alignment pointer; palette usable after close')
    await page.close()


async def main() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
        try:
            for width, height in [(1440, 900), (960, 800), (390, 844)]:
                await verify(browser, width, height)
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
