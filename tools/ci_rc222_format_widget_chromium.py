#!/usr/bin/env python3
"""Chromium CSS acceptance for RC222 editor-only answer wrapping/Arial and compact ribbon.

Run explicitly after installing Playwright/Chromium. Static fixture covers the
real stylesheet (no mock CSS), including rich-text glyph spans and two layouts.
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
ANSWER='Questa è una risposta sufficientemente lunga per occupare più righe, anche quando l’opzione compare nell’editor; tutte le parole devono restare visibili e modificabili.'


def run():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('QUORIVIO_CHROMIUM_PATH') or '/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        try:
            for width in (1440,390):
                page=browser.new_page(viewport={'width':width,'height':900})
                # Browser fixture mirrors the production hierarchy (especially
                # the independent subquestion and RichWidgetText generated spans).
                page.set_content(f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
                <body><div class="editor-ux-v2">
                <div class="widget-canvas-item" data-widget-kind="question" style="width:280px;container-type:inline-size;font-family:Arial">
                  <div class="widget-fit-content">
                   <div class="canvas-widget-answer-preview" data-answer-mode="single" style="font-family:Arial;--q-answer-font-family:Arial;--q-answer-font-size:16px">
                    <label class="widget-answer-option"><input type="radio"/><div class="widget-rich-inline widget-rich-display" data-widget-text-field="option:a"><span id="plain">{ANSWER}</span></div></label>
                   </div>
                   <div class="canvas-subquestion"><div class="canvas-subquestion-option" style="--q-answer-font-family:Arial;--q-answer-font-size:16px">
                    <input type="checkbox"/><div class="widget-rich-inline" data-widget-text-field="question:q:option:a"><span id="sub">{ANSWER}</span></div>
                   </div></div>
                  </div>
                </div>
                <div class="editor-floating-panel widget-selection-palette" style="top:390px;left:8px">
                 <div class="palette-ribbon-head"><span class="palette-ribbon-context">Formato widget</span><span class="palette-ribbon-selection">Seleziona del testo per formattarlo</span><button class="palette-ribbon-dismiss">×</button></div>
                 <div class="palette-ribbon-groups">
                  <section class="palette-ribbon-group palette-ribbon-target" aria-label="Ambito formattazione"><div class="palette-ribbon-controls"><label>Applica a <select><option>Widget intero</option></select></label></div><span class="palette-ribbon-group-title">Ambito</span></section>
                  <section class="palette-ribbon-group palette-ribbon-font" aria-label="Carattere"><div class="palette-ribbon-controls"><div class="palette-ribbon-font-picker"><select><option>Arial</option></select><input type="number" value="16"/></div><div class="palette-ribbon-buttons"><button>B</button><button>I</button><button>U</button><button>S</button></div></div><span class="palette-ribbon-group-title">Carattere</span></section>
                  <section class="palette-ribbon-group palette-ribbon-paragraph" aria-label="Paragrafo"><div class="palette-ribbon-controls"><div class="palette-ribbon-buttons"><button>Left</button><button>Center</button><button>Right</button></div></div><span class="palette-ribbon-group-title">Paragrafo</span></section>
                  <section class="palette-ribbon-group palette-ribbon-shape" aria-label="Formato forma"><div class="palette-ribbon-controls"><div class="palette-ribbon-buttons"><button>Fill</button><button>Border</button></div></div><span class="palette-ribbon-group-title">Forma</span></section>
                  <section class="palette-ribbon-group palette-ribbon-answer-types" aria-label="Testo delle risposte"><div class="palette-ribbon-controls"><label class="palette-ribbon-answer">Campo % <input type="number" value="100"/></label><label class="palette-ribbon-answer">Campo px <input type="number" value="96"/></label></div></section>
                 </div>
                </div></div></body></html>''')
                values=page.evaluate('''() => {
                 const get=id=>{const el=document.getElementById(id),rich=el.parentElement,r=rich.getBoundingClientRect(),s=getComputedStyle(el),rStyle=getComputedStyle(rich);return {height:r.height,spanHeight:el.getBoundingClientRect().height,lineHeight:parseFloat(rStyle.lineHeight),whiteSpace:s.whiteSpace,display:s.display,font:s.fontFamily,parentFont:rStyle.fontFamily,text:rich.textContent}};
                 const bar=document.querySelector('.editor-floating-panel.widget-selection-palette');
                 const group=document.querySelector('.palette-ribbon-groups');
                 return {main:get('plain'),sub:get('sub'),barHeight:bar.getBoundingClientRect().height,groupHeight:group.getBoundingClientRect().height,viewport:innerWidth,barScrollHeight:group.scrollHeight,barClientHeight:group.clientHeight};
                }''')
                for key in ('main','sub'):
                    value=values[key]
                    assert value['font'].startswith('Arial') and value['parentFont'].startswith('Arial'),(width,key,value)
                    assert value['display']=='inline' and value['whiteSpace'] in ('pre-wrap','normal'),(width,key,value)
                    assert value['height']>value['lineHeight']*1.7,(width,key,value)
                    assert value['text']==ANSWER,(width,key,value)
                assert values['barHeight']<205,(width,values)
                assert values['barHeight']<900 and values['groupHeight']>0,(width,values)
                # Author-specified whole-widget override must flow to BOTH
                # independent and main choices, without changing text content.
                page.locator('.canvas-widget-answer-preview').evaluate('(el)=>{el.style.fontFamily="Georgia";el.style.setProperty("--q-answer-font-family","Georgia")}')
                page.locator('.canvas-subquestion-option').evaluate('(el)=>el.style.setProperty("--q-answer-font-family","Georgia")')
                families=page.evaluate('''() => ['#plain','#sub'].map(s=>getComputedStyle(document.querySelector(s)).fontFamily)''')
                assert all(f.startswith('Georgia') for f in families),(width,families)
                print('PASS RC222 Chromium',width,'px, multiline choice text, Arial defaults, whole-widget Georgia, ribbon height',round(values['barHeight'],1),'px')
                page.close()
        finally: browser.close()

if __name__=='__main__': run()
