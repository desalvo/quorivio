#!/usr/bin/env python3
"""RC234: real Chromium acceptance for the responsive widget palette.

Uses the existing static RC171 editor fixture; no API session, credentials or
external network. The mobile palette must wrap and scroll vertically, never
hide tools beyond the horizontal viewport.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright
from ci_rc171_editor_palette_chromium import html

ROOT = Path(__file__).resolve().parents[1]
WIDTHS = (320, 390, 440, 620, 740, 760, 761, 960, 1440)


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True,
            executable_path='/usr/bin/chromium',
            args=['--no-sandbox', '--disable-dev-shm-usage'],
        )
        try:
            for width in WIDTHS:
                page = await browser.new_page(viewport={'width': width, 'height': 740})
                try:
                    await page.set_content(html(), wait_until='domcontentloaded')
                    await page.add_style_tag(path=str(ROOT / 'apps/web/src/style.css'))
                    metrics = await page.evaluate('''() => {
                        const grid = document.querySelector('.editor-widget-grid');
                        const rail = document.querySelector('.editor-widget-rail');
                        const tools = [...grid.querySelectorAll('.editor-icon-wrapper')];
                        const css = getComputedStyle(grid);
                        const box = grid.getBoundingClientRect();
                        return {
                            gridWidth: grid.clientWidth, scrollWidth: grid.scrollWidth,
                            gridHeight: grid.clientHeight, scrollHeight: grid.scrollHeight,
                            wrap: css.flexWrap, overflowX: css.overflowX, overflowY: css.overflowY,
                            railWidth: rail.getBoundingClientRect().width,
                            tools: tools.length,
                            toolWidths: tools.map(tool => tool.getBoundingClientRect().width),
                            beyondRight: tools.some(tool => tool.getBoundingClientRect().right > box.right + 3),
                        };
                    }''')
                    assert metrics['wrap'] == 'wrap', f'palette does not wrap at {width}: {metrics}'
                    assert metrics['scrollWidth'] <= metrics['gridWidth'] + 3, f'horizontal overflow at {width}: {metrics}'
                    assert not metrics['beyondRight'], f'widget tool clipped horizontally at {width}: {metrics}'
                    assert metrics['tools'] == 19, f'widget/graphics tools missing at {width}: {metrics}'
                    assert all(40 <= w <= 72 for w in metrics['toolWidths']), f'oversized icon at {width}: {metrics}'
                    assert metrics['gridHeight'] <= min(740 * .3, 198) + 3, f'palette consumes the canvas at {width}: {metrics}'
                    if width <= 760:
                        assert metrics['railWidth'] <= width + 2, f'widget rail exceeds viewport at {width}: {metrics}'
                        assert metrics['overflowY'] == 'auto', f'cannot scroll to lower palette tools at {width}: {metrics}'
                    await page.locator('.editor-widget-grid .editor-graphic-wrapper:last-child').scroll_into_view_if_needed()
                    last_visible = await page.evaluate('''() => {
                        const grid = document.querySelector('.editor-widget-grid').getBoundingClientRect();
                        const last = document.querySelector('.editor-widget-grid .editor-graphic-wrapper:last-child').getBoundingClientRect();
                        return last.top >= grid.top - 3 && last.bottom <= grid.bottom + 3;
                    }''')
                    assert last_visible, f'last graphic tool is not reachable at {width}px'
                    print(f'PASS RC234 Chromium widget palette {width}px: 19 tools, no horizontal overflow, last tool reachable')
                finally:
                    await page.close()
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
