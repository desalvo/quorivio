#!/usr/bin/env python3
"""RC252: exercise the actual compiled React editor, not a fake CSS widget.

Regression for CSSStyleDeclaration.fontFamily = undefined, which creates the
literal CSS family "undefined" on every unmarked RichWidgetText span. The parent
widget said Arial, so historical tests that inspected the parent passed while
users saw the fallback font in the real new-widget title and answer options.

An offline Chromium harness injects the production Vite bundle into a page with
an in-memory API and WebSocket fixture; no network, credentials or production DB
are required. The socket shim is scoped to the about:blank test URL, without
filtering any browser console/page errors.
"""
import asyncio
import json
import os
from pathlib import Path

from playwright.async_api import async_playwright, expect

from ci_browser_editor import (
    SESSION, ACTIVITY, SES, ACT,
    acknowledge_functional_cookie_notice,
)

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'apps/web/dist/assets'
BASE_WIDGETS = [
    {'id': 'arial-default', 'kind': 'question', 'label': 'Domanda senza stile',
     'answerMode': 'single',
     'options': [{'id': 'a', 'label': 'Risposta predefinita'},
                 {'id': 'b', 'label': 'Seconda risposta'}],
     'position': {'x': 4, 'y': 5, 'width': 38, 'height': 29}},
    {'id': 'author-styled', 'kind': 'question', 'label': 'Custom prompt',
     'answerMode': 'single',
     'style': {'fontFamily': 'Verdana', 'answerFontFamily': 'Tahoma'},
     'options': [{'id': 'c', 'label': 'Custom answer'}],
     'textMarks': [
         {'field': 'label', 'start': 0, 'end': 6,
          'style': {'fontFamily': 'Georgia'}},
         {'field': 'option:c', 'start': 0, 'end': 6,
          'style': {'fontFamily': 'Trebuchet MS'}},
     ],
     'position': {'x': 54, 'y': 5, 'width': 38, 'height': 29}},
]

# Source faithfully uses the compiled React component rather than hand-authored
# RichWidgetText HTML. A blank in-memory page is used because this environment
# forbids Chrome http://localhost navigation, not because a fixture would be enough.
BOOTSTRAP = r"""arg => {
 const fakeStore=()=>{const values=new Map();return {
   getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,String(value)),
   removeItem:key=>values.delete(key),clear:()=>values.clear(),
   key:n=>[...values.keys()][n]??null,get length(){return values.size}}};
 Object.defineProperty(window,'localStorage',{configurable:true,value:fakeStore()});
 Object.defineProperty(window,'sessionStorage',{configurable:true,value:fakeStore()});
 let cookie='';Object.defineProperty(document,'cookie',{
   configurable:true,get:()=>cookie,set:v=>{cookie+=(cookie?'; ':'')+v}});
 let seq=0;Object.defineProperty(window.crypto,'randomUUID',{
   configurable:true,value:()=>`00000000-0000-4000-8000-${String(++seq).padStart(12,'0')}`});
 // RC253: about:blank resolves the app's /live socket as ws://live/?session=...
 // There is no live server in the self-contained typography fixture. Replace
 // ONLY that synthetic test URL BEFORE React imports the production bundle.
 // Never suppress console/pageerror: unrelated errors must still fail the gate.
 const sockets=[];
 class OfflineFixtureWebSocket {
   static CONNECTING=0;static OPEN=1;static CLOSING=2;static CLOSED=3;
   constructor(url){
     this.url=String(url);
     if(!/^ws:\/\/live\/\?session=[0-9a-f-]+$/.test(this.url)){
       throw new Error('Unexpected WebSocket URL in offline React fixture: '+this.url);
     }
     this.readyState=OfflineFixtureWebSocket.CONNECTING;
     this.onopen=null;this.onclose=null;this.onerror=null;this.onmessage=null;
     sockets.push(this.url);
     queueMicrotask(()=>{
       if(this.readyState!==OfflineFixtureWebSocket.CONNECTING)return;
       this.readyState=OfflineFixtureWebSocket.OPEN;
       this.onopen?.(new Event('open'));
     });
   }
   close(){
     if(this.readyState===OfflineFixtureWebSocket.CLOSED)return;
     this.readyState=OfflineFixtureWebSocket.CLOSED;
     this.onclose?.(new CloseEvent('close',{code:1000,wasClean:true}));
   }
   send(){if(this.readyState!==OfflineFixtureWebSocket.OPEN)throw new Error('Fixture socket not open')}
 }
 window.WebSocket=OfflineFixtureWebSocket;
 window.__rc253_offline_socket_urls=sockets;
 const model={session:arg.session,activity:arg.activity,widgets:arg.widgets,revision:1,saves:0};
 window.__rc252=model;
 window.fetch=async(input,options={})=>{
   const url=String(input);let data=[];
   if(url==='/api/auth/me')data={id:'user-test',email:'test@example.org',nickname:'Test',role:'presenter'};
   else if(url==='/api/auth/oidc/providers')data={providers:[]};
   else if(url==='/api/sessions'||url.startsWith('/api/sessions?'))data={items:[model.session],total:1};
   else if(url==='/api/sessions/'+model.session.id)data={session:model.session,
      activities:[{...model.activity,design_revision:model.revision,
        page_design:{widgets:model.widgets},result_design:{}}],
      results:[],totals:[],connected_participants:0};
   else if(url.endsWith('/design')&&(options.method||'GET')==='PATCH'){
     const request=JSON.parse(options.body);
     model.widgets=JSON.parse(JSON.stringify(request.page_design.widgets));
     model.revision++;model.saves++;
     data={ok:true,design_revision:model.revision};
   }
   return new Response(JSON.stringify(data),{status:200,headers:{'Content-Type':'application/json'}});
 };
}"""


