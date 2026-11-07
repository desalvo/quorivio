#!/usr/bin/env python3
"""RC248: real Chromium canvas must fit dynamic editor stage at every UI zoom.

The RC247 fullscreen adjustment grew the slide from viewport height instead of
available editor-stage height; the old CSS fails at 1440x900 by about 15 px.
The editor chrome can wrap, so fixed-height assumptions must never be used.
"""
from __future__ import annotations
import asyncio
import os
from playwright.async_api import async_playwright
from ci_editor_mock_layout_chromium import HTML


async def verify(browser, width: int, height: int, ui_scale: float):
    page = await browser.new_page(viewport={'width':width, 'height':height})
    try:
        await page.set_content(HTML)
        await page.evaluate('''scale => {
            document.documentElement.style.zoom = String(scale * 100) + '%';
            document.documentElement.style.setProperty('--quorivio-ui-scale', String(scale));
        }''', ui_scale)
        boxes = await page.evaluate('''() => {
            const box = selector => {
                const element = document.querySelector(selector);
                if (!element) throw Error('missing ' + selector);
                const r = element.getBoundingClientRect();
                const s = getComputedStyle(element);
                return {x:r.x,y:r.y,w:r.width,h:r.height,
                    scrollHeight:element.scrollHeight,clientHeight:element.clientHeight,
                    maxWidth:s.maxWidth,containerType:s.containerType};
            };
            return {editor:box('.editor-ux-v2'),stage:box('.editor-stage'),
                slot:box('.editor-canvas-slot'),slide:box('.widget-canvas')};
        }''')
        editor, stage, slot, slide = (boxes[k] for k in ('editor','stage','slot','slide'))
        assert abs(editor['w']-width)<3 and abs(editor['h']-height)<3, (width,height,ui_scale,boxes)
        assert 0 <= stage['y'] and stage['y']+stage['h'] <= height+2, boxes
        # Desktop: slide and its horizontal ruler must fit the stage content box.
        # The 16:9 canvas should grow to use most of the *remaining* stage area.
        if width > 760:
            assert stage['containerType']=='size', boxes
            assert slide['y'] >= stage['y']-1, boxes
            assert slide['y']+slide['h'] <= stage['y']+stage['h']+1.5, boxes
            assert slot['y'] >= stage['y']-1, boxes
            assert slot['y']+slot['h'] <= stage['y']+stage['h']+1.5, boxes
            assert stage['scrollHeight'] <= stage['clientHeight']+3, boxes
            assert slide['w']>=stage['w']*.54, boxes
        assert abs(slide['w']/slide['h'] - 16/9)<.035, boxes
        print(f'PASS RC248 Chromium {width}x{height} scale={ui_scale:.2f}: editor/stage fit, 16:9 slide, no wasted canvas width')
    finally:
        await page.close()

async def main():
    async with async_playwright() as playwright:
        opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await playwright.chromium.launch(headless=True,args=['--no-sandbox'],**opts)
        try:
            for width,height in ((1440,900),(1200,900),(960,760),(760,820),(390,844)):
                for scale in (0.64,0.80,0.96):
                    await verify(browser,width,height,scale)
        finally:
            await browser.close()

if __name__=='__main__':
    asyncio.run(main())
