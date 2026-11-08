#!/usr/bin/env python3
"""RC266 computed-style acceptance: both floating editor panel families resize.

Uses actual project CSS in headless Chromium; unlike source-pattern contracts, it
checks the cascade including legacy !important rules and mobile overrides.
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[1]
css = (root/'apps/web/src/style.css').read_text()
html=f'''<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"/><style>{css}</style></head><body><section class="editor-ux-v2 editor-floating-scope"><div id="props" class="editor-context-drawer editor-floating-panel"><div class="editor-drawer-heading">Properties</div><div style="min-height:45px">Widget properties</div><button type="button" class="editor-floating-resize-handle" aria-label="Resize properties"></button></div></section><div id="ribbon" class="widget-selection-palette editor-floating-panel"><div class="palette-ribbon-head">Widget format</div><div class="palette-ribbon-groups">Font etc</div><button type="button" class="editor-floating-resize-handle" aria-label="Resize format"></button></div></body></html>'''
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(headless=True,executable_path=os.getenv('QUORIVIO_BROWSER_BIN','/usr/bin/chromium'),args=['--no-sandbox'])
    for vw,vh in [(1440,900),(390,844),(280,220)]:
        page=browser.new_page(viewport={'width':vw,'height':vh})
        page.set_content(html)
        for css_id,width,height in [('props',360,330),('ribbon',620,220)]:
            capwidth=max(1,vw-16)
            capheight=max(1,vh-16)
            proposed_width=min(capwidth,max(min((320 if css_id=='ribbon' else 280),capwidth),width))
            proposed_height=min(capheight,max(min((115 if css_id=='ribbon' else 160),capheight),height))
            page.locator('#'+css_id).evaluate('''(element, size) => {
                element.style.setProperty('--editor-floating-width', `${size[0]}px`);
                element.style.setProperty('--editor-floating-height', `${size[1]}px`);
                element.style.left = '12px';element.style.top = '12px';
            }''',[proposed_width,proposed_height])
            actual=page.locator('#'+css_id).evaluate('''element=>{const style=getComputedStyle(element),grip=element.querySelector('.editor-floating-resize-handle');return {width:element.getBoundingClientRect().width,height:element.getBoundingClientRect().height,grip:getComputedStyle(grip).display,position:getComputedStyle(element).position}}''')
            assert abs(actual['width']-proposed_width)<1.5,(vw,vh,css_id,actual,proposed_width)
            assert abs(actual['height']-proposed_height)<1.5,(vw,vh,css_id,actual,proposed_height)
            assert actual['grip']=='block' and actual['position']=='fixed',(vw,vh,css_id,actual)
        page.close()
        print(f'RC266 chromium CSS PASS at {vw}x{vh}: ribbon and properties resize handles remain available')
    # RC247 studio zoom is applied to <html> (80% at the UI default), so
    # logical fixed-position offsets must use documentElement.clientWidth/Height.
    page=browser.new_page(viewport={'width':1440,'height':900})
    page.set_content(html)
    for zoom in ('80%','70%','120%'):
        page.evaluate('(value)=>document.documentElement.style.zoom=value',zoom)
        page.wait_for_timeout(50)  # CSS zoom triggers asynchronous layout/ResizeObserver
        measurement=page.evaluate('''()=>{
            const zoom=parseFloat(getComputedStyle(document.documentElement).zoom);
            const vw=innerWidth/zoom;
            const vh=innerHeight/zoom;
            const panel=document.querySelector('#props');
            panel.style.left=(vw-112)+'px';panel.style.top=(vh-44)+'px';
            const rect=panel.getBoundingClientRect();
            return {vw,vh,left:rect.left,top:rect.top,zoom:parseFloat(getComputedStyle(document.documentElement).zoom)};
        }''')
        assert abs(measurement['vw']*measurement['zoom']-1440)<2,measurement
        assert abs(measurement['vh']*measurement['zoom']-900)<2,measurement
        assert measurement['left']>1250,measurement
        assert measurement['top']>800,measurement
        print(f"RC266 Chromium CSS zoom {zoom} PASS: dock is reachable at physical viewport edges")
    page.close()
    browser.close()
