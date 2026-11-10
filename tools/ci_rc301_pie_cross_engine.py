#!/usr/bin/env python3
"""RC301: native CSS and production pie-geometry parity for Chromium/Firefox/WebKit.

Uses the shipped stylesheet AND actual TypeScript resultPieLayout imported by
Node, not a hand-computed SVG. Browser evidence is an offline rendering check:
it is not a PostgreSQL live-vote test, a physical iOS Safari test, or an
independent screen-reader/AGID certification.
"""
from __future__ import annotations

import argparse
import asyncio
from html import escape
import json
import os
from pathlib import Path
import subprocess

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path('/tmp/quorivio-cross-browser-artifacts')
OPTIONS = [
    f"{i+1}. Una risposta molto lunga con lettere accentate, punteggiatura e "
    "parole leggibili su più righe anche da smartphone"
    for i in range(12)
]
COUNTS = [100_000_000] + [1] * 11

def production_geometry() -> dict:
    # The production calculation is imported, not reimplemented by this test.
    js = (
        "import {resultPieLayout} from './apps/web/src/result-pie-layout.ts';"
        f"const counts={json.dumps(COUNTS)};"
        "console.log(JSON.stringify({"
        "visible:resultPieLayout(counts,85,true,true),"
        "hidden:resultPieLayout([2,1],85,false,false)"
        "}));"
    )
    raw = subprocess.check_output(
        ['node','--experimental-strip-types','--input-type=module','-e',js],
        cwd=ROOT, text=True, timeout=20
    )
    data=json.loads(raw)
    assert len(data['visible']) == 12
    assert len(data['hidden']) == 2
    assert all(row['label'] for row in data['visible'])
    assert all(not row['label'] for row in data['hidden'])
    return data

def markup(slices:list[dict], *,percentages:bool, editor_phone:bool=False) -> str:
    if percentages:
        labels=OPTIONS
    else:
        labels=['Prima opzione','Seconda opzione']
    calls=[]
    legend=[]
    paths=[]
    for row in slices:
        n=row['index']-1
        name=labels[n]
        count=int(row['count'])
        plural='risposta' if count==1 else 'risposte'
        percentage=row['label'].split(' ')[-1] if percentages else ''
        description=f'{name}: {count} {plural}'+(f', {percentage}' if percentages else '')
        paths.append(
            '<path d="'+escape(row['path'],quote=True)+'" fill="#277fd1">'
            '<title>'+escape(description)+'</title></path>'
        )
        if row['label']:
            calls.append(
                '<g class="linked-results-pie-callout"><polyline points="'
                +escape(row['leader'],quote=True)+'" />'
                f'<text x="{row["labelX"]}" y="{row["labelY"]}" '
                f'text-anchor="{("end" if row["side"]=="left" else "start")}" '
                'dominant-baseline="middle">'+escape(row['label'])+'</text></g>'
            )
        if percentages:
            legend.append(
                '<div class="linked-results-pie-mobile-item" role="listitem" aria-label="'
                +escape(description,quote=True)+'">'
                '<span class="linked-results-pie-mobile-swatch" aria-hidden="true"></span>'
                '<span class="linked-results-pie-mobile-name">'+escape(name)+'</span>'
                '<strong class="linked-results-pie-mobile-percent">'+escape(percentage)+'</strong></div>'
            )
    wrapper = (
        '<div class="editor-ux-v2"><div class="canvas-editor-group" '
        'data-canvas-device="phone"><div class="widget-canvas-item" '
        'data-widget-kind="results-button">'
    ) if editor_phone else '<div class="widget-canvas-item" data-widget-kind="results-button">'
    closes='</div></div></div>' if editor_phone else '</div>'
    svg_label = ('Distribuzione percentuale delle risposte. Legenda accessibile con conteggi e percentuali.'
                 if percentages else 'Distribuzione delle risposte.')
    legend_markup=(
        '<div class="linked-results-pie-mobile-legend" role="list" '
        'aria-label="Percentuali delle risposte">'+''.join(legend)+'</div>'
    ) if percentages else ''
    return (
        '<!doctype html><html lang="it"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
        '<body><main style="width:min(100%,350px);margin:0 auto">'
        +wrapper+
        '<section class="linked-results result-view-pie" style="width:100%;font:18px Arial">'
        '<svg class="linked-results-pie linked-results-pie-chart" role="img" '
        'aria-label="'+escape(svg_label,quote=True)+'" '
        f'data-mobile-percent-labels="{str(percentages).lower()}" '
        'viewBox="0 0 500 320" preserveAspectRatio="xMidYMid meet">'
        +''.join(paths)+''.join(calls)+'</svg>'+legend_markup+
        '</section>'+closes+'</main></body></html>'
    )

