"""RC112 browser regression of shared master/page canvas CSS, not a compiled React E2E test."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()
HTML='''<style>{css}</style><section class="panel slide-scheme-workspace" style="width:min(900px,95vw);padding:8px">
<header class="slide-scheme-header"><h2>Editor schemi</h2><button type="button" class="slide-scheme-exit outline">Esci dagli schemi</button></header>
<div class="slide-scheme-ribbon"><div class="slide-scheme-ribbon-group"><strong>Allinea</strong><button>Centro</button></div></div>
<div class="slide-scheme-layout"><div class="slide-scheme-canvas"><div class="canvas-with-rulers"><div class="canvas-ruler-horizontal">0 10 20</div><div class="canvas-ruler-vertical">0 10 20</div><div class="widget-canvas" style="position:relative;width:100%;aspect-ratio:16/9">
<div class="widget-canvas-item" data-art-theme="studio" data-selected="true" style="left:12%;top:14%;width:33%;height:23%"><span class="widget-rotate-handle"></span>{edges}<button class="canvas-remove">x</button></div>
<div class="widget-canvas-item" data-art-theme="studio" data-selected="false" style="left:58%;top:41%;width:30%;height:20%"><span class="widget-rotate-handle"></span>{edges}<button class="canvas-remove">x</button></div>
</div></div></div><aside class="slide-scheme-inspector">Proprietà</aside></div></section>
<section class="powerpoint-editor editor-ux-v2" style="width:min(900px,95vw);padding:8px"><div class="canvas-with-rulers"><div class="canvas-ruler-horizontal">0 10</div><div class="canvas-ruler-vertical">0 10</div><div class="widget-canvas" style="position:relative;aspect-ratio:16/9"></div></div></section>'''
EDGES=['n','ne','e','se','s','sw','w','nw']

def checks(page,width):
 page.set_viewport_size({'width':width,'height':900})
 html=HTML.format(css=CSS,edges=''.join(f'<span class="widget-resize-edge edge-{e}" data-resize-edge="{e}"></span>' for e in EDGES))
 page.set_content(html.split('<section class="powerpoint-editor')[0])
 first=page.locator('.slide-scheme-workspace .widget-canvas-item').first
 second=page.locator('.slide-scheme-workspace .widget-canvas-item').nth(1)
 assert len([x for x in first.locator('.widget-resize-edge').all() if x.is_visible()])==8
 assert len([x for x in second.locator('.widget-resize-edge').all() if x.is_visible()])==0
 assert first.locator('.widget-rotate-handle').is_visible()
 assert not second.locator('.widget-rotate-handle').is_visible()
 assert not second.locator('.canvas-remove').is_visible()
 outer=first.bounding_box()
 assert outer
 for edge,rx,ry in [('n',.5,0),('ne',1,0),('e',1,.5),('se',1,1),('s',.5,1),('sw',0,1),('w',0,.5),('nw',0,0)]:
  b=first.locator('.edge-'+edge).bounding_box();assert b
  cx,cy=b['x']+b['width']/2,b['y']+b['height']/2
  assert abs(cx-(outer['x']+outer['width']*rx))<2,(edge,'x',cx,outer)
  assert abs(cy-(outer['y']+outer['height']*ry))<2,(edge,'y',cy,outer)
 exit_button=page.locator('.slide-scheme-exit')
 b=exit_button.bounding_box();assert b
 assert page.evaluate('([x,y])=>document.elementFromPoint(x,y)?.closest(".slide-scheme-exit")!==null',[b['x']+b['width']/2,b['y']+b['height']/2]),'Exit is covered'
 page.set_content('<style>'+CSS+'</style><section class="powerpoint-editor editor-ux-v2" style="width:min(900px,95vw);padding:8px">'+html.split('<section class="powerpoint-editor editor-ux-v2" style="width:min(900px,95vw);padding:8px">')[1])
 ruler=page.locator('.editor-ux-v2 .canvas-ruler-horizontal');assert ruler.is_visible()
 canvas=page.locator('.editor-ux-v2 .widget-canvas').bounding_box();r=ruler.bounding_box()
 assert canvas and r and abs(canvas['x']-r['x'])<3,(canvas,r)
 print(f'PASS RC112 Chromium {width}px: master resize handles, exit hit-target and page ruler')

with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,executable_path=os.environ.get('QUORIVIO_CHROMIUM_BIN') or '/usr/bin/chromium',args=['--no-sandbox'])
 page=browser.new_page()
 for w in (1440,390):checks(page,w)
 browser.close()
