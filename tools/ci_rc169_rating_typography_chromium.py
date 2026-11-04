#!/usr/bin/env python3
"""Real Chromium parity: same 390px authored title and rating widget in both surfaces.

This is a deterministic CSS/DOM acceptance, separate from the authenticated
PostgreSQL check. Never embeds join URLs, cookies, usernames or live answers.
"""
from pathlib import Path
import os
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')


def widget(kind, content, surface):
    name = 'rehearsal-widget rehearsal-' + kind if surface == 'preview' else 'page-widget'
    y = 6 if kind == 'title' else 24
    h = 12 if kind == 'title' else 40
    size = 38 if kind == 'title' else 24
    return (f'<div class="{name}" data-widget-kind="{kind}" '
            f'data-show-title="true" style="--stage-x:4%;--stage-y:{y}%;'
            f'--stage-width:92%;--stage-height:{h}%;--mobile-widget-font-size:{size}px;'
            f'--authored-widget-font-size:{size / 1280 * 100:.5f}cqw;'
            f'font-family:Arial;font-size:{size}px">'
            f'<div class="widget-fit-frame"><div class="widget-fit-content">{content}</div></div></div>')


def rating():
    buttons = ''.join(f'<button type="button" aria-label="Vota {n} su 9">{n}</button>' for n in range(10))
    return ('<div class="projection-sample-rating" data-rating-parity="true">'
            '<strong>Gradimento</strong><p>Testo descrittivo</p>'
            '<label class="rating-comment-field">Commento facoltativo'
            '<textarea class="rating-comment-input" rows="2" placeholder="Commento"></textarea></label>'
            '<p class="rating-range-hint muted tiny">0 = gradimento minimo · 9 = gradimento massimo</p>'
            f'<div class="rating-choice-buttons" role="group" style="--rating-font-size:1.5em">{buttons}</div>'
            '</div>')


def run():
    chromium = os.environ.get('QUORIVIO_CHROMIUM_PATH') or shutil.which('chromium')
    if not chromium:
        raise RuntimeError('Chromium is mandatory for RC169 visual acceptance')
    page_widgets = widget('title','<h2 class="projection-slide-title">Titolo schema</h2>','public') + widget('rating',rating(),'public')
    rehearsal_widgets = widget('title','<h2 class="projection-slide-title">Titolo schema</h2>','preview') + widget('rating',rating(),'preview')
    html = ('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
            '<main class="participant-live-view" style="width:390px"><div class="audience-stage-scroll">'
            '<div id="public" class="audience-widget-layout stage-phone" style="height:930px">'
            +page_widgets+'</div></div></main>'
            '<div class="rehearsal-phone-stage" style="position:relative;transform:none;width:390px;height:930px">'
            '<section class="rehearsal-slide"><div class="rehearsal-widgets">'
            +rehearsal_widgets+'</div></section></div></body></html>')
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=chromium,args=['--no-sandbox'])
        try:
            for width in (390, 1440):
                page = browser.new_page(viewport={'width':width,'height':960})
                page.set_content(html)
                page.add_style_tag(content=CSS)
                stats = page.evaluate('''() => {
                  const read=(root)=>{
                    const title=document.querySelector(root+' [data-widget-kind="title"]');
                    const rating=document.querySelector(root+' [data-widget-kind="rating"]');
                    const comment=rating.querySelector('.rating-comment-input');
                    const titleRect=title.getBoundingClientRect(),r=rating.getBoundingClientRect();
                    const color=getComputedStyle(comment);
                    return {stageWidth:document.querySelector(root).getBoundingClientRect().width,titleSize:getComputedStyle(title).fontSize,
                      titleFace:getComputedStyle(title).fontFamily,
                      titleX:titleRect.left,titleY:titleRect.top,
                      ratingFont:getComputedStyle(rating).fontSize,
                      ratingX:r.left,ratingY:r.top,
                      commentColor:color.color,commentBackground:color.backgroundColor,
                      commentWidth:comment.getBoundingClientRect().width,
                      choiceCount:rating.querySelectorAll('.rating-choice-buttons>button').length,
                      rangeText:rating.querySelectorAll('.rating-range-hint').length,
                      descriptionCount:rating.querySelectorAll('p:not(.rating-range-hint)').length};
                  };return {public:read('#public'),preview:read('.rehearsal-phone-stage')};
                }''')
                pub,pre = stats['public'],stats['preview']
                for field in ('titleSize','titleFace','ratingFont','commentColor',
                              'commentBackground','commentWidth','choiceCount','rangeText','descriptionCount'):
                    if field=='commentWidth':
                        assert abs(pub[field]/pub['stageWidth']-pre[field]/pre['stageWidth'])<.015,(width,field,stats)
                    else:assert pub[field]==pre[field],(width,field,stats)
                assert pub['titleSize']=='38px',(width,stats)
                assert pub['ratingFont']=='24px',(width,stats)
                assert pub['commentBackground']=='rgb(255, 255, 255)',(width,stats)
                assert pub['choiceCount']==10 and pub['rangeText']==1 and pub['descriptionCount']==1,(width,stats)
                # Compare relative positions inside each stage, not browser viewport.
                assert abs((pub['ratingY']-pub['titleY'])-(pre['ratingY']-pre['titleY']))<2,(width,stats)
                print(f'PASS RC169 Chromium {width}px: phone title 38px, rating 24px, 10 choices, white comment, preview/live parity')
                page.close()
        finally:
            browser.close()

if __name__=='__main__':
    run()
