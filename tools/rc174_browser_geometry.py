#!/usr/bin/env python3
"""Optional real Chromium CSS acceptance for the live participant's slide.

This is an isolated DOM/CSS check, not an authenticated React or PostgreSQL
session. It deliberately uses the same DOM classes/styles as the React stage.
"""
from __future__ import annotations

import html
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')

def document(mode='stage-fidelity'):
    return '''<!doctype html><html lang="it"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"/>
<style>'''+CSS+'''</style><div class="app"><main class="narrow participant-live-view participant-slide-active">
<h1 class="participant-session-heading-offscreen">Sessione scuola</h1>
<section class="panel"><div class="audience-stage-scroll">
<div class="audience-widget-layout '''+html.escape(mode)+'''" id="slide" style="background-color:rgb(246,250,255);background-image:linear-gradient(rgb(200,210,220),rgb(230,240,250))">
<div class="page-widget" id="question" data-widget-kind="question" style="position:absolute;left:5%;top:22%;width:44%;height:32%;--stage-x:5%;--stage-y:22%;--stage-width:44%;--stage-height:32%;--stage-rotation:0deg;"><label>Una domanda<textarea rows="2">Risposta</textarea></label></div>
<div class="page-widget" id="rating" data-widget-kind="rating" style="position:absolute;left:55%;top:22%;width:30%;height:32%;--stage-x:55%;--stage-y:22%;--stage-width:30%;--stage-height:32%;--stage-rotation:0deg;"><div class="rating-choice-buttons"><button>0</button><button>1</button><button>2</button></div></div>
<div class="page-widget" id="shape" data-widget-kind="shape" style="position:absolute;left:4%;top:65%;width:33%;height:22%;--stage-x:4%;--stage-y:65%;--stage-width:33%;--stage-height:22%;--stage-rotation:0deg;"></div>
</div></div></section></main></div></html>'''

def metrics(page):
    return page.evaluate('''() => {
      const r=id=>{const e=document.getElementById(id),b=e.getBoundingClientRect(),s=getComputedStyle(e);return {x:b.left,y:b.top,w:b.width,h:b.height,display:s.display,pos:s.position,bg:s.backgroundImage}};
      const q=document.querySelector('#question textarea').getBoundingClientRect();
      const btn=document.querySelector('#rating button').getBoundingClientRect();
      const title=document.querySelector('main>h1').getBoundingClientRect();
      return {slide:r('slide'),question:r('question'),rating:r('rating'),shape:r('shape'),textarea:{w:q.width,h:q.height},button:{w:btn.width,h:btn.height},heading:{w:title.width,h:title.height},docScroll:document.documentElement.scrollWidth,inner:innerWidth};
    }''')

def check():
    with sync_playwright() as p:
        executable=os.environ.get('QUORIVIO_CHROMIUM_PATH') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').is_file() else None)
        browser=p.chromium.launch(**({'executable_path':executable} if executable else {}),headless=True,args=['--no-sandbox'])
        try:
            samples={}
            for width in (1280,390,320):
                page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1)
                page.set_content(document())
                m=metrics(page)
                slide=m['slide']
                assert abs(slide['w']/slide['h']-16/9)<.02,(width,m)
                for id,x,y,w,h in [('question',5,22,44,32),('rating',55,22,30,32),('shape',4,65,33,22)]:
                    r=m[id]
                    assert abs((r['x']-slide['x'])/slide['w']*100-x)<1,(width,id,r,slide)
                    assert abs((r['y']-slide['y'])/slide['h']*100-y)<1,(width,id,r,slide)
                    assert abs(r['w']/slide['w']*100-w)<1,(width,id,r,slide)
                    assert abs(r['h']/slide['h']*100-h)<1,(width,id,r,slide)
                assert m['heading']['w']<=2 and m['heading']['h']<=2,(width,m)
                samples[width]=m
                page.close()
            # Detect control-size regression seen in real mobile screenshots:
            # the stage shrinks with viewport but a two-row textarea used to
            # stay at ~57px regardless of viewport width.
            desktop=samples[1280]
            for width in (390,320):
                current=samples[width]
                ratio=current['slide']['w']/desktop['slide']['w']
                assert abs(current['textarea']['h']/desktop['textarea']['h']-ratio)<.06,(width,current,desktop)
                assert current['docScroll']<=current['inner']+1,(width,current)
            page=browser.new_page(viewport={'width':390,'height':900})
            page.set_content(document('stage-reading'))
            m=metrics(page)
            assert m['slide']['bg']=='none',m
            assert m['slide']['pos']=='relative'
            assert m['shape']['display']=='none'
            assert m['question']['pos']=='relative',m
            assert m['textarea']['h']>=44,m  # large usable reading-mode input
            page.close()
            for width in (1280,390,320):
                m=samples[width]
                print(f'Viewport {width}: stage={m["slide"]["w"]:.1f}x{m["slide"]["h"]:.1f}, '
                      f'textarea={m["textarea"]["w"]:.1f}x{m["textarea"]["h"]:.1f}, '
                      f'button={m["button"]["w"]:.1f}x{m["button"]["h"]:.1f}')
            print('PASS: geometry, hidden visual chrome, reading reflow/neutral background (Chromium fixture)')
        finally:
            browser.close()

if __name__=='__main__': check()