def faces_query(selector: str) -> str:
    return f'''el => [...el.querySelectorAll({json.dumps(selector)})].map(node => ({{
      computed:getComputedStyle(node).fontFamily,
      inline:node.style.fontFamily,
      text:node.textContent.trim()
    }}))'''


async def check(browser, width, height):
    page = await browser.new_page(viewport={'width': width, 'height': height})
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    try:
        await page.set_content('<!doctype html><html lang="it"><head><meta charset="utf-8" />'
                               '<meta name="viewport" content="width=device-width, initial-scale=1" />'
                               '</head><body><div id="root"></div></body></html>')
        css = list(DIST.glob('*.css'))
        js = list(DIST.glob('*.js'))
        assert len(css) == 1 and len(js) == 1, 'Build the actual frontend before this test'
        await page.add_style_tag(content=css[0].read_text(encoding='utf-8'))
        await page.evaluate(BOOTSTRAP, {'session': SES, 'activity': ACT, 'widgets': BASE_WIDGETS})
        # Prove the offline socket actually opens/closes inside Chromium, while
        # unexpected real endpoints are rejected instead of silently ignored.
        socket_probe = await page.evaluate('''expected => {
          const socket = new WebSocket(expected);
          return new Promise(resolve => queueMicrotask(() => {
            const opened = socket.readyState === WebSocket.OPEN;
            socket.close();
            let rejected = false;
            try { new WebSocket('ws://unrelated.invalid/live?session=other'); }
            catch { rejected = true; }
            resolve({opened, closed:socket.readyState === WebSocket.CLOSED, rejected});
          }));
        }''', f'ws://live/?session={SES["id"]}')
        assert socket_probe == {'opened': True, 'closed': True, 'rejected': True}, socket_probe
        await page.add_script_tag(content=js[0].read_text(encoding='utf-8'), type='module')
        await expect(page.locator('#root .app')).to_be_visible(timeout=25000)
        await acknowledge_functional_cookie_notice(page)
        await page.get_by_role('button', name='Apri sessione').first.click()
        card = page.locator('details').filter(has=page.get_by_text('Browser acceptance', exact=True))
        await card.locator('summary').click()
        await card.get_by_role('button', name='Apri sessione').click()
        await page.get_by_role('button', name='✎ Modifica le pagine').first.click()
        await expect(page.locator('.powerpoint-editor .widget-canvas-item')).to_have_count(2)

        normal = page.locator('.powerpoint-editor [data-widget-id="arial-default"]')
        assert await normal.evaluate('el => getComputedStyle(el).fontFamily') == 'Arial'
        title = await normal.evaluate(faces_query('[data-widget-text-field="label"] > span'))
        answers = await normal.evaluate(faces_query('.widget-answer-option .widget-rich-inline > span'))
        assert len(title) == 1 and len(answers) == 2, (title, answers)
        for row in title + answers:
            assert row['computed'] == 'Arial', ('RC252 real glyph fallback from Arial', width, row)
            assert not row['inline'], ('Never set font-family: undefined', width, row)

        authored = page.locator('.powerpoint-editor [data-widget-id="author-styled"]')
        custom_title = await authored.evaluate(faces_query('[data-widget-text-field="label"] > span'))
        custom_answer = await authored.evaluate(faces_query('.widget-answer-option .widget-rich-inline > span'))
        assert [(x['computed'], x['inline']) for x in custom_title] == [
            ('Georgia', 'Georgia'), ('Verdana', '')], custom_title
        assert [(x['computed'], x['inline']) for x in custom_answer] == [
            ('"Trebuchet MS"', '"Trebuchet MS"'), ('Tahoma', '')], custom_answer

        # Real click on the insert tool; verifies the actual initialized state,
        # React RichWidgetText mounted spans and global 80% studio zoom.
        await page.get_by_role('button', name='Aggiungi widget: Domanda o sondaggio').click()
        inserted = page.locator('.powerpoint-editor .widget-canvas-item[data-widget-kind="question"]')
        await expect(inserted).to_have_count(3)
        new = inserted.last
        created = await new.evaluate(faces_query('[data-widget-text-field="label"] > span'))
        assert len(created) == 1 and created[0]['text'] == 'Nuova domanda', created
        assert created[0]['computed'] == 'Arial' and not created[0]['inline'], created
        assert await new.evaluate('el => getComputedStyle(el).fontFamily') == 'Arial'
        assert await page.evaluate("getComputedStyle(document.documentElement).zoom") == '0.8', 'Studio compact zoom regressed'
        fixture_sockets = await page.evaluate('window.__rc253_offline_socket_urls')
        # A dormant session need not open a socket on every browser/runner.
        # Any socket it does open must use the one explicitly isolated URL.
        assert fixture_sockets and all(
            url == f'ws://live/?session={SES["id"]}' for url in fixture_sockets
        ), ('Unexpected isolated test socket', fixture_sockets)
        assert await page.evaluate('window.WebSocket.name') == 'OfflineFixtureWebSocket' 
        assert not errors, ('Compiled React errors', errors[:3])
        print(f'PASS RC252 compiled React Chromium {width}x{height}: native insertion, Arial title and options, preserved marked Georgia/Trebuchet, no undefined CSS font')
    finally:
        await page.close()


async def main():
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=True, executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH', '/usr/bin/chromium'),
            args=['--no-sandbox'])
        try:
            for width, height in [(390, 844), (1440, 940)]:
                await check(browser, width, height)
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
