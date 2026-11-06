#!/usr/bin/env python3
"""RC226 actual CSS acceptance on phone + tablet + desktop: studio screens fit."""
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()
SHELL='''<div class="app"><header><span class="brand">Quorivio</span><nav><a href="#">Manuale</a><a href="#">Dashboard</a><button>Logout</button></nav></header><div class="dashboard"><aside class="aside"><div class="list"><button class="session">Sessione lunga</button><button class="session">Un'altra sessione</button></div></aside><main class="workspace"><div class="workspace-head"><h2>Dashboard</h2><button>Apri sessione</button></div><section class="panel"><h3>Statistiche</h3><table><tr>'''+''.join('<td>Dati '+str(i)+'</td>' for i in range(15))+'''</tr></table></section><div class="slide-scheme-workspace"><header class="slide-scheme-header"><h2>Editor schemi</h2><button>Esci</button></header><div class="slide-scheme-ribbon">'''+''.join('<div class="slide-scheme-ribbon-group"><strong>Allinea</strong><div class="slide-scheme-ribbon-actions">'+''.join('<button class="slide-scheme-ribbon-tool"><span class="slide-scheme-ribbon-icon">▤</span><span class="slide-scheme-ribbon-caption">'+str(i)+'</span></button>' for i in range(6))+'</div></div>' for _ in range(4))+'''</div><div class="slide-scheme-widget-rail"><strong>Widget</strong><div class="slide-scheme-widget-options">'''+''.join('<button data-widget-kind="question"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/></svg><span>Domanda</span></button>' for _ in range(15))+'''</div></div><div class="slide-scheme-layout"><div class="slide-scheme-canvas"><div class="canvas-with-rulers"><div class="widget-canvas"></div></div></div><aside class="panel slide-scheme-inspector">Proprietà dello schema</aside></div></div></main></div></div>'''
EDITOR='''<section class="editor-ux-v2"><header class="editor-mock-header"><div class="editor-mock-brand">Quorivio</div><div class="editor-mock-actions"><div class="editor-mock-action-buttons"><button>Esci</button><button>Anteprima</button><button>Salva</button></div></div><div class="editor-device-switch">Smartphone</div></header><aside class="page-editor-sidebar"><header><strong>Pagine</strong></header><div class="page-editor-thumbnails">'''+''.join('<div class="page-editor-thumb-row"><button class="page-editor-thumb"><span class="page-editor-preview">Anteprima</span></button></div>' for _ in range(16))+'''</div></aside><div class="editor-widget-rail"><div class="editor-widget-grid">'''+''.join('<button class="editor-icon-tool">A</button>' for _ in range(16))+'''</div></div><main class="editor-stage"><div class="editor-canvas-slot"><div class="canvas-editor-group"><div class="canvas-with-rulers"><div class="widget-canvas"></div></div></div></div><div class="editor-bottom-controls">Azioni</div></main></section>'''
async def run():
 async with async_playwright() as p:
  browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  try:
   for width,height in [(320,568),(390,844),(760,920),(1440,900)]:
    page=await browser.new_page(viewport={'width':width,'height':height},is_mobile=width<800,has_touch=width<800)
    await page.set_content('<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+CSS+'</style></head><body>'+SHELL+'</body></html>')
    out=await page.evaluate('''() => {
      const d=document.querySelector('.dashboard'), w=document.querySelector('.workspace'),r=document.querySelector('.slide-scheme-ribbon'), g=document.querySelector('.slide-scheme-widget-options');
      const width=e=>Math.round(e.getBoundingClientRect().width);
      return {dashboardWidth:width(d),workspaceWidth:width(w),ribbonScrollable:r.scrollWidth>r.clientWidth,widgetScrollable:g.scrollWidth>g.clientWidth,
      workspaceFits:w.getBoundingClientRect().right<=innerWidth+2, ribbonFits:r.getBoundingClientRect().right<=innerWidth+2};
    }''')
    assert out['workspaceFits'] and out['ribbonFits'],(width,out)
    if width<=760:assert out['ribbonScrollable'] and out['widgetScrollable'],(width,out)
    await page.set_content('<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+CSS+'</style></head><body>'+EDITOR+'</body></html>')
    view=await page.evaluate('''() => {
     const stage=document.querySelector('.editor-stage'), rail=document.querySelector('.page-editor-sidebar'), thumbs=document.querySelector('.page-editor-thumbnails'), palette=document.querySelector('.editor-widget-grid'),root=document.querySelector('.editor-ux-v2');
     const r=e=>e.getBoundingClientRect();
     return {columns:getComputedStyle(root).gridTemplateColumns.split(' ').length,stageFits:r(stage).right<=innerWidth+2,
     railFits:r(rail).right<=innerWidth+2,thumbnailsScrollable:thumbs.scrollWidth>thumbs.clientWidth,
     paletteScrollable:palette.scrollWidth>palette.clientWidth,stageVisible:r(stage).height>50};
    }''')
    assert view['stageFits'] and view['stageVisible'],(width,view)
    if width<=760:assert view['columns']==1 and view['railFits'] and view['thumbnailsScrollable'] and view['paletteScrollable'],(width,view)
    else:assert view['columns']>=2,(width,view)
    print(f'PASS RC226 Chromium {width}×{height}: studio, master ribbon, page editor layout',flush=True)
    await page.close()
  finally:await browser.close()
if __name__=='__main__':asyncio.run(run())
