#!/usr/bin/env python3
"""Offline Chromium CSS acceptance for RC223 footer, QR and counter sizing.

This exercises the actual shipped stylesheet in a representative DOM. It is
not a substitute for compiled React/real PostgreSQL acceptance in GitHub CI.
"""
from pathlib import Path
import asyncio
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text()

async def main():
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for viewport in (1440,390):
                page=await browser.new_page(viewport={'width':viewport,'height':840})
                html='''<main>
                  <div class="projection-widget" data-widget-kind="footer" data-vertical-align="bottom" style="position:relative;width:380px;height:110px;text-align:right;font:16px Arial">
                    <div class="widget-fit-frame"><div class="widget-fit-content"><div class="projection-slide-footer"><span class="slide-footer-center">Footer allineato a destra e in basso</span></div></div></div>
                  </div>
                  <div class="editor-ux-v2"><div class="widget-canvas-item" data-widget-kind="footer" data-vertical-align="bottom" style="position:relative;width:380px;height:110px;text-align:left;font:16px Arial">
                    <div class="widget-fit-frame"><div class="widget-fit-content"><span class="widget-rich-inline">Footer editor a sinistra</span></div></div>
                  </div></div>
                  <div class="projection-widget" data-widget-kind="qr" style="position:relative;width:130px;height:115px">
                    <div class="widget-fit-frame"><div class="widget-fit-content" style="height:100%"><div class="participant-access-qr" data-qr-show-url="true" data-qr-show-title="false"><img alt="QR" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='black'/%3E%3C/svg%3E"><a class="participant-qr-url" href="https://example.org/join/long/very/long/complete/link" title="https://example.org/join/long/very/long/complete/link">https://example.org/join/long/very/long/complete/link</a></div></div></div>
                  </div>
                  <div class="projection-widget" data-widget-kind="participant-count" data-show-title="true" style="position:relative;width:106px;height:83px"><div class="widget-fit-frame"><div class="widget-fit-content"><div class="projection-participant-count"><strong>Partecipanti connessi</strong><span data-live-participants="true">1254</span></div></div></div></div>
                  <div class="projection-widget" data-widget-kind="participant-count" data-show-title="false" style="position:relative;width:106px;height:68px"><div class="widget-fit-frame"><div class="widget-fit-content"><div class="projection-participant-count"><strong>Partecipanti connessi</strong><span data-live-participants="true">1254</span></div></div></div></div>
                  <div class="editor-floating-panel widget-selection-palette" style="position:relative;left:0;top:0;width:700px"><div class="widget-format-tabs" role="tablist">'''+''.join('<button type="button" role="tab"'+(' aria-selected="true"' if i==0 else '')+'>'+t+'</button>' for i,t in enumerate(['Testo','Bordi','Effetti','Contenuti','Collegamenti']))+'''</div><div class="palette-ribbon-groups" role="tabpanel">Controlli contestuali</div></div>
                </main>'''
                await page.set_content('<html><head><style>'+CSS+'</style></head><body>'+html+'</body></html>')
                data=await page.evaluate('''() => {
                  const rect=e=>{const b=e.getBoundingClientRect();return {top:b.top,bottom:b.bottom,left:b.left,right:b.right,width:b.width,height:b.height}}
                  const foot=document.querySelector('.projection-widget[data-widget-kind="footer"]');
                  const ftext=foot.querySelector('.slide-footer-center');
                  const editor=document.querySelector('.editor-ux-v2 [data-widget-kind="footer"]');
                  const etext=editor.querySelector('.widget-rich-inline');
                  const qr=document.querySelector('.participant-access-qr');
                  const url=qr.querySelector('.participant-qr-url');
                  const image=qr.querySelector('img');
                  const counts=[...document.querySelectorAll('.projection-widget[data-widget-kind="participant-count"]')].map(w=>{
                    const num=w.querySelector('[data-live-participants]'),title=w.querySelector('strong');
                    return {root:rect(w),number:rect(num),title:rect(title),titleDisplay:getComputedStyle(title).display,numberFont:getComputedStyle(num).fontSize,overflow:num.scrollWidth>num.clientWidth+1};
                  });
                  return {footer:{root:rect(foot),text:rect(ftext),align:getComputedStyle(ftext).textAlign},editor:{root:rect(editor),text:rect(etext),align:getComputedStyle(etext).textAlign},qr:{root:rect(qr),url:rect(url),img:rect(image),whiteSpace:getComputedStyle(url).whiteSpace,overflow:getComputedStyle(url).overflowX,scroll:url.scrollWidth,client:url.clientWidth},counts,tabs:document.querySelector('.widget-format-tabs').scrollHeight};
                }''')
                assert data['footer']['align']=='right',data
                assert data['footer']['text']['top']>data['footer']['root']['top']+30,data
                assert data['editor']['align']=='left',data
                assert data['editor']['text']['top']>data['editor']['root']['top']+30,data
                assert data['qr']['whiteSpace']=='nowrap',data
                assert data['qr']['overflow']=='auto',data
                assert data['qr']['url']['height']>=20 and data['qr']['url']['top']>=data['qr']['img']['bottom']-2,data
                assert len(data['counts'])==2 and not any(c['overflow'] for c in data['counts']),data
                assert data['counts'][0]['number']['bottom']<=data['counts'][0]['root']['bottom']+1,data
                assert data['counts'][1]['titleDisplay']=='none',data
                # Both editor and projected footer must respond to every authored
                # vertical setting, not merely the bottom-aligned fixture.
                offsets={}
                for mode in ('top','middle','bottom'):
                    offsets[mode]=await page.evaluate('''mode=>{
                      const nodes=[document.querySelector('.projection-widget[data-widget-kind="footer"]'),document.querySelector('.editor-ux-v2 [data-widget-kind="footer"]')];
                      return nodes.map(root=>{
                        root.setAttribute('data-vertical-align',mode);
                        const content=root.querySelector('.slide-footer-center,.widget-rich-inline');
                        return content.getBoundingClientRect().top-root.getBoundingClientRect().top;
                      });
                    }''',mode)
                assert all(offsets['top'][i]<offsets['middle'][i]<offsets['bottom'][i] for i in (0,1)),offsets
                print('PASS RC223 computed CSS at',viewport,'px, QR one-line height',data['qr']['url']['height'],'counter font',data['counts'][0]['numberFont'])
                await page.close()
        finally:
            await browser.close()

if __name__=='__main__':asyncio.run(main())
