#!/usr/bin/env python3
"""Offline CSS geometry/keyboard probe for the *public* participant slide.

Loads the real production CSS, exercises saved positions and the accessible
reading alternative at desktop and 390px, and checks against rehearsal geometry.
This is NOT an authenticated React/PostgreSQL, Firefox/WebKit or device test.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = '''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body><main style="width:100%;max-width:1050px;margin:auto">
 <div class="audience-layout-controls" role="group" aria-label="Visualizzazione della pagina"><button id="fidelity" aria-pressed="true">Diapositiva 16:9</button><button id="reading" aria-pressed="false">Lettura accessibile</button></div>
 <div class="audience-stage-scroll" role="region" aria-label="Contenuto della diapositiva" tabindex="0"><div id="public" class="audience-widget-layout stage-fidelity">
 <div class="page-widget" id="public-widget" style="position:absolute;left:16%;top:23%;width:37%;height:26%;--stage-x:16%;--stage-y:23%;--stage-width:37%;--stage-height:26%;--stage-rotation:9deg;transform:rotate(9deg)"><button id="answer">Risposta</button></div>
 </div></div>
 <div class="rehearsal-pane" style="width:700px"><section class="rehearsal-slide"><div class="rehearsal-widgets"><div class="rehearsal-widget" id="preview-widget" style="--stage-x:16%;--stage-y:23%;--stage-width:37%;--stage-height:26%;--stage-rotation:9deg;transform:rotate(9deg)">Preview</div></div></section></div>
</main></body></html>'''

async def main():
    css=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
    async with async_playwright() as playwright:
        browser=await playwright.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for width,height in [(1440,940),(390,844)]:
                page=await browser.new_page(viewport={'width':width,'height':height})
                await page.set_content(HTML)
                await page.add_style_tag(content=css)
                result=await page.evaluate('''() => {
                 const stage=document.getElementById('public'),widget=document.getElementById('public-widget');
                 const r=stage.getBoundingClientRect(),w=widget.getBoundingClientRect();
                 // Rotation distorts the rendered bounding rectangle; compare
                 // computed absolute *layout offsets* instead.
                 const st=getComputedStyle(widget);
                 const ratio=r.width/r.height;
                 return {ratio,x:parseFloat(st.left)/r.width,y:parseFloat(st.top)/r.height,
                   width:parseFloat(st.width)/r.width,height:parseFloat(st.height)/r.height,
                   scroll:document.querySelector('.audience-stage-scroll').scrollWidth,
                   outer:document.querySelector('.audience-stage-scroll').clientWidth,
                   transform:st.transform,
                   background:getComputedStyle(stage).backgroundColor};
                }''')
                assert abs(result['ratio']-16/9)<0.025,result
                for label,expected in [('x',.16),('y',.23),('width',.37),('height',.26)]:
                    assert abs(result[label]-expected)<.006,(label,result)
                assert result['transform']!='none',result
                assert width!=390 or result['scroll']>result['outer'],result
                await page.locator('#public').evaluate("node=>{node.className='audience-widget-layout stage-reading'}")
                await page.locator('#reading').evaluate("node=>node.setAttribute('aria-pressed','true')")
                await page.locator('#fidelity').evaluate("node=>node.setAttribute('aria-pressed','false')")
                result=await page.evaluate('''() => {const stage=document.getElementById('public');const widget=document.getElementById('public-widget');const r=widget.getBoundingClientRect(),s=stage.getBoundingClientRect();return {widgetPosition:getComputedStyle(widget).position,ratio:s.width/s.height,transform:getComputedStyle(widget).transform,touch:document.getElementById('answer').getBoundingClientRect().height,stageLeft:r.left-s.left}}''')
                assert result['widgetPosition']=='relative' and result['transform']=='none',result
                assert result['touch']>=44,result
                assert 0<=result['stageLeft']<=30,result
                await page.close()
                print(f'PASS public CSS stage Chromium {width}px: faithful saved geometry, scroll and readable 44px-target mode')
        finally:
            await browser.close()

if __name__=='__main__':asyncio.run(main())
