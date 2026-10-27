#!/usr/bin/env python3
"""Real Chromium preflight: editor canvas must not cover Save (CI 40513571247).

Uses production CSS and representative DOM geometry, including an *expanded*
accessible widget list with three entries. No JS overrides of layout or
pointer-events, no forced clicks, no external web/database. Both desktop and
mobile must be able to save and return to keyboard/touch controls.
"""
import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright, expect
from ci_editor_context_tools import editor_save_button

CSS = (Path(__file__).resolve().parents[1] / 'apps/web/src/style.css').read_text(encoding='utf-8')


def fixture():
    entries = ''
    for name in ('First', 'Second', 'Third'):
        controls = ''.join(f'<button type="button" aria-label="{action} {name}">{action}</button>'
                           for action in ('Sposta a sinistra', 'Sposta a destra', 'Sposta in alto',
                                          'Sposta in basso', 'Duplica', 'Porta in primo piano',
                                          'Porta sullo sfondo'))
        entries += f'<div class="canvas-accessible-row"><strong>{name}</strong><div>{controls}</div></div>'
    return '''<!doctype html><html lang="it"><head><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>
<div class="editor-ux-v2">
 <aside class="page-editor-sidebar" aria-label="Miniature delle pagine"></aside>
 <div class="editor-stage" role="region" aria-label="Editor grafico delle pagine">
  <div class="editor-canvas-slot"><div class="canvas-editor-group" data-tools-open="false">
   <div class="canvas-with-rulers"><div class="widget-canvas" style="width:100%;height:auto">
    <div class="widget-canvas-item" style="left:75%;top:70%;width:15%;height:10%"><button>Third</button></div>
   </div></div>
   <details class="canvas-accessible-controls" open role="region" aria-label="Organizzazione accessibile dei widget">
    <summary>Controlli accessibili per tastiera e touchscreen</summary>
    <div class="canvas-accessible-list">''' + entries + '''</div></details>
  </div></div>
  <div class="editor-bottom-controls" role="toolbar" aria-label="Salvataggio e navigazione editor">
   <button type="button" aria-label="Salva layout della pagina">Salva layout della pagina</button>
  </div>
  <div class="editor-secondary-workflow"><div class="downloads">
   <button type="button" class="primary small" onclick="document.querySelector('#result').textContent='saved'">Salva layout</button>
  </div></div>
 </div><aside class="editor-widget-rail"></aside><output id="result"></output>
</div></body></html>'''


async def verify(browser, width, height, touch):
    page = await browser.new_page(viewport={'width': width, 'height': height},
                                  is_mobile=touch, has_touch=touch)
    try:
        await page.set_content(fixture())
        await page.add_style_tag(content=CSS)
        save = editor_save_button(page)
        await expect(save).to_be_visible()
        await save.scroll_into_view_if_needed()
        hit = await save.evaluate('''element => {
            const b=element.getBoundingClientRect();
            const target=document.elementFromPoint(b.left+b.width/2,b.top+b.height/2);
            return target===element || element.contains(target);
        }''')
        assert hit, 'Expanded canvas controls intercept the real Save button'
        if touch:
            await save.tap()
        else:
            await save.click()
        await expect(page.locator('#result')).to_have_text('saved')
        # Accessible alternatives remain reachable after saving: the fix must
        # not hide, disable, or clip the expanded keyboard/touch controls.
        control = page.get_by_role('button', name='Porta in primo piano Third')
        await expect(control).to_be_visible()
        if touch:
            await control.tap()
        else:
            await control.click()
        await expect(page.locator('.canvas-accessible-controls')).to_have_attribute('open', '')
    finally:
        await page.close()


async def main():
    async with async_playwright() as pw:
        launch = {'executable_path': os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser = await pw.chromium.launch(headless=True, args=['--no-sandbox'], **launch)
        try:
            await verify(browser, 1440, 1000, False)
            await verify(browser, 390, 844, True)
        finally:
            await browser.close()
    print('PASS real Chromium canvas overflow: accessible rows and Save both clickable on desktop and touch')


if __name__ == '__main__':
    asyncio.run(main())
