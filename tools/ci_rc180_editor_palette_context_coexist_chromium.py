#!/usr/bin/env python3
"""RC180: selection tools and wrapped insert rail must BOTH receive native clicks.

Regression for GitHub Actions 41913987787. The RC179 raised the whole
editor stage to make Duplica selezione clickable, but its fixed toolbar then
intercepted clicks on the Linee insertion palette. Neither forcing Playwright
clicks nor synthetic pointer dispatch is an acceptable workaround.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / 'apps/web/src/style.css'


def fixture():
    icons = [
        f'<span class="editor-icon-wrapper"><button type="button" class="editor-icon-tool" data-widget-kind="test{i}" '
        f'aria-label="Aggiungi widget {i}" onclick="window.widgets=(window.widgets||0)+1">W{i}</button></span>'
        for i in range(22)
    ]
    return '''<!doctype html><html lang="it"><head><meta charset="utf-8"></head><body>
    <section class="panel powerpoint-editor editor-ux-v2" aria-label="Editor grafico delle pagine">
      <header class="editor-mock-header">Editor</header>
      <aside class="page-editor-sidebar">Pagine</aside>
      <aside class="editor-widget-rail" aria-label="Aggiungi widget"><div class="editor-widget-grid">
        ''' + ''.join(icons[:4]) + '''
        <span class="editor-graphic-wrapper"><button type="button" class="editor-icon-tool" data-graphic-palette="line" aria-label="Aggiungi widget: Linee" onclick="window.lines=(window.lines||0)+1">Linee</button></span>
        ''' + ''.join(icons[4:]) + '''</div></aside>
      <section class="editor-stage" data-editor-device="desktop">
        <div class="editor-canvas-slot"><div class="canvas-editor-group" data-tools-open="true">
          <div class="canvas-editor-tools"><button type="button" id="duplicate" onclick="window.duplicates=(window.duplicates||0)+1">Duplica selezione</button></div>
          <div class="canvas-editor-tools" role="group" aria-label="Allineamento widget selezionati"><button type="button" id="align" onclick="window.alignments=(window.alignments||0)+1">Sinistra</button></div>
          <div class="canvas-with-rulers"><div class="widget-canvas" role="group" aria-label="Canvas grafico widget"></div></div>
        </div></div>
      </section>
    </section></body></html>'''


async def verify(browser, width, height):
    page = await browser.new_page(viewport={'width': width, 'height': height})
    try:
        await page.set_content(fixture())
        await page.add_style_tag(path=str(CSS))
        rail = page.get_by_role('complementary', name='Aggiungi widget')
        line = rail.get_by_role('button', name='Aggiungi widget: Linee')
        duplicate = page.get_by_role('button', name='Duplica selezione')
        align = page.get_by_role('button', name='Sinistra', exact=True)
        for label, control in [('duplicate', duplicate), ('line', line), ('align', align), ('line', line)]:
            await control.scroll_into_view_if_needed()
            hit = await control.evaluate('''el=>{
                const r=el.getBoundingClientRect(),x=r.x+r.width/2,y=r.y+r.height/2;
                const owner=document.elementFromPoint(x,y);
                return {x,y,tag:owner?.tagName,ok:owner===el||el.contains(owner),
                  intercepted:owner?.closest('.editor-widget-rail')?'rail':owner?.closest('.canvas-editor-tools')?'context':'other'};
            }''')
            print('HIT',width,label,hit,flush=True)
            assert hit['ok'], f'{width}x{height} {label} is covered: {hit}'
            await control.click(timeout=3000)  # Genuine native pointer, no force or dispatch.
        assert await page.evaluate('window.duplicates===1 && window.alignments===1 && window.lines===2')
        print(f'PASS RC180 Chromium {width}x{height}: selection and Linee palette coexist with genuine pointer clicks')
    finally:
        await page.close()


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'), args=['--no-sandbox'])
        try:
            for width,height in [(1440,940),(960,800),(390,844)]:
                await verify(browser,width,height)
        finally:
            await browser.close()


if __name__=='__main__':
    asyncio.run(main())
