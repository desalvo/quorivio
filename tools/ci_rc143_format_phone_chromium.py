#!/usr/bin/env python3
"""Browser CSS acceptance: visible formatting, wrapped cloud and true 390px mobile stage."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
HTML='''<!doctype html><html><head><meta charset="utf-8"><style>__CSS__</style></head>
<body class="editor-ux-v2"><div class="widget-selection-palette editor-floating-panel" style="top:10px;left:8px" role="toolbar" aria-label="Formato widget">
  <div class="palette-ribbon-head"><span class="palette-ribbon-context">Formato widget</span><strong class="palette-widget-label">Risultati</strong><span class="palette-ribbon-selection">Testo selezionato nella domanda</span><button type="button" class="palette-ribbon-dismiss" aria-label="Chiudi Formato widget" onclick="this.closest('.widget-selection-palette').remove()">X</button></div>
  <div class="palette-ribbon-groups">__GROUPS__</div></div>
  <div class="linked-results result-view-cloud" style="position:absolute;top:350px;left:8px;width:175px;height:200px;font-size:17px;">
    <div class="linked-results-items"><div class="linked-results-row"><span class="linked-result-pair"><span class="linked-result-label">Infrastrutture di calcolo distribuito </span><span class="linked-result-final">avanzato<output>[15]</output></span></span></div></div>
  </div>
  <div class="rehearsal-pane rehearsal-pane-phone" style="position:absolute;top:350px;left:240px;width:390px">
   <div class="rehearsal-phone-frame"><div class="rehearsal-phone-stage-sizer" style="height:720px"><div class="rehearsal-phone-stage" style="width:390px;height:720px;transform:scale(1)">
     <section class="rehearsal-slide" style="background-image:none;background-color:#e0f8ff;"><div class="rehearsal-widgets">
      <div class="rehearsal-widget" id="phone-widget" style="--stage-x:20%;--stage-y:25%;--stage-width:40%;--stage-height:20%;left:20%;top:25%;width:40%;height:20%;">Widget</div>
     </div></section></div></div></div>
  </div>
</body></html>'''.replace('__CSS__',CSS).replace('__GROUPS__',''.join(f'<section class="palette-ribbon-group"><div class="palette-ribbon-controls"><label>Gruppo {n}<input aria-label="Scelta {n}" type="text" value="Opzione lunga"/></label></div></section>' for n in range(8)))

def check():
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH') or '/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  try:
   for width,height in [(1225,720),(390,760)]:
    page=browser.new_page(viewport={'width':width,'height':height})
    page.set_content(HTML)
    close=page.get_by_role('button',name='Chiudi Formato widget')
    close.wait_for(state='visible')
    box=close.bounding_box()
    assert box and box['x']>=0 and box['x']+box['width']<=width,('close invisible',width,box)
    ribbon=page.locator('.palette-ribbon-groups')
    metrics=ribbon.evaluate('(node)=>({client:node.clientWidth,scroll:node.scrollWidth,scrollY:node.scrollHeight,clientY:node.clientHeight,overflowY:getComputedStyle(node).overflowY})')
    assert metrics['scroll']<=metrics['client']+2,('groups have inaccessible horizontal overflow',width,metrics)
    assert metrics['overflowY'] in ('auto','scroll'),('groups must scroll vertically when taller',metrics)
    cloud=page.locator('.linked-result-pair')
    assert cloud.evaluate('(node)=>getComputedStyle(node).whiteSpace')=='normal'
    tail=page.locator('.linked-result-final')
    assert tail.evaluate('(node)=>getComputedStyle(node).whiteSpace')=='nowrap'
    phone=page.locator('#phone-widget')
    outer=page.locator('.rehearsal-phone-stage')
    parent=outer.bounding_box();pos=phone.bounding_box()
    assert parent and pos
    assert abs((pos['x']-parent['x'])/parent['width']-.20)<.02,(width,parent,pos)
    assert abs((pos['y']-parent['y'])/parent['height']-.25)<.02,(width,parent,pos)
    assert page.locator('.rehearsal-phone-stage .rehearsal-slide').evaluate('(e)=>getComputedStyle(e).backgroundImage')=='none'
    assert page.locator('.rehearsal-phone-stage .rehearsal-slide').evaluate('(e)=>getComputedStyle(e).backgroundColor')=='rgb(224, 248, 255)'
    close.click();assert page.locator('.widget-selection-palette').count()==0
    page.close()
  finally: browser.close()
if __name__=='__main__':
 check();print('PASS RC144 formatting window, top cloud line-wrap and independent phone stage (1225px/390px)')
