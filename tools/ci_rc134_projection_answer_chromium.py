#!/usr/bin/env python3
"""Bounded real Chromium CSS acceptance: text and choice projection controls.

Only synthetic text; no session, account, answer or API network access.
The source-level RC134 contract independently guards wiring to the real app.
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')


def screen(kind: str, stage: str) -> str:
    root = 'projection-widget' if stage == 'projection' else 'rehearsal-widget'
    title = 'Domanda aperta' if kind == 'text' else 'Seleziona una risposta'
    controls = ('<textarea class="widget-free-answer-field" disabled readonly tabindex="-1" '
                'style="width:80%;height:7.5cqw;font-size:1.25cqw" placeholder="Scrivi una risposta…"></textarea>'
                if kind == 'text' else
                '<div role="group"><label class="widget-answer-option" style="font-size:1.25cqw"><input type="radio" disabled tabindex="-1">Prima opzione con testo lungo</label></div>')
    outer_start = '<div class="rehearsal-pane"><section class="rehearsal-slide"><div class="rehearsal-widgets">' if stage=='rehearsal' else '<div class="projection-page-content">'
    outer_end = '</div></section></div>' if stage=='rehearsal' else '</div>'
    return outer_start+f'''<div data-surface="{stage}-{kind}" class="{root}" data-widget-kind="question" style="position:relative;width:100%;height:100%;font-size:1.5625cqw;--authored-widget-font-size:1.5625cqw;font-family:Georgia;--stage-x:0%;--stage-y:0%;--stage-width:100%;--stage-height:100%;">
        <div class="widget-fit-frame"><div class="widget-fit-content"><section class="projection-interactive-widget" data-readonly-preview="true">
          <strong>{title}</strong>{controls}<button type="button" disabled tabindex="-1" class="outline small projection-readonly-submit" style="font-size:1.25cqw;min-height:2.8cqw">Invia risposta</button>
        </section></div></div></div>'''+outer_end


def main():
    html = '''<!doctype html><html><head><meta charset="utf-8"><style>'''+CSS+'''</style><style>
    body{margin:0;padding:12px;background:#fff}
    .test-stage{width:var(--stage-width);height:calc(var(--stage-width)*.5625);container-type:inline-size;margin-bottom:10px}
    .test-stage .rehearsal-pane,.test-stage .rehearsal-slide,.test-stage .rehearsal-widgets,.test-stage .projection-page-content{position:relative!important;display:block!important;width:100%!important;height:100%!important;min-height:0!important;max-height:none!important;margin:0!important;padding:0!important;overflow:hidden!important;box-sizing:border-box!important;container-type:inline-size}
    .test-stage .rehearsal-pane{min-width:0!important;max-width:none!important;flex:none!important;}
    [data-surface]{box-sizing:border-box}
    </style></head><body><div id="host"></div></body></html>'''
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True,
            executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH', '/usr/bin/chromium'), args=['--no-sandbox'])
        try:
            for viewport, width in ((1440, 960), (390, 320)):
                page = browser.new_page(viewport={'width': viewport, 'height': 900})
                page.set_content(html)
                page.evaluate('''(width)=>{
                    document.body.style.setProperty('--stage-width',width+'px');
                }''', width)
                htmls = ''.join(f'<div class="test-stage">{screen(kind,stage)}</div>'
                    for kind in ('text','choice') for stage in ('projection','rehearsal'))
                page.locator('#host').evaluate('(host,markup)=>{host.innerHTML=markup}', htmls)
                metrics = page.evaluate('''() => {
                    const data = {};
                    for(const surface of document.querySelectorAll('[data-surface]')) {
                        const submit=surface.querySelector('.projection-readonly-submit');
                        const strong=surface.querySelector('strong');
                        const input=surface.querySelector('textarea,input');
                        const box=surface.getBoundingClientRect();
                        const sb=submit.getBoundingClientRect();
                        const ib=input.getBoundingClientRect();
                        data[surface.dataset.surface]={
                          buttonDisabled:submit.disabled,inputDisabled:input.disabled,
                          buttonVisible:sb.width>10&&sb.height>10, inputVisible:ib.width>2&&ib.height>2,
                          buttonY:(sb.top-box.top)/box.width,inputY:(ib.top-box.top)/box.width,
                          font:getComputedStyle(strong).fontFamily, titleSize:getComputedStyle(strong).fontSize,
                          inputWidth:ib.width/box.width,inputHeight:ib.height/box.width,
                          buttonText:submit.textContent.trim()
                        };
                    }return data;
                }''')
                for kind in ('text', 'choice'):
                    presenter=metrics['projection-'+kind]
                    rehearsal=metrics['rehearsal-'+kind]
                    for key in ('buttonDisabled','inputDisabled','buttonVisible','inputVisible'):
                        assert presenter[key] is True and rehearsal[key] is True, (viewport,kind,key,presenter,rehearsal)
                    for key in ('buttonY','inputY','inputWidth'):
                        assert abs(presenter[key]-rehearsal[key])<.006, (viewport,kind,key,presenter,rehearsal)
                    for key in ('font','buttonText'):
                        assert presenter[key]==rehearsal[key],(viewport,kind,key,presenter,rehearsal)
                    assert abs(float(presenter['titleSize'].rstrip('px'))-float(rehearsal['titleSize'].rstrip('px')))<.2,(viewport,kind,presenter,rehearsal)
                    assert presenter['buttonText']=='Invia risposta'
                print(f'PASS RC134 real Chromium projection/preview readonly input+submit parity: {viewport}px')
                page.close()
        finally: browser.close()


if __name__ == '__main__': main()
