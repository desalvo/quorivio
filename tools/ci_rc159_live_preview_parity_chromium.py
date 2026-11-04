#!/usr/bin/env python3
"""Test actual Chromium layout calculations for same authored title on 3 slide surfaces."""
from pathlib import Path
import os, shutil
from playwright.sync_api import sync_playwright
CSS=Path(__file__).resolve().parents[1].joinpath('apps/web/src/style.css').read_text()

HTML='''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>
<div class="projection presenter-stage" id="presenter"><div class="projection-page-content" style="width:100%"><div class="projection-widget" data-widget-kind="title" style="position:absolute;left:8%;top:3%;width:84%;height:12%;font-family:Arial;font-size:1.875cqw;--authored-widget-font-size:1.875cqw;display:flex"><div class="widget-fit-frame"><div class="widget-fit-content"><h2 class="projection-slide-title">Titolo della prova</h2></div></div></div></div></div>
<div id="preview"><div class="rehearsal-widgets" style="position:relative;width:100%;aspect-ratio:16/9"><div class="rehearsal-widget" data-widget-kind="title" style="--stage-x:8%;--stage-y:3%;--stage-width:84%;--stage-height:12%;font-family:Arial;font-size:1.875cqw;--authored-widget-font-size:1.875cqw;display:flex"><h2 class="projection-slide-title">Titolo della prova</h2></div></div></div>
<main class="narrow participant-live-view" id="participant"><div class="audience-stage-scroll"><div class="audience-widget-layout stage-fidelity"><div class="page-widget" data-widget-kind="title" style="--stage-x:8%;--stage-y:3%;--stage-width:84%;--stage-height:12%;position:absolute;font-family:Arial;--authored-widget-font-size:1.875cqw;"><h2 class="projection-slide-title">Titolo della prova</h2></div></div></div></main>
</body></html>'''

def run():
    chromium=os.environ.get('QUORIVIO_CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
    if not chromium:raise RuntimeError('Real Chromium missing; parity cannot silently skip')
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path=chromium,args=['--no-sandbox'])
        try:
            for width in (1440,390):
                page=browser.new_page(viewport={'width':width,'height':860},device_scale_factor=1)
                page.set_content(HTML)
                page.add_style_tag(content=CSS)
                result=page.evaluate('''()=>{
                  const selectors=['#presenter .projection-page-content','#preview .rehearsal-widgets','#participant .audience-widget-layout'];
                  const boxes=selectors.map(s=>document.querySelector(s));
                  const viewportWidth=window.innerWidth;
                  const title=boxes.map(e=>e.querySelector('.projection-slide-title'));
                  return {viewportWidth,stages:boxes.map(e=>({width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height})),font:title.map(e=>getComputedStyle(e).fontSize),family:title.map(e=>getComputedStyle(e).fontFamily),titlePosition:title.map(e=>{const r=e.getBoundingClientRect(),p=e.closest('[data-widget-kind]');const b=p.getBoundingClientRect(),c=p.parentElement.getBoundingClientRect();return {x:(b.left-c.left)/c.width,y:(b.top-c.top)/c.height}})};
                }''')
                # Browser viewport differences are allowed; each artboard must be the same size,
                # so measured font parity is evaluated at equal authored stage widths.
                aw=result['stages'][2]
                assert .555<aw['height']/aw['width']<.57,(width,result)
                assert aw['width']<=width+1,(width,result)
                # A projection heading must not inherit the global 35–62px heading rule.
                fs=[float(x.removesuffix('px')) for x in result['font']]
                actual_width=result['stages'][0]['width']
                assert abs(fs[0]-actual_width*24/1280)<1.2,(width,fs,result)
                assert result['family'][0].startswith('Arial') and result['family'][2].startswith('Arial'),result
                assert all(abs(p['x']-.08)<.02 and abs(p['y']-.03)<.02 for p in result['titlePosition']),(width,result)
                print(f"PASS Chromium {width}px live 16:9 canvas / title geometry; title fonts {result['font']}")
                page.close()
        finally:browser.close()
if __name__=='__main__':run()
