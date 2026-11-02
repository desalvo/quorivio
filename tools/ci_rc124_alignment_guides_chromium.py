#!/usr/bin/env python3
"""RC124 actual Chromium CSS/pointer geometry for editor and slide-master guides.

The live React integration continues to be enforced by the full browser workflow;
this isolated check specifically fails on hidden/misaligned/interactive guides.
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
HTML='''<style>__CSS__</style>
<div class="editor-ux-v2" style="width:min(90vw,960px);aspect-ratio:16/9;display:block"><div class="widget-canvas" role="group" aria-label="Canvas di prova" style="width:100%;height:100%;margin:0">
<div class="widget-snap-grid" aria-hidden="true"></div>
<div class="widget-alignment-guides" aria-hidden="true">
<span class="widget-alignment-guide axis-x" style="left:50%" data-guide-source="canvas"></span>
<span class="widget-alignment-guide axis-y" style="top:35%" data-guide-source="widget"></span>
</div>
<div class="widget-canvas-item" style="left:40%;top:20%;width:20%;height:30%" data-widget-id="w">Content</div>
</div></div>'''


def main():
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            for width in (1440,390):
                page=browser.new_page(viewport={'width':width,'height':850})
                page.set_content(HTML.replace('__CSS__',CSS))
                # Model the actual editor stage, without unrelated app-shell constraints.
                page.add_style_tag(content='.editor-ux-v2{position:relative!important;width:90vw!important;max-width:960px!important;height:auto!important;aspect-ratio:16/9!important;display:block!important}.editor-ux-v2 .widget-canvas{width:100%!important;height:100%!important;aspect-ratio:16/9!important}')
                canvas=page.locator('.widget-canvas')
                box=canvas.bounding_box()
                assert box and box['width']>300,(width,box)
                x=page.locator('.widget-alignment-guide.axis-x')
                y=page.locator('.widget-alignment-guide.axis-y')
                assert x.count()==1 and y.count()==1
                assert x.is_visible() and y.is_visible(), f'invisible alignment guide {width}'
                xbox=x.bounding_box();ybox=y.bounding_box()
                assert xbox and ybox
                assert abs((xbox['x']-box['x'])/box['width']-.5)<.005,(width,xbox,box)
                assert abs((ybox['y']-box['y'])/box['height']-.35)<.005,(width,ybox,box)
                props=page.locator('.widget-alignment-guides').evaluate('el => getComputedStyle(el).pointerEvents')
                assert props=='none',f'guides intercept canvas clicks: {props}'
                hit=page.evaluate('''() => {
                    const b=document.querySelector('.widget-canvas').getBoundingClientRect();
                    const el=document.elementFromPoint(b.left+b.width/2,b.top+b.height*.35);
                    return el?.className||'';
                }''')
                assert 'alignment' not in str(hit),(width,hit)
                assert page.locator('.widget-snap-grid').evaluate('e=>getComputedStyle(e).backgroundSize')=='5% 5%, 5% 5%'
                print(f'PASS RC124 alignment guides and 5% grid: {width}px, geometry, pointer safety')
                page.close()
        finally:
            browser.close()

if __name__=='__main__':main()