async def check_page(page, css:str, data:dict, *,phone:bool,editor_phone:bool) -> None:
    await page.set_content(markup(data['visible'],percentages=True,editor_phone=editor_phone))
    await page.add_style_tag(content=css)
    legend=page.get_by_role('list',name='Percentuali delle risposte')
    assert await legend.count()==1,'accessible list missing'
    assert await legend.get_by_role('listitem').count()==12,'all nonzero slices must be described'
    assert await page.locator('.linked-results-pie-chart path title').count()==12
    report=await page.evaluate('''() => {
      const legend=document.querySelector('.linked-results-pie-mobile-legend');
      const chart=document.querySelector('.linked-results-pie-chart');
      const percent=[...legend.querySelectorAll('.linked-results-pie-mobile-percent')];
      const names=[...legend.querySelectorAll('.linked-results-pie-mobile-name')];
      const callouts=[...chart.querySelectorAll('.linked-results-pie-callout')];
      const svg=chart.getBoundingClientRect();
      const box=legend.getBoundingClientRect();
      return {
        count:percent.length,
        legendVisible:getComputedStyle(legend).position==='static' &&
          getComputedStyle(legend).clipPath==='none' && box.width>80,
        overflow:legend.scrollWidth>legend.clientWidth+1,
        minPercentFont:Math.min(...percent.map(x=>parseFloat(getComputedStyle(x).fontSize))),
        namesWrap:names.every(x=>getComputedStyle(x).whiteSpace==='normal' &&
          getComputedStyle(x).overflowWrap==='anywhere'),
        longNameHasMultipleLines:names.some(x=>x.getBoundingClientRect().height>
          parseFloat(getComputedStyle(x).lineHeight)*1.5),
        allNamesFit:names.every(x=>x.scrollWidth<=x.clientWidth+1),
        calloutsVisible:callouts.every(x=>getComputedStyle(x).display!=='none'),
        chartRatio:svg.width/svg.height,
        properDescriptions:[...legend.querySelectorAll('[role="listitem"]')]
          .every(x=>x.getAttribute('aria-label')?.includes('rispost') &&
                     x.getAttribute('aria-label')?.includes('%')),
        tinySharePresent:[...legend.querySelectorAll('[role="listitem"]')]
          .some(x=>x.getAttribute('aria-label')?.includes('<0.0001%')),
      };
    }''')
    assert report['count']==12 and report['properDescriptions'] and report['tinySharePresent'],report
    assert report['namesWrap'],report
    assert abs(report['chartRatio']-500/320)<.06,report
    if phone:
        assert not report['overflow'] and report['allNamesFit'],report
        assert report['legendVisible'] and report['minPercentFont']>=14,report
        assert report['longNameHasMultipleLines'],report
        assert not report['calloutsVisible'],report
    else:
        assert not report['legendVisible'] and report['calloutsVisible'],report
    # Disabled percentages must never be present in SVG titles or a ghost legend.
    await page.set_content(markup(data['hidden'],percentages=False,editor_phone=editor_phone))
    await page.add_style_tag(content=css)
    assert await page.get_by_role('list',name='Percentuali delle risposte').count()==0
    titles=await page.locator('.linked-results-pie-chart path title').all_text_contents()
    assert len(titles)==2 and all('%' not in value for value in titles),titles

async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engines',nargs='+',choices=['chromium','firefox','webkit'],default=['chromium'])
    args=parser.parse_args()
    data=production_geometry()
    css=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
    async with async_playwright() as pw:
        for engine in args.engines:
            kwargs={'headless':True}
            if engine=='chromium':
                kwargs.update(executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),
                              args=['--no-sandbox'])
            browser=await getattr(pw,engine).launch(**kwargs)
            try:
                for name,width,phone,editor in (
                    ('desktop',1200,False,False),
                    ('phone390',390,True,False),
                    ('phone360',360,True,False),
                    ('editor-phone',1200,True,True),
                ):
                    context=await browser.new_context(viewport={'width':width,'height':860},locale='it-IT')
                    try:
                        page=await context.new_page()
                        page.set_default_timeout(10000)
                        errors=[]
                        page.on('pageerror',lambda error:errors.append(str(error)))
                        try:
                            await check_page(page,css,data,phone=phone,editor_phone=editor)
                            assert not errors,'Browser JavaScript errors: '+repr(errors[:3])
                        except Exception as error:
                            ARTIFACTS.mkdir(parents=True,exist_ok=True)
                            target=ARTIFACTS/f'rc301-{engine}-{name}'
                            try:await page.screenshot(path=str(target)+'.png',full_page=True,timeout=3000)
                            except Exception:pass
                            Path(str(target)+'.json').write_text(json.dumps({
                                'engine':engine,'case':name,'error':type(error).__name__,
                                'message':str(error)[:500],
                                'note':'Public fixture data; no credentials or personal information.'
                            },indent=2),encoding='utf8')
                            raise
                    finally:
                        await context.close()
                    print(f'RC301 PASS: {engine}, {name}: real TS pie geometry, wrapped names, readable percent legend, no disabled percentage leak')
            finally:
                await browser.close()

if __name__=='__main__':
    asyncio.run(main())
