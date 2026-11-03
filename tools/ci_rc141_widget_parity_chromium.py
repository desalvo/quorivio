#!/usr/bin/env python3
"""Real Chromium CSS parity contract for RC141–RC152 on all widget surfaces.

RC143 deliberately allows long result labels to wrap while keeping the final
word and bracketed count together. The old RC141 assertion that the entire
pair must be nowrap was obsolete and hid this accessibility requirement.
Uses only synthetic values and no user, network or session data.
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
      <span class="linked-result-label">Servizi di ricerca avanzata per la collaborazione scientifica tra istituti di ricerca e infrastrutture distribuite con strumenti interoperabili e accessibili a tutte le comunità </span><span class="linked-result-final">europea<output>[28]</output></span>
      </span></div></div></section>'''
    box = f'<div data-stage="{surface}" class="{cls}" data-widget-kind="reactions" data-show-title="false" style="position:relative;width:320px;height:180px;font-size:16px;font-family:Arial;--authored-widget-font-size:16px;padding:9px">{body}</div>'
    if surface == 'editor': return f'<div class="editor-ux-v2">{box}</div>'
    if surface == 'presenter': return f'<div class="projection-page-content">{box}</div>'
    if surface == 'rehearsal': return f'<div class="rehearsal-pane"><div class="rehearsal-slide"><div class="rehearsal-widgets">{box}</div></div></div>'
    return f'<div class="audience-widget-layout stage-fidelity">{box}</div>'


def run(css_text: str | None = None) -> None:
    stylesheet = CSS if css_text is None else css_text
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
        try:
            for viewport in (1440, 390):
                page = browser.new_page(viewport={'width':viewport,'height':900})
                # The 320px fixture must not be squeezed to 98px by the mobile editor shell.
                # The participant stage is rendered at authored widget font size.
                page.set_content('<html><head><style>'+stylesheet+'</style><style>body{margin:0;padding:8px} .test-stage{margin:8px 0;height:195px;width:340px;position:relative;container-type:inline-size} .test-stage .widget-canvas-item{position:relative!important;width:320px!important;min-width:320px!important;height:180px!important} .test-stage .audience-widget-layout.stage-fidelity{width:100%!important;min-width:0!important} .test-stage .rehearsal-pane,.test-stage .rehearsal-slide,.test-stage .rehearsal-widgets{position:relative!important;width:100%!important;height:100%!important;min-height:0!important;padding:0!important;margin:0!important;max-width:none!important} .test-stage .rehearsal-widget{position:relative!important;left:auto!important;top:auto!important;width:320px!important;height:180px!important;font-size:16px!important;--stage-x:0%;--stage-y:0%;--stage-width:100%;--stage-height:100%} .test-stage .rehearsal-pane{min-width:0!important;max-width:none!important}</style></head><body>'+''.join('<div class="test-stage">'+markup(stage)+'</div>' for stage in ('editor','presenter','rehearsal','participant'))+'</body></html>')
                values = page.evaluate('''() => Object.fromEntries([...document.querySelectorAll('[data-stage]')].map(el=>{
                   const reaction=el.querySelector('.reaction-choice-buttons button');
                   const checkbox=el.querySelector('.widget-answer-option input');
                   const title=el.querySelector('.projection-sample-reactions strong');
                   const r=reaction.getBoundingClientRect();const c=checkbox.getBoundingClientRect();
                   const pair=el.querySelector('.linked-result-pair');
                   const label=pair.querySelector('.linked-result-label');
                   const final=pair.querySelector('.linked-result-final');
                   const count=final.querySelector('output');
                   const finalWord=document.createRange();finalWord.selectNodeContents(final.firstChild);
                   const labelFragments=label.getClientRects();
                   return [el.dataset.stage,{titleVisible:getComputedStyle(title).display!=='none',
                     pairWraps:getComputedStyle(pair).whiteSpace!=='nowrap',
                     labelWraps:labelFragments.length>1,
                     tailNoWrap:getComputedStyle(final).whiteSpace==='nowrap',
                     tailInline:Math.abs(finalWord.getBoundingClientRect().top-count.getBoundingClientRect().top)<1.5,
                     pairFits:pair.scrollWidth<=pair.clientWidth+1,
                     width:r.width,height:r.height,font:getComputedStyle(reaction).fontSize,
                     checkboxWidth:c.width,checkboxHeight:c.height,
                     checkboxLeft:c.left,checkboxTextLeft:el.querySelector('.widget-answer-option span').getBoundingClientRect().left}]
                }))''')
                base = values['presenter']
                assert all(item['titleVisible'] is False for item in values.values()), values
                # RC143+: the full label wraps; only the final word/count is atomic.
                # Keep result rows inside the authored stage at both viewport sizes.
                assert all(item['pairWraps'] and item['labelWraps'] and item['tailInline'] and item['tailNoWrap'] and item['pairFits'] for item in values.values()), values
                for stage, value in values.items():
                    for key in ('width','height','checkboxWidth','checkboxHeight'):
                        assert abs(value[key]-base[key]) <= 1.5, (viewport,stage,key,value,base)
                    assert value['font']==base['font'],(viewport,stage,'font',value,base)
                    assert value['checkboxTextLeft']>value['checkboxLeft'],(viewport,stage,value)
                print(f'PASS RC141/RC152 Chromium reactions, checkbox and wrapped result-count parity across 4 surfaces at {viewport}px')
                page.close()
        finally:
            browser.close()


if __name__ == '__main__':run()
