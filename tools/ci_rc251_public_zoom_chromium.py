#!/usr/bin/env python3
"""Offline Chromium check for the RC251 studio/public physical pixel separation.

This test uses the real stylesheet and a representative question DOM. The
authenticated API/PostgreSQL+React lifecycle remains the responsibility of the
existing tools/ci_browser_participant.py gate in the full GitHub workflow.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    root=Path(__file__).resolve()
    # Accept --repo=... or default to checkout next to this script.
    import sys
    repo=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root.parents[1]
    css=(repo/'apps/web/src/style.css').read_text(encoding='utf8')
    html='''<!doctype html><html><body style="margin:0">
      <div class="audience-widget-layout stage-phone" style="height:720px;width:390px">
        <div class="page-widget" data-widget-kind="question" style="--stage-x:4%;--stage-y:16%;--stage-width:92%;--stage-height:33.0556%;--mobile-widget-font-size:20px">
          <section class="widget-question"><strong>Domanda leggibile</strong>
            <label class="widget-answer-option"><input type="radio" name="choice"><span>Prima opzione</span></label>
            <label class="widget-answer-option"><input type="radio" name="choice"><span>Seconda opzione</span></label>
          </section>
        </div>
      </div></body></html>'''
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        try:
            for width in (390,760):
                page=await browser.new_page(viewport={'width':width,'height':844})
                await page.set_content(html)
                await page.add_style_tag(content=css)
                results={}
                for name,scale in [('previous_root_zoom','80%'),('rc251_public_live','100%')]:
                    await page.evaluate('''zoom=>{document.documentElement.style.zoom=zoom;
                      document.documentElement.style.setProperty('--quorivio-ui-scale',String(parseFloat(zoom)/100));}''',scale)
                    results[name]=await page.locator('.stage-phone').evaluate('''stage=>{
                      const rows=[...stage.querySelectorAll('.widget-answer-option')];
                      const r=stage.getBoundingClientRect();
                      return {width:r.width,choices:rows.map(el=>({height:el.getBoundingClientRect().height,
                        cssFont:parseFloat(getComputedStyle(el).fontSize)}))};
                    }''')
                former=results['previous_root_zoom']; fixed=results['rc251_public_live']
                assert all(row['height']<43.5 for row in former['choices']),results
                assert abs(former['choices'][0]['height']-35.2)<2,results
                assert all(row['height']>=43.5 for row in fixed['choices']),results
                assert abs(fixed['width']-390)<2,results
                print(f'PASS {width}px Chromium: previous 80% root rendered {former["choices"][0]["height"]:.1f}px (broken); '
                      f'RC251 public native scale renders {fixed["choices"][0]["height"]:.1f}px (44px target preserved).')
                await page.close()
        finally:
            await browser.close()
if __name__=='__main__':asyncio.run(main())
