#!/usr/bin/env python3
"""RC159 real Chromium CSS acceptance: lifecycle action contrast and white rating input.

A minimal DOM fixture uses the production stylesheet. The Node contracts check
that React actually mounts these classes/components; real full-app Chromium
acceptance remains a separate CI stage.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
HTML='''<!doctype html><html lang="it"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><main class="dashboard"><div class="workspace"><div class="downloads"><button class="outline session-action-terminate">Termina</button><button class="outline session-action-pause">Pausa</button><button class="outline session-action-reset">Riporta a non avviata</button></div><section class="projection-sample-rating"><label class="rating-comment-field">Commento facoltativo<textarea class="rating-comment-input" rows="2" readonly placeholder="Scrivi un commento (facoltativo)"></textarea></label><label class="rating-comment-field">Commento facoltativo<textarea class="rating-comment-input" rows="2" placeholder="Scrivi un commento (facoltativo)"></textarea></label></section></div></main></body></html>'''
EXPECTED={'session-action-terminate':'rgb(173, 41, 57)','session-action-pause':'rgb(185, 244, 206)','session-action-reset':'rgb(181, 233, 255)'}

def main():
 executable=os.environ.get('QUORIVIO_CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome')
 if not executable:raise RuntimeError('Chromium required: no test silently skipped')
 with sync_playwright() as playwright:
  browser=playwright.chromium.launch(headless=True,executable_path=executable,args=['--no-sandbox'])
  try:
   for width in (1440,390):
    page=browser.new_page(viewport={'width':width,'height':844})
    page.set_content(HTML)
    page.add_style_tag(content=CSS)
    # Disable inherited button transitions so computed colors are deterministic.
    page.add_style_tag(content="button{transition:none!important}")
    result=page.evaluate('''() => ({
      colors: Object.fromEntries(['terminate','pause','reset'].map(name=>['session-action-'+name,getComputedStyle(document.querySelector('.session-action-'+name)).backgroundColor])),
      comments: [...document.querySelectorAll('.rating-comment-input')].map(e=>({color:getComputedStyle(e).color,background:getComputedStyle(e).backgroundColor,disabled:e.disabled,readOnly:e.readOnly,visible:e.getBoundingClientRect().width>0})),
      bodyWidth: document.body.scrollWidth,
    })''')
    for key,value in EXPECTED.items():
     assert result['colors'][key]==value,(width,key,result)
    for comment in result['comments']:
     assert comment['background']=='rgb(255, 255, 255)' and comment['color']=='rgb(20, 43, 68)',(width,comment)
     assert not comment['disabled'] and comment['visible'],(width,comment)
    assert result['comments'][0]['readOnly'] and not result['comments'][1]['readOnly']
    print(f'PASS RC159 Chromium {width}px: session lifecycle colors and white rating comments')
    page.close()
  finally:browser.close()

if __name__=='__main__':main()
