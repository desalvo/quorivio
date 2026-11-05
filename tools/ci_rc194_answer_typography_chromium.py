#!/usr/bin/env python3
"""Chromium computed-style regression: long answer wrap, shared font, title hierarchy.

This fixture deliberately runs against the actual app CSS without a network service.
The built React integration is separately exercised by the existing CI browser gate.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
STYLE = (ROOT / 'apps/web/src/style.css').read_text()
LONG = 'Questa risposta comprende una descrizione sufficientemente lunga da richiedere due oppure tre righe senza interrompere il testo, anche quando il widget viene visualizzato su uno schermo stretto.'

def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        try:
            for width in (1440, 390):
                page = browser.new_page(viewport={'width': width, 'height': 800})
                page.set_content('''<div class="editor-ux-v2"><div class="widget-canvas-item" data-widget-kind="question" style="font-family:Arial;font-weight:700;font-size:22px;width:235px;">
                <div class="widget-fit-content"><div class="widget-rich-inline" id="question-title">Domanda di prova</div>
                <div class="canvas-widget-answer-preview" data-answer-mode="single" style="--q-answer-font-family:Georgia;--q-answer-font-size:16px;font:inherit;">
                  <label class="widget-answer-option" style="--q-answer-font-family:Georgia;--q-answer-font-size:16px;">
                    <input type="radio" disabled/><span class="widget-rich-inline" id="answer">PLACEHOLDER</span>
                  </label>
                </div></div></div></div>
                <div class="projection-widget" data-widget-kind="question" style="font-family:Arial;font-weight:700;font-size:22px;width:235px;"><div class="projection-interactive-widget"><label class="widget-answer-option" style="--q-answer-font-family:Georgia;--q-answer-font-size:16px"><input type="checkbox" disabled/><span id="live-answer">PLACEHOLDER</span></label></div></div>'''.replace('PLACEHOLDER',LONG))
                page.add_style_tag(content=STYLE)
                results=page.evaluate('''() => {
                    const answer=document.querySelector('#answer'),live=document.querySelector('#live-answer'),
                      title=document.querySelector('#question-title');
                    const style=el=>getComputedStyle(el);
                    return {
                      answerFamily:style(answer).fontFamily,liveFamily:style(live).fontFamily,
                      titleFamily:style(title).fontFamily,titleWeight:style(title).fontWeight,
                      titleSize:parseFloat(style(title).fontSize),answerSize:parseFloat(style(answer).fontSize),
                      lines:answer.getBoundingClientRect().height / parseFloat(style(answer).lineHeight),
                      textHeight:answer.getBoundingClientRect().height,
                      answerWhiteSpace:style(answer).whiteSpace,
                      labelHeight:document.querySelector('.canvas-widget-answer-preview .widget-answer-option').getBoundingClientRect().height
                    };
                }''')
                assert results['answerFamily'].startswith('Georgia'), results
                assert results['liveFamily'].startswith('Georgia'), results
                assert results['titleFamily'].startswith('Arial'), results
                assert results['titleSize']>results['answerSize'], results
                assert results['titleWeight'] in ('700','bold'), results
                assert results['answerWhiteSpace']=='pre-wrap',results
                assert results['textHeight']>results['answerSize']*2,results
                assert results['labelHeight']>results['answerSize']*2,results
                page.close()
                print(f'PASS RC194 Chromium CSS {width}px: full-widget faces, bold larger title, long multiline answers')
        finally:
            browser.close()

if __name__=='__main__':
    main()
