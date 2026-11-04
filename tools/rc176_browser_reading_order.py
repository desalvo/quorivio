#!/usr/bin/env python3
"""RC176: real Chromium CSS + actual TypeScript policy, without npm dependencies.

An isolated DOM/CSS fixture cannot certify the logged-in React/PostgreSQL app.
The opt-in authenticated test in ci_browser_participant.py checks that journey.
"""
from __future__ import annotations

import html
import json
import os
from pathlib import Path
import subprocess

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'apps/web/src/style.css').read_text(encoding='utf8')


def policy_views() -> dict:
    js = '''import {participantVisibleWidgets,participantReadingWidgets} from './apps/web/src/live-slide-policy.ts';
const p=(x,y,width=40,height=20)=>({x,y,width,height,rotation:0});
const widgets=[
{id:'footer',kind:'footer',position:p(0,93,100,7)},
{id:'rating',kind:'rating',position:p(52,27,44,38)},
{id:'private-fill',kind:'shape',label:'Forma',position:p(3,58,40,24)},
{id:'chart',kind:'results-button',position:p(3,58,40,24)},
{id:'question',kind:'question',position:p(3,27,45,38)},
{id:'line',kind:'line',position:p(0,19,98,2)},
{id:'title',kind:'title',position:p(5,3,90,12)},
{id:'count',kind:'participant-count',position:p(85,70,12,15)}
];
console.log(JSON.stringify({reading:participantReadingWidgets(widgets),faithful:participantVisibleWidgets(widgets)}));'''
    result = subprocess.run(['node', '--experimental-strip-types', '--input-type=module', '-e', js],
                            cwd=ROOT, text=True, check=True, capture_output=True, timeout=15)
    return json.loads(result.stdout)


def document(widgets: list[dict], mode: str) -> str:
    assert mode in ('stage-reading', 'stage-fidelity')
    pieces = []
    for w in widgets:
        p = w['position']
        style = ('position:absolute;left:{x}%;top:{y}%;width:{width}%;height:{height}%;'
                 '--stage-x:{x}%;--stage-y:{y}%;--stage-width:{width}%;--stage-height:{height}%;'
                 '--stage-rotation:0deg').format(**p)
        label = {'title':'Titolo','question':'Domanda','rating':'Gradimento',
                 'footer':'Footer','shape':'Forma','line':'Linea'}.get(w['kind'], w['kind'])
        if w['kind'] == 'rating':
            body = '<div class="projection-sample-rating"><label class="rating-comment-field">Commento facoltativo<textarea class="rating-comment-input" aria-label="Commento facoltativo"></textarea></label><div class="rating-choice-buttons"><button type="button">0</button><button type="button">9</button></div></div>'
        elif w['kind'] == 'question':
            body = '<label>Risposta<input type="text" aria-label="Risposta"/></label>'
        else:
            body = html.escape(label)
        pieces.append(f'<div class="page-widget" data-widget-kind="{html.escape(w["kind"])}" '
                      f'data-widget-id="{html.escape(w["id"])}" style="{style}">'
                      f'<div class="widget-fit-frame"><div class="widget-fit-content">{body}</div></div></div>')
    return ('<!doctype html><html lang="it"><meta charset="utf-8"/>'
            '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
            '<style>' + CSS + '</style><main class="participant-live-view participant-slide-active">'
            '<section class="panel"><div class="audience-stage-scroll">'
            '<div id="stage" class="audience-widget-layout ' + mode + '" '
            'style="background-image:linear-gradient(red,blue);background-color:rgb(0,0,0)">'
            + ''.join(pieces) + '</div></div></section></main></html>')


def verify() -> None:
    views = policy_views()
    assert [w['id'] for w in views['reading']] == ['title','question','rating','footer']
    assert [w['id'] for w in views['faithful']] == ['footer','rating','question','line','title']
    executable = os.environ.get('QUORIVIO_CHROMIUM_PATH') or ('/usr/bin/chromium' if Path('/usr/bin/chromium').is_file() else None)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'],
                                    **({'executable_path':executable} if executable else {}))
        try:
            for width in (1280, 390, 320):
                page = browser.new_page(viewport={'width':width,'height':840})
                page.set_content(document(views['reading'],'stage-reading'))
                result = page.evaluate('''() => {
                  const stage=document.getElementById('stage'),s=getComputedStyle(stage);
                  const children=[...stage.querySelectorAll(':scope>.page-widget')];
                  const textarea=stage.querySelector('textarea');
                  return {ids:children.map(el=>el.dataset.widgetId),
                    backgroundImage:s.backgroundImage,backgroundColor:s.backgroundColor,
                    textareaHeight:textarea.getBoundingClientRect().height,
                    stageWidth:stage.getBoundingClientRect().width,
                    viewport:innerWidth};
                }''')
                assert result['ids'] == ['title','question','rating','footer'], (width,result)
                assert result['backgroundImage'] == 'none' and result['backgroundColor'] == 'rgb(255, 255, 255)',(width,result)
                assert result['textareaHeight'] >= 44,(width,result)
                assert result['stageWidth'] <= result['viewport']+2,(width,result)
                page.close()
                page = browser.new_page(viewport={'width':width,'height':840})
                page.set_content(document(views['faithful'],'stage-fidelity'))
                ratio = page.locator('#stage').evaluate('e=>e.getBoundingClientRect().width/e.getBoundingClientRect().height')
                assert abs(ratio-16/9)<.025, (width,ratio)
                assert page.locator('.page-widget[data-widget-kind="line"]').count()==1
                assert page.locator('.page-widget[data-widget-kind="results-button"]').count()==0
                page.close()
            print('PASS RC176: readable DOM order, clean background, >=44px inputs and unaffected 16:9 (1280/390/320)')
        finally:
            browser.close()


if __name__=='__main__':
    verify()
