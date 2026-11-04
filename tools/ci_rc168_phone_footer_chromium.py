#!/usr/bin/env python3
"""CSS-level Chromium acceptance for public desktop 16:9 and phone footer.

Supplement only: tools/ci_browser_participant.py verifies the saved, logged-in
session and actual layout against PostgreSQL, without leaking join tokens.
"""
from pathlib import Path
import os
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')


def widget(kind, y, height):
    return (f'<div class="page-widget" data-widget-kind="{kind}" '
            f'style="--stage-x:4%;--stage-y:{100*y/928:.4f}%;--stage-width:92%;'
            f'--stage-height:{100*height/928:.4f}%;font-family:Arial;'
            f'--mobile-widget-font-size:16px"><div class="widget-fit-frame">'
            f'<div class="widget-fit-content">{kind}</div></div></div>')


HTML = '''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body><main class="participant-live-view" style="width:100%;max-width:none;margin:0;padding:0">
<div class="audience-stage-scroll"><div id="slide" class="audience-widget-layout stage-fidelity"><div class="page-widget" data-widget-kind="title" style="--stage-x:8%;--stage-y:3%;--stage-width:84%;--stage-height:12%;font-family:Arial">Title</div></div></div>
<div class="audience-stage-scroll"><div id="phone" class="audience-widget-layout stage-phone" style="height:928px">__WIDGETS__</div></div>
</main></body></html>'''


def run():
    chromium = os.environ.get('QUORIVIO_CHROMIUM_PATH') or shutil.which('chromium')
    if not chromium:
        raise RuntimeError('Chromium is required for the public stage acceptance')
    phone = ''.join((widget('title',24,90),widget('question',130,260),
                     widget('line',406,80),widget('topic-question',502,210),
                     widget('shape',728,80),widget('footer',840,64)))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=chromium,
                                             args=['--no-sandbox'])
        try:
            for viewport in (390,1440):
                page = browser.new_page(viewport={'width':viewport,'height':900})
                page.set_content(HTML.replace('__WIDGETS__', phone))
                page.add_style_tag(content=CSS)
                stats = page.evaluate('''() => {
                  const slide=document.querySelector('#slide').getBoundingClientRect();
                  const stage=document.querySelector('#phone').getBoundingClientRect();
                  const widgets=[...document.querySelectorAll('#phone>.page-widget')];
                  const footer=widgets.find(x=>x.dataset.widgetKind==='footer').getBoundingClientRect();
                  const lastContent=widgets.find(x=>x.dataset.widgetKind==='shape').getBoundingClientRect();
                  return {ratio:slide.width/slide.height,height:stage.height,
                    bottomGap:stage.bottom-footer.bottom,footerAfterContent:footer.top>lastContent.bottom,
                    phoneWidth:stage.width,bodyOverflow:document.documentElement.scrollWidth>innerWidth+2,
                    kinds:widgets.map(x=>x.dataset.widgetKind)};
                }''')
                assert abs(stats['ratio'] - 16/9)<.03, (viewport, stats)
                assert abs(stats['height']-928)<1.5, (viewport, stats)
                assert 22<=stats['bottomGap']<=26, (viewport, stats)
                assert stats['footerAfterContent'], (viewport, stats)
                assert stats['phoneWidth']<=390.5, (viewport, stats)
                assert not stats['bodyOverflow'], (viewport, stats)
                assert not {'results-button','participant-count'}.intersection(stats['kinds']), stats
                print(f'PASS Chromium RC168 {viewport}px: 16:9, filtered phone 928px, footer bottom 24px')
                page.close()
        finally:
            browser.close()


if __name__ == '__main__':
    run()
