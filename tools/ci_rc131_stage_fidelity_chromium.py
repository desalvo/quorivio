#!/usr/bin/env python3
"""Real CSS geometry/typography parity on three slide stages, desktop and mobile.

This fixture tests the unscaled 16:9 stage rather than screenshot pixel hashes or
private user sessions. It is a bounded supplement to the real app E2E tests.
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')

WIDGETS=[('title',6,5,88,13,24,True),('question',12,25,52,42,20,False),('footer',2,92,96,6,18,True)]

def pane(stage:str):
    if stage=='editor':
        shell='<div class="editor-ux-v2 editor-fixture"><div class="widget-canvas">__WIDGETS__</div></div>'
        container='widget-canvas-item'
    elif stage=='rehearsal':
        shell='<div class="rehearsal-pane"><section class="rehearsal-slide"><div class="rehearsal-widgets">__WIDGETS__</div></section></div>'
        container='rehearsal-widget'
    elif stage=='projection':
        shell='<div class="projection-page-content">__WIDGETS__</div>'
        container='projection-widget'
    else:
        shell='<div class="audience-widget-layout stage-fidelity">__WIDGETS__</div>'
        container='page-widget'
    children=[]
    for kind,x,y,w,h,font,bold in WIDGETS:
        text='Anteprima titolo' if kind=='title' else 'Footer sessione' if kind=='footer' else 'Domanda di esempio'
        children.append(f'''<div data-widget-kind="{kind}" data-stage-widget="{kind}" class="{container}" style="position:absolute;left:{x}%;top:{y}%;width:{w}%;height:{h}%;font-family:Georgia;font-size:{font/12.8:.5f}cqw;font-weight:{'700' if bold else '400'};--authored-widget-font-size:{font/12.8:.5f}cqw;color:rgb(35, 53, 85);--stage-x:{x}%;--stage-y:{y}%;--stage-width:{w}%;--stage-height:{h}%"><div class="widget-fit-frame"><div class="widget-fit-content"><span class="widget-rich-inline">{text}</span>{'<textarea class="widget-free-answer-field" style="height:15cqw"></textarea><button class="canvas-widget-submit-preview">Invia risposta</button>' if kind=='question' else ''}</div></div></div>''')
    return '<div data-surface="'+stage+'">'+shell.replace('__WIDGETS__',''.join(children))+'</div>'

HTML='''<!doctype html><html><head><meta charset="utf-8"><style>__CSS__</style><style>
body{margin:0;padding:12px;background:#fff;}
[data-surface]{width:var(--stage-size);height:auto;display:block;margin:0 0 15px;}
.editor-ux-v2.editor-fixture,.editor-ux-v2.editor-fixture:not(:fullscreen){position:static!important;inset:auto!important;width:100%!important;height:auto!important;max-width:none!important;display:block!important;padding:0!important;margin:0!important;}
.editor-fixture .widget-canvas,.projection-page-content,.audience-widget-layout.stage-fidelity,.rehearsal-pane>.rehearsal-slide{position:relative!important;display:block!important;width:100%!important;height:auto!important;aspect-ratio:16/9!important;min-height:0!important;max-height:none!important;overflow:hidden!important;box-sizing:border-box!important;padding:0!important;margin:0!important;border:0!important;box-shadow:none!important;}
</style></head><body>__PANES__</body></html>'''


def main():
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True,executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
        try:
            for viewport,stage_size in ((1440,960),(390,320)):
                page=browser.new_page(viewport={'width':viewport,'height':950})
                page.set_content(HTML.replace('__CSS__',CSS).replace('__PANES__',''.join(map(pane,('editor','rehearsal','projection','audience')))))
                page.evaluate('(size) => document.body.style.setProperty("--stage-size", size+"px")',stage_size)
                metrics=page.evaluate('''() => {
                  const out={};for(const surf of document.querySelectorAll('[data-surface]')){
                    const stage=surf.querySelector('.widget-canvas,.rehearsal-widgets,.projection-page-content,.audience-widget-layout');
                    const box=stage.getBoundingClientRect();const result={};
                    for(const elem of surf.querySelectorAll('[data-stage-widget]')){
                      const r=elem.getBoundingClientRect(),s=getComputedStyle(elem);
                      const span=elem.querySelector('.widget-rich-inline');const text=getComputedStyle(span);
                      result[elem.dataset.stageWidget]={x:(r.x-box.x)/box.width,y:(r.y-box.y)/box.height,
                        w:r.width/box.width,h:r.height/box.height,font:(parseFloat(s.fontSize)*1280/box.width).toFixed(2),family:s.fontFamily,
                        weight:text.fontWeight,color:text.color,overflow:s.overflow};
                    }
                    out[surf.dataset.surface]=result;
                  }return out;
                }''')
                baseline=metrics['editor'];
                for stage in ('rehearsal','projection','audience'):
                    for kind,values in baseline.items():
                        actual=metrics[stage][kind]
                        for key in ('x','y','w','h'):
                            assert abs(values[key]-actual[key])<.003,(viewport,stage,kind,key,values,actual)
                        for key in (('font','family','weight','color') if kind in ('title','footer') else ('font','family','color')):
                            assert actual[key]==values[key],(viewport,stage,kind,key,values,actual)
                print(f'PASS RC131 real Chromium stage geometry and authored title/footer typography: {viewport}px')
                page.close()
        finally:browser.close()

if __name__=='__main__':main()
