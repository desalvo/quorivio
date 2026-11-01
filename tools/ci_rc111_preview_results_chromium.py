#!/usr/bin/env python3
"""RC111 actual editor CSS tested by native Chromium on desktop and mobile.

This is a CSS stack and text geometry preflight, NOT a substitute for the
compiled-React rehearsal acceptance run which remains mandatory in full CI.
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
LABEL='Un lungo quesito che contiene parole di molte lunghezze, spiegazioni articolate, osservazioni su informatica e considerazioni che devono occupare diverse righe.'
ANSWER='Una risposta testuale particolarmente lunga che non deve essere troncata anche con il grafico ristretto e deve rimanere completamente leggibile in più righe.'
HTML=f'''<!doctype html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>{CSS}</style></head><body>
<section class="editor-ux-v2 powerpoint-editor"><header class="editor-mock-header"><button class="editor-preview-open">▶ Presentatore</button></header></section>
<div class="editor-floating-panel widget-selection-palette" style="left:16px;top:120px;height:130px;width:280px">Proprietà</div>
<div role="dialog" aria-modal="true" class="rehearsal-backdrop"><div class="rehearsal-shell" style="width:65vw;height:65vh"><h2>Anteprima partecipante</h2>
<div style="width:210px;height:230px;padding:8px;border:1px solid #bbb">
<section class="linked-results result-view-bars"><strong>Risultati</strong><small>{LABEL}</small><div class="linked-results-items"><div class="linked-results-row"><span>{ANSWER}</span><output>6</output><div class="linked-results-track"><div style="width:80%"></div></div></div></div></section>
</div></div></div></body></html>'''

def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('QUORIVIO_BROWSER_BIN','/usr/bin/chromium'),args=['--no-sandbox'],headless=True)
  for width,height in [(1440,900),(390,844)]:
   page=browser.new_page(viewport={'width':width,'height':height});page.set_content(HTML)
   info=page.evaluate('''() => {
     const preview=document.querySelector('.rehearsal-backdrop');
     const center={x:innerWidth/2,y:innerHeight/2};
     const top=document.elementFromPoint(center.x,center.y);
     const s=document.querySelector('.linked-results>small');
     const label=document.querySelector('.linked-results-row span');
     const bounds=e=>({height:e.getBoundingClientRect().height,scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,whiteSpace:getComputedStyle(e).whiteSpace});
     return {overlayOnTop:preview.contains(top),overlayZ:getComputedStyle(preview).zIndex,editorZ:getComputedStyle(document.querySelector('.editor-ux-v2')).zIndex,panelZ:getComputedStyle(document.querySelector('.editor-floating-panel')).zIndex,small:bounds(s),label:bounds(label)};
   }''')
   assert info['overlayOnTop'], f'{width}px: preview hidden behind editor or inspector: {info}'
   assert int(info['overlayZ'])>max(int(info['editorZ']),int(info['panelZ']))
   for kind in ('small','label'):
    box=info[kind]
    assert box['whiteSpace']=='normal',f'{kind} forced to single line: {box}'
    assert box['height']>36, f'{width}px {kind} did not wrap: {box}'
    assert box['scrollWidth']<=box['clientWidth']+2, f'{kind} overflowed: {box}'
   page.close()
   print(f'PASS Chromium {width}x{height}: body preview above editor/inspectors and result labels wrap')
  browser.close()

if __name__=='__main__':main()
