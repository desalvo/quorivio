#!/usr/bin/env python3
"""RC306 visual CSS regression: responsive multiline result bars in native Chromium.

Uses the actual production stylesheet on a minimal representative rendered DOM.
This checks CSS geometry, not backend data or authenticated routing; the full
Chromium editor and PostgreSQL tests in the same workflow cover those paths.
"""
from __future__ import annotations
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=ROOT/'apps/web/src/style.css'
LONG='Si deve essere informati tempestivamente e avere tutte le informazioni per risolvere i problemi rilevati nel più breve tempo possibile '
HTML='''<!doctype html><html lang="it"><head><meta charset="UTF-8"></head>
<body style="margin:0;background:#fff;font:20px Arial,sans-serif">
<div class="editor-ux-v2" style="padding:30px">
 <div class="widget-canvas-item" data-widget-kind="results-button" style="position:relative;width:WIDpx;height:360px;font:20px Arial,sans-serif">
  <div class="widget-fit-frame" data-fit-mode="scroll">
   <div class="widget-fit-content">
    <section class="linked-results result-view-bars" data-result-source-kind="question">
     <strong>Il controllo e il monitoring dei servizi informatici</strong>
     <small>58 risposte · simulazione</small>
     <div class="linked-results-items">
      <div class="linked-results-row"><span class="linked-result-pair">
       <span class="linked-result-label">LABEL</span><span class="linked-result-final">possibile<output>12</output></span>
      </span><div class="linked-results-track"><div style="width:100%"></div></div></div>
      <div class="linked-results-row"><span class="linked-result-pair">
       <span class="linked-result-label">Si devono offrire servizi efficienti senza la necessità di intervento</span>
       <span class="linked-result-final">manuale<output>23</output></span>
      </span><div class="linked-results-track"><div style="width:50%"></div></div></div>
     </div>
    </section>
   </div>
  </div>
 </div>
</div></body></html>'''

def main()->None:
 with sync_playwright() as pw:
  browser_options={"headless":True}
  path=os.environ.get('QUORIVIO_CHROMIUM_PATH','')
  if path:browser_options["executable_path"]=path
  browser=pw.chromium.launch(**browser_options)
  try:
   metrics=[]
   for width in (420,740):
    page=browser.new_page(viewport={"width":max(900,width+90),"height":820})
    page.set_content(HTML.replace('WID',str(width)).replace('LABEL',LONG))
    page.add_style_tag(content=CSS.read_text(encoding='utf8'))
    result=page.evaluate("""() => {
      const row=document.querySelector('.linked-results-row');
      const label=row.querySelector('.linked-result-label');
      const pair=row.querySelector('.linked-result-pair');
      const track=row.querySelector('.linked-results-track');
      const frame=document.querySelector('.widget-fit-frame');
      const text=window.getComputedStyle(label);
      const rectangles=[...label.getClientRects()];
      const rect=(el)=>el.getBoundingClientRect();
      return {
        lines:rectangles.length,
        textFont:parseFloat(text.fontSize),
        whitespace:text.whiteSpace,
        rowWidth:rect(row).width,
        pairWidth:rect(pair).width,
        trackWidth:rect(track).width,
        parentWidth:rect(frame).width,
        rowScrollWidth:row.scrollWidth,
        rowClientWidth:row.clientWidth,
        rootScrollWidth:frame.scrollWidth,
        fitTransform:window.getComputedStyle(frame.querySelector('.widget-fit-content')).transform
      };
    }""")
    assert result['lines']>=2, f"{width}px: long label stayed on one line: {result}"
    assert result['whitespace']=='normal', f"{width}px: CSS nowrap override: {result}"
    assert result['textFont']>=14, f"{width}px: unreadable font: {result}"
    assert result['rowScrollWidth']<=result['rowClientWidth']+2, f"{width}px: horizontal overflow: {result}"
    assert result['pairWidth']<=result['parentWidth']+2, f"{width}px: max-content pair: {result}"
    assert result['trackWidth']>=result['parentWidth']*.72, f"{width}px: track failed to stretch: {result}"
    assert result['fitTransform']=='none',f"{width}px: content was scaled: {result}"
    metrics.append((width,result['lines'],result['textFont'],round(result['trackWidth'])))
    page.close()
   print('RC306 native Chromium multiline result bars passed:',metrics,flush=True)
  finally:browser.close()

if __name__=='__main__':
 main()
