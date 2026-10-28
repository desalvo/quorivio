#!/usr/bin/env python3
"""Network-free true Chromium CSS geometry contract on 16:9 editor/preview/audience.
A fast preflight; does not certify end-to-end PostgreSQL or visual sign-off.
"""
import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

CSS=(Path(__file__).resolve().parents[1]/'apps/web/src/style.css').read_text()

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH') or shutil.which('chromium') or shutil.which('google-chrome') or '/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        for vw,stage_width in [(1440,960),(390,288)]:
            page=await browser.new_page(viewport={'width':vw,'height':950})
            markup='''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/><style>'''+CSS+'''</style></head><body style="margin:0">
              <div class="editor-ux-v2" style="position:absolute!important;inset:auto!important;width:auto!important;height:auto!important;display:block!important;top:10px!important;left:10px!important">
              <div class="canvas-with-rulers" style="width:STAGEpx"><div class="widget-canvas"><div class="widget-canvas-item" id="ed" style="--stage-x:5%;--stage-y:10%;--stage-width:22%;--stage-height:24%;left:5%;top:10%;width:22%;height:24%;background:yellow">Timer</div></div></div></div>
              <div class="rehearsal-shell" style="position:absolute;left:10px;top:550px;width:STAGEpx;height:auto"><div class="rehearsal-stage" style="padding:0!important;width:STAGEpx;height:auto;min-height:0!important;overflow:visible"><section class="rehearsal-slide" style="width:STAGEpx"><div class="rehearsal-widgets"><div class="rehearsal-widget" id="re" style="--stage-x:5%;--stage-y:10%;--stage-width:22%;--stage-height:24%;left:5%;top:10%;width:22%;height:24%;background:yellow">Timer</div></div></section></div></div>
              <div class="audience-widget-layout" id="audience" style="position:absolute!important;top:1120px;left:10px;width:STAGEpx"><div class="page-widget" id="au" style="position:absolute;--stage-x:5%;--stage-y:10%;--stage-width:22%;--stage-height:24%;left:5%;top:10%;width:22%;height:24%;background:yellow">Timer</div></div>
              <span class="editor-floating-tooltip tooltip-left" id="tip" style="top:50px;left:STAGEpx">Aggiungi widget: Domanda o sondaggio</span>
              </body></html>'''.replace('STAGE',str(stage_width))
            await page.set_content(markup)
            result=await page.evaluate('''() => {
              const pairs=[['.widget-canvas','#ed'],['.rehearsal-widgets','#re'],['.audience-widget-layout','#au']];
              return pairs.map(([p,w])=>{
                const a=document.querySelector(p).getBoundingClientRect(),b=document.querySelector(w).getBoundingClientRect();
                return {aspect:a.width/a.height,x:100*(b.x-a.x)/a.width,y:100*(b.y-a.y)/a.height,width:100*b.width/a.width,height:100*b.height/a.height};
              });
            }''')
            for area in result:
                assert abs(area['aspect']-16/9)<.07,(vw,area)
                assert abs(area['x']-5)<.75,(vw,area)
                assert abs(area['y']-10)<.75,(vw,area)
                assert abs(area['width']-22)<.75,(vw,area)
                assert abs(area['height']-24)<.75,(vw,area)
            size=await page.locator('#tip').bounding_box()
            assert size is not None and size['width']>size['height']*2,(vw,size)
            print(f'PASS Chromium {vw}px: editor/preview/audience 16:9 geometry and rectangular tooltip')
            await page.close()
        await browser.close()

if __name__=='__main__':asyncio.run(main())
