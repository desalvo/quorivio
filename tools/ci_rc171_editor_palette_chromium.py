#!/usr/bin/env python3
"""RC171 real Chromium CSS acceptance for visible phone switch and responsive graphic rail.

Uses a static, token-free editor fixture. No network, sessions or secrets.
The end-to-end React click/context-menu flow remains a GitHub CI acceptance.
"""
from __future__ import annotations
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parents[1]

def html():
    normal=''.join('<span class="editor-icon-wrapper"><button type="button" class="editor-icon-tool"><svg width="24" height="24"></svg><span class="editor-icon-caption">Widget</span></button></span>' for _ in range(17))
    graphic=''.join(f'<span class="editor-icon-wrapper editor-graphic-wrapper"><button type="button" data-graphic-palette="{k}" class="editor-icon-tool"><svg width="24" height="24"></svg><span class="editor-icon-caption">{label}</span></button><button class="editor-graphic-options" aria-label="Opzioni {label}">⋯</button></span>' for k,label in [('line','Linee'),('shape','Forme')])
    return f'''<!doctype html><html><head><meta charset="utf-8"></head><body>
    <section class="powerpoint-editor editor-ux-v2" style="width:100%;height:95vh;">
      <header class="editor-mock-header">
        <div class="editor-mock-brand"><span>Quorivio · Sessione</span></div>
        <div class="editor-device-switch" role="group" aria-label="Layout da modificare">
          <span class="device-label is-active">Desktop 16:9</span>
          <label class="editor-device-slider"><input type="checkbox" role="switch" aria-label="Modifica layout Smartphone"/><span class="editor-device-slider-track"><span class="editor-device-slider-thumb"></span></span></label>
          <span class="device-label">Smartphone 390px</span>
        </div>
        <div class="editor-mock-actions"><button>Anteprima</button><button>Esci</button></div>
      </header>
      <aside class="page-editor-sidebar">Pagine</aside>
      <aside class="editor-widget-rail"><div class="editor-widget-grid">{normal}{graphic}</div></aside>
      <div class="editor-stage"><div class="editor-canvas-slot" style="height:160px">Canvas</div></div>
    </section></body></html>'''

async def main():
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for width,height in [(1440,900),(960,760),(620,740)]:
                page=await browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
                await page.set_content(html(),wait_until='domcontentloaded')
                await page.add_style_tag(path=str(ROOT/'apps/web/src/style.css'))
                result=await page.evaluate('''() => {
                  const box = s=>document.querySelector(s).getBoundingClientRect();
                  const palette=document.querySelector('.editor-widget-grid');
                  const normal=box('.editor-icon-wrapper:not(.editor-graphic-wrapper)>.editor-icon-tool');
                  const line=box('[data-graphic-palette=line]');
                  const shape=box('[data-graphic-palette=shape]');
                  const toggle=box('.editor-device-switch');
                  const header=box('.editor-mock-header');
                  const slot=box('.editor-canvas-slot');
                  const options=box('.editor-graphic-options');
                  return {normal:normal.width,line:line.width,shape:shape.width,toggleY:toggle.y,headerY:header.y,headerBottom:header.bottom,
                          slotY:slot.y,optionsWidth:options.width,scrollW:palette.scrollWidth,clientW:palette.clientWidth,
                          paletteHeight:palette.clientHeight,viewportW:innerWidth};
                }''')
                assert result['line']<=72 and result['shape']<=72, f'giant graphic icon at {width}: {result}'
                assert abs(result['line']-result['normal'])<=15, f'graphic button not standard-sized: {result}'
                assert result['optionsWidth']<=26, f'graphic options overflow: {result}'
                assert result['toggleY']>=result['headerY']-1 and result['toggleY']<result['headerBottom']+1, f'switch not in top header: {result}'
                assert result['slotY']>=result['headerBottom']-1, f'canvas hidden under header: {result}'
                assert result['scrollW']<=result['clientW']+3, f'horizontal palette overflow at {width}: {result}'
                assert result['paletteHeight']<=min(int(height*.3),198)+3, f'palette too tall: {result}'
                await page.get_by_role('switch',name='Modifica layout Smartphone').check()
                assert await page.get_by_role('switch',name='Modifica layout Smartphone').is_checked()
                print(f'PASS RC171 Chromium editor {width}x{height}: slider visible, graphic icons compact, palette wraps without x scroll')
                await page.close()
        finally:
            await browser.close()

if __name__=='__main__':asyncio.run(main())
