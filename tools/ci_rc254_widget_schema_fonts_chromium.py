#!/usr/bin/env python3
"""RC254: compiled real React widget AND slide-master authoring Arial test.

Exercises the shared WidgetCanvas/RichWidgetText machinery with all text-bearing
widget kinds, title/footer, independent quiz options and explicit overrides.
Must not hide browser errors; uses the previously reviewed offline WebSocket shim.
"""
import asyncio
import copy
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from ci_browser_editor import SES, ACT, acknowledge_functional_cookie_notice
from ci_rc252_arial_rich_dom_chromium import BOOTSTRAP

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'apps/web/dist/assets'
TEXT_KINDS=['title','footer','question','timed-quiz','topic-question','rating','reactions',
            'timer','qr','profile','text','postit','participant-count','results-button']

def widgets():
 result=[]
 for i,kind in enumerate(TEXT_KINDS):
  item={'id':'font-'+kind,'kind':kind,'label':('Nuova domanda' if kind=='question' else 'Quiz a tempo' if kind=='timed-quiz' else 'Esempio '+kind),
        'position':{'x':3+(i%4)*24,'y':3+(i//4)*23,'width':21,'height':19,'rotation':0},
        'autoFit':False}
  if kind in ('question','timed-quiz'):
   item.update(answerMode='single',options=[{'id':'first','label':'Prima opzione'},{'id':'second','label':'Seconda opzione'}],
     questions=[{'id':'child','label':'Domanda secondaria','answerMode':'single','options':[{'id':'child-option','label':'Risposta secondaria'}]}])
  if kind in ('text','postit','rating','profile'):
   item['description']='Descrizione senza carattere esplicito'
  if kind=='footer':item.update(footerShowSessionTitle=False,footerShowPageNumber=True)
  if kind=='qr':item['showTitle']=True
  if kind=='question':
   item['textMarks']=[{'field':'label','start':0,'end':5,'style':{'fontFamily':'Georgia'}},
                      {'field':'option:first','start':0,'end':5,'style':{'fontFamily':'Trebuchet MS'}}]
   item['style']={'fontFamily':'Verdana','answerFontFamily':'Tahoma'}
  if kind=='postit': item['style']={'fontFamily':'undefined'}  # invalid older/imported snapshot
  result.append(item)
 return result

async def check_area(page,area):
 assert await page.locator(area+' .widget-canvas-item').count() >= len(TEXT_KINDS)-1
 found=await page.locator(area+' .widget-canvas-item').evaluate_all('''nodes => nodes.map(el => ({kind:el.dataset.widgetKind,face:getComputedStyle(el).fontFamily,
   spans:[...el.querySelectorAll('[data-widget-text-field] > span')].map(n=>({face:getComputedStyle(n).fontFamily,inline:n.style.fontFamily,text:(n.textContent||'').trim()}))}))''')
 seen=set()
 for item in found:
  kind=item['kind'];seen.add(kind)
  expected='Verdana' if kind=='question' else 'Arial'
  assert item['face']==expected,(area,kind,'container',item['face'])
  for span in item['spans']:
   text=span['text'];expected_span='Arial' if kind!='question' else 'Verdana'
   if kind=='question' and text in ('Nuova','Prima'):expected_span='Georgia' if text=='Nuova' else '"Trebuchet MS"'
   if kind=='question' and text.startswith(('opzione','Seconda','Risposta')):expected_span='Tahoma'
   assert span['face']==expected_span,(area,kind,span,expected_span)
   assert span['inline'] not in ('undefined','null','NaN'),(area,kind,span)
  assert all('undefined' not in n['inline'] for n in item['spans'])
 assert set(TEXT_KINDS)<=seen,(area,sorted(set(TEXT_KINDS)-seen))
 assert any(item['kind']=='question' and len(item['spans'])>=5 for item in found),'Independent question fields missing'
 return len(found),sum(len(x['spans']) for x in found)

async def check(browser,width,height):
 page=await browser.new_page(viewport={'width':width,'height':height})
 errors=[]
 page.on('pageerror',lambda e: errors.append(str(e)))
 page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None)
 try:
  await page.set_content('<!doctype html><html lang="it"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /></head><body><div id="root"></div></body></html>')
  css=list(DIST.glob('*.css'));js=list(DIST.glob('*.js'))
  assert len(css)==1 and len(js)==1,'Actual compiled frontend missing'
  await page.add_style_tag(content=css[0].read_text())
  # Reuse the same persisted layout in the page editor and the slide-master editor.
  session=copy.deepcopy(SES);session['theme']={'master':{'widgets':widgets()}}
  await page.evaluate(BOOTSTRAP,{'session':session,'activity':ACT,'widgets':widgets()})
  await page.add_script_tag(content=js[0].read_text(),type='module')
  await expect(page.locator('#root .app')).to_be_visible(timeout=25000)
  await acknowledge_functional_cookie_notice(page)
  await page.get_by_role('button',name='Apri sessione').first.click()
  card=page.locator('details').filter(has=page.get_by_text('Browser acceptance',exact=True))
  await card.locator('summary').click()
  await card.get_by_role('button',name='Apri sessione').click()
  await page.get_by_role('button',name='✎ Modifica le pagine').first.click()
  await expect(page.locator('.powerpoint-editor .widget-canvas-item')).to_have_count(len(TEXT_KINDS),timeout=15000)
  regular=await check_area(page,'.powerpoint-editor')
  # The page editor overlays the dashboard sidebar: invoke the genuine
  # accessible schema shortcut handler directly to exercise the master route.
  await page.get_by_role('button',name='Apri editor degli schemi della sessione').evaluate('el => el.click()')
  await expect(page.locator('.slide-scheme-workspace .widget-canvas-item')).to_have_count(len(TEXT_KINDS),timeout=15000)
  master=await check_area(page,'.slide-scheme-workspace')
  assert not errors,('React browser errors',errors[:3])
  print(f'PASS RC254 compiled React {width}x{height}: page {regular}, slide masters {master}, all Arial defaults and explicit Georgia/Trebuchet/Verdana/Tahoma overrides')
 finally:
  await page.close()

async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
  try:
   for dims in [(390,844),(1440,940)]: await check(browser,*dims)
  finally:
   await browser.close()

if __name__=='__main__': asyncio.run(main())
