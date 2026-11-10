#!/usr/bin/env python3
"""Chrome geometry acceptance for R: frame colour may change, text must not move.

Uses the *shipped* CSS and markup matching both linked source and results rows.
This is a browser-level regression, not proof of full app/DB end-to-end state.
"""
from __future__ import annotations
from pathlib import Path
import asyncio
import os
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
HTML='''<section class="linked-results" style="width:460px;height:760px;font-family:Arial;font-size:24px;">
 <section class="linked-source-question"><div class="linked-source-answers">
  <div class="widget-answer-option linked-source-answer" id="answer-a"><span>•</span> <strong id="text-a">Una risposta con testo molto lungo e grande formato che richiede almeno tre righe senza cambiare posizione</strong></div>
  <div class="widget-answer-option linked-source-answer" id="answer-b"><span>•</span> <strong id="text-b">Un'altra risposta corretta con un font personalizzato molto grande</strong></div>
 </div></section>
 <div class="linked-results-items"><div class="linked-results-row" id="row-a"><span class="linked-result-pair"><span class="linked-result-label" id="row-text">Risultato verificato per la prima opzione testuale</span><span class="linked-result-final">conclusione <output>27</output></span></span></div></div>
</section>'''

async def main():
 async with async_playwright() as playwright:
  browser=await playwright.chromium.launch(executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
  page=await browser.new_page(viewport={'width':900,'height':850})
  await page.set_content('<style>'+CSS+'</style>'+HTML)
  measure='''() => Object.fromEntries(['answer-a','answer-b','text-a','text-b','row-a','row-text'].map(id=>{let r=document.getElementById(id).getBoundingClientRect();return [id,[r.x,r.y,r.width,r.height].map(v=>Math.round(v*100)/100)]}))'''
  baseline=await page.evaluate(measure)
  await page.evaluate('''() => {
    document.getElementById('answer-a').setAttribute('data-answer-verdict','correct');
    document.getElementById('answer-b').setAttribute('data-answer-verdict','incorrect');
    document.getElementById('row-a').setAttribute('data-answer-verdict','correct');
    for (let id of ['answer-a','answer-b']){
      let icon=document.createElement('span');icon.className='answer-verdict-icon';icon.textContent='✓';document.getElementById(id).appendChild(icon);
    }
    let icon=document.createElement('small');icon.className='answer-verdict-icon';icon.textContent='✓';document.querySelector('#row-a .linked-result-final').appendChild(icon);
  }''')
  after=await page.evaluate(measure)
  mismatches={k:(baseline[k],after[k]) for k in baseline if any(abs(a-b)>.5 for a,b in zip(baseline[k],after[k]))}
  print('R layout before:',baseline)
  print('R layout after:',after)
  await browser.close()
  if mismatches:raise AssertionError('R changed layout: '+str(mismatches))
  print('PASS: R changed only the visual frame, not geometry of options, rows or text')

if __name__=='__main__':asyncio.run(main())
