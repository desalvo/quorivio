#!/usr/bin/env python3
"""Real Chromium CSS contract for RC141 on all 16:9 widget surfaces.

Uses synthetic values only. No session, external provider or network state.
The source tests independently verify these CSS primitives are wired into React.
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')


def markup(surface: str) -> str:
    widget_classes = {'editor': 'widget-canvas-item', 'presenter': 'projection-widget',
                      'rehearsal': 'rehearsal-widget', 'participant': 'page-widget'}
    cls = widget_classes[surface]
    body = '''<section class="projection-sample-reactions">
      <strong>Reazioni</strong><div class="reaction-choice-buttons" style="--reaction-size:32px">
      <button disabled aria-label="Reazione 👍">👍</button><button disabled aria-label="Reazione ❤️">❤️</button>
      <button disabled aria-label="Reazione 😂">😂</button></div></section>
      <label class="widget-answer-option"><input type="checkbox" disabled><span>Reti e infrastrutture</span></label>
      <section class="linked-results result-view-cloud" data-fit-mode="scale">
      <div class="linked-results-items"><div class="linked-results-row"><span class="linked-result-pair">
      <span class="linked-result-label">Servizi alla ricerca</span><output>[28]</output>
      </span></div></div></section>'''
    box = f'<div data-stage="{surface}" class="{cls}" data-widget-kind="reactions" data-show-title="false" style="position:relative;width:320px;height:180px;font-size:16px;font-family:Arial;padding:9px">{body}</div>'
    if surface == 'editor': return f'<div class="editor-ux-v2">{box}</div>'
    if surface == 'presenter': return f'<div class="projection-page-content">{box}</div>'
    if surface == 'rehearsal': return f'<div class="rehearsal-pane"><div class="rehearsal-slide"><div class="rehearsal-widgets">{box}</div></div></div>'
    return f'<div class="audience-widget-layout stage-fidelity">{box}</div>'


def run() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
        try:
            for viewport in (1440, 390):
                page = browser.new_page(viewport={'width':viewport,'height':900})
                page.set_content('<html><head><style>'+CSS+'</style><style>body{margin:0;padding:8px} .test-stage{margin:8px 0;height:195px;width:340px;position:relative;container-type:inline-size} .test-stage .rehearsal-pane,.test-stage .rehearsal-slide,.test-stage .rehearsal-widgets{position:relative!important;width:100%!important;height:100%!important;min-height:0!important;padding:0!important;margin:0!important;max-width:none!important} .test-stage .rehearsal-widget{position:relative!important;left:auto!important;top:auto!important;width:320px!important;height:180px!important;font-size:16px!important;--stage-x:0%;--stage-y:0%;--stage-width:100%;--stage-height:100%} .test-stage .rehearsal-pane{min-width:0!important;max-width:none!important}</style></head><body>'+''.join('<div class="test-stage">'+markup(stage)+'</div>' for stage in ('editor','presenter','rehearsal','participant'))+'</body></html>')
                values = page.evaluate('''() => Object.fromEntries([...document.querySelectorAll('[data-stage]')].map(el=>{
                   const reaction=el.querySelector('.reaction-choice-buttons button');
                   const checkbox=el.querySelector('.widget-answer-option input');
                   const title=el.querySelector('.projection-sample-reactions strong');
                   const r=reaction.getBoundingClientRect();const c=checkbox.getBoundingClientRect();
                   const pair=el.querySelector('.linked-result-pair');
                   const label=pair.querySelector('.linked-result-label').getBoundingClientRect();
                   const count=pair.querySelector('output').getBoundingClientRect();
                   return [el.dataset.stage,{titleVisible:getComputedStyle(title).display!=='none',
                     pairInline:Math.abs(label.top-count.top)<1.5,
                     pairNoWrap:getComputedStyle(pair).whiteSpace==='nowrap',
                     width:r.width,height:r.height,font:getComputedStyle(reaction).fontSize,
                     checkboxWidth:c.width,checkboxHeight:c.height,
                     checkboxLeft:c.left,checkboxTextLeft:el.querySelector('.widget-answer-option span').getBoundingClientRect().left}]
                }))''')
                base = values['presenter']
                assert all(item['titleVisible'] is False for item in values.values()), values
                assert all(item['pairInline'] and item['pairNoWrap'] for item in values.values()), values
                for stage, value in values.items():
                    for key in ('width','height','checkboxWidth','checkboxHeight'):
                        assert abs(value[key]-base[key]) <= 1.5, (viewport,stage,key,value,base)
                    assert value['font']==base['font'],(viewport,stage,'font',value,base)
                    assert value['checkboxTextLeft']>value['checkboxLeft'],(viewport,stage,value)
                print(f'PASS RC141 Chromium reactivity/checkbox visual parity across 4 surfaces at {viewport}px')
                page.close()
        finally:
            browser.close()


if __name__ == '__main__':run()
