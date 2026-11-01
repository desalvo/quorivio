#!/usr/bin/env python3
"""RC105 Chromium geometry regression for the actual compiled editor CSS.

No dependency on a fixture pretending to render the React editor: that is covered
by CI editor workflow. This guard proves CSS handle visibility/position and the
floating panels' non-participation in normal canvas layout.
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf-8')
EDGES = 'n ne e se s sw w nw'.split()
HANDLE_HTML = ''.join(f'<span class="widget-resize-edge edge-{edge}" data-resize-edge="{edge}"></span>' for edge in EDGES)


def run():
    # A genuine art-themed widget uses the historical selector which previously
    # changed every direct child's positioning and scattered the resize handles.
    html = f'''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>{CSS}</style>
    <style>.test-canvas{{position:absolute;top:70px;left:30px;width:70vw;height:58vh}}
    .test-widget{{left:10%;top:10%;width:45%;height:40%;}}
    </style></head><body><div class="editor-ux-v2"><div class="test-canvas">
    <div class="widget-canvas-item test-widget" data-art-theme="paper" data-selected="false">text{HANDLE_HTML}<span class="widget-rotate-handle"></span><button class="canvas-remove">×</button></div>
    </div></div></body></html>'''
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get('QUORIVIO_BROWSER_BIN','/usr/bin/chromium'), headless=True, args=['--no-sandbox'])
        for width, height in ((1440,900),(390,844)):
            page=browser.new_page(viewport={'width':width,'height':height})
            page.set_content(html)
            info=page.evaluate('''() => {const w=document.querySelector('.test-widget');const b=w.getBoundingClientRect();
              return {rect:[b.x,b.y,b.width,b.height],handles:[...document.querySelectorAll('[data-resize-edge]')].map(e=>({display:getComputedStyle(e).display,position:getComputedStyle(e).position})),remove:getComputedStyle(document.querySelector('.canvas-remove')).visibility};}''')
            assert all(h['display']=='none' for h in info['handles']),f'unselected handles visible at {width}px: {info}'
            assert info['remove']=='hidden',f'unselected remove visible at {width}px'
            page.locator('.test-widget').evaluate("el=>el.dataset.selected='true'")
            measured=page.evaluate('''() => {const w=document.querySelector('.test-widget').getBoundingClientRect();
              return Object.fromEntries([...document.querySelectorAll('[data-resize-edge]')].map(e=>{const r=e.getBoundingClientRect();return [e.dataset.resizeEdge,{display:getComputedStyle(e).display,position:getComputedStyle(e).position,x:r.left+r.width/2-w.left,y:r.top+r.height/2-w.top}]}));}''')
            desired={'n':(.5,0),'ne':(1,0),'e':(1,.5),'se':(1,1),'s':(.5,1),'sw':(0,1),'w':(0,.5),'nw':(0,0)}
            for edge,(rx,ry) in desired.items():
                h=measured[edge]; assert h['display']=='block' and h['position']=='absolute',f'{edge} not absolute/visible: {h}'
                assert abs(h['x']-info['rect'][2]*rx)<2 and abs(h['y']-info['rect'][3]*ry)<2,f'{width}px displaced {edge}: {h}'
            page.locator('.test-widget').evaluate("el=>el.dataset.selected='false'")
            assert page.locator('[data-resize-edge]').first.evaluate("e=>getComputedStyle(e).display")=='none'
            # These are the actual CSS classes after the RC105 portal/overlay change.
            page.evaluate('''() => {const panel=document.createElement('div');panel.className='widget-selection-palette editor-floating-panel';
              panel.innerHTML='<div class="palette-ribbon-head">Formato widget</div><div class="palette-ribbon-groups">Carattere</div>';
              Object.assign(panel.style,{left:'14px',top:'15px'});document.body.append(panel);}
            ''')
            after=page.locator('.test-widget').bounding_box()
            before=info['rect']
            assert all(abs(a-b)<.5 for a,b in zip((after['x'],after['y'],after['width'],after['height']),before)),f'floating ribbon resized canvas {width}'
            assert page.locator('.widget-selection-palette').evaluate("e=>getComputedStyle(e).position")=='fixed'
            assert page.locator('.widget-selection-palette').evaluate("e=>e.getBoundingClientRect().width<=innerWidth-8")
            print(f'PASS Chromium RC105 {width}x{height}: artistic widget handles aligned and selection-only; floating ribbon preserves widget geometry')
            page.close()
        browser.close()

if __name__ == '__main__': run()
