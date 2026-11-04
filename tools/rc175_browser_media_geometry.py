#!/usr/bin/env python3
"""RC175 Chromium DOM/CSS regression: faithful mobile media geometry.

This probes the actual shipped stylesheet at desktop and narrow viewport sizes.
It does not replace an authenticated React/PostgreSQL participant test.
"""
from __future__ import annotations

import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')
PHOTO = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
         "width='320' height='80'%3E%3Crect width='320' height='80' "
         "fill='%23de4555'/%3E%3C/svg%3E")


def fixture(mode: str = 'stage-fidelity') -> str:
    assert mode in ('stage-fidelity', 'stage-reading', 'stage-phone')
    stage_height = 'height:980px;' if mode == 'stage-phone' else ''
    return f'''<!doctype html><html lang="it"><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>{CSS}</style><main class="participant-live-view participant-slide-active">
<section class="panel"><div class="audience-stage-scroll"><div id="slide"
class="audience-widget-layout {mode}" style="{stage_height}background-color:lightblue;background-image:linear-gradient(red,blue)">
<div class="page-widget" id="image-widget" data-widget-kind="image"
style="--stage-x:5%;--stage-y:12%;--stage-width:26%;--stage-height:40%;left:5%;top:12%;width:26%;height:40%;position:absolute">
<div class="widget-fit-frame"><div class="widget-fit-content">
<img id="image" class="projection-media" src="{PHOTO}" alt="Sample image"/></div></div></div>
<div class="page-widget" id="video-widget" data-widget-kind="video"
style="--stage-x:35%;--stage-y:12%;--stage-width:26%;--stage-height:40%;left:35%;top:12%;width:26%;height:40%;position:absolute">
<div class="widget-fit-frame"><div class="widget-fit-content">
<video id="video" class="projection-media" controls preload="none"></video></div></div></div>
<div class="page-widget" id="crop-widget" data-widget-kind="image"
style="--stage-x:65%;--stage-y:12%;--stage-width:26%;--stage-height:40%;left:65%;top:12%;width:26%;height:40%;position:absolute">
<div class="widget-fit-frame"><div class="widget-fit-content">
<div class="pptx-cropped-image projection-media" role="img" aria-label="cropped">
<img id="cropped" src="{PHOTO}" alt="" aria-hidden="true"
style="position:absolute;max-width:none;max-height:none;width:125%;height:125%;left:-12.5%;top:-12.5%"/>
</div></div></div></div></div></div></section></main></html>'''


MEASURE = '''() => {
  const rect = id => {const e=document.getElementById(id),r=e.getBoundingClientRect();
    return {w:r.width,h:r.height,x:r.left,y:r.top}};
  return {stage:rect('slide'),image:rect('image'),video:rect('video'),
    cropped:rect('cropped'),cropBox:rect('crop-widget'),
    imageBox:rect('image-widget'),videoBox:rect('video-widget'),
    background:getComputedStyle(document.getElementById('slide')).backgroundImage,
    docScroll:document.documentElement.scrollWidth,viewport:innerWidth};
}'''


def verify() -> None:
    path = os.environ.get('QUORIVIO_CHROMIUM_PATH')
    if not path and Path('/usr/bin/chromium').is_file():
        path = '/usr/bin/chromium'
    with sync_playwright() as p:
        options = {'executable_path': path} if path else {}
        browser = p.chromium.launch(headless=True,args=['--no-sandbox'],**options)
        try:
            sample = {}
            for viewport in (1280, 390, 320):
                page = browser.new_page(viewport={'width':viewport,'height':850})
                page.set_content(fixture())
                m = page.evaluate(MEASURE)
                sample[viewport] = m
                assert abs(m['stage']['w']/m['stage']['h']-16/9)<.025, (viewport,m)
                for item, container in (('image','imageBox'), ('video','videoBox')):
                    # A media node fills its widget's content box at each viewport;
                    # it must not revert to the source asset's intrinsic ratio.
                    assert .85<m[item]['h']/m[container]['h']<1.02, (viewport,item,m)
                assert m['cropped']['h']>m['cropBox']['h']*.85, (viewport,m)
                assert m['docScroll']<=m['viewport']+2, (viewport,m)
                print(f'{viewport}px: image {m["image"]["w"]:.0f}x{m["image"]["h"]:.0f}, '
                      f'video {m["video"]["w"]:.0f}x{m["video"]["h"]:.0f}')
                page.close()
            wide=sample[1280]
            for width in (390,320):
                m=sample[width]
                ratio=m['stage']['w']/wide['stage']['w']
                for kind in ('image','video'):
                    actual=m[kind]['h']/wide[kind]['h']
                    assert abs(actual-ratio)<.05, (width,kind,actual,ratio)
            # The reading mode intentionally does not paint the authored
            # background into a second slide-shaped canvas.
            page=browser.new_page(viewport={'width':390,'height':900})
            page.set_content(fixture('stage-reading'))
            m=page.evaluate(MEASURE)
            assert m['background']=='none',m
            page.close()
            print('PASS RC175: faithful media geometry + neutral reading background')
        finally:
            browser.close()


if __name__ == '__main__': verify()
