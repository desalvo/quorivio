#!/usr/bin/env python3
"""RC193: real compiled React + disposable PostgreSQL authoring focus and font acceptance.

Runs only on localhost with authenticated disposable test credentials. Tests a
stale last-option cursor, continuous typing into the first option and the
properties drawer without reloading the page, then font input/answer parity.
"""
import asyncio
import os
from playwright.async_api import async_playwright, expect
from ci_browser_editor_postgres import call, open_editor

async def main():
 async with async_playwright() as pw:
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
  headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']} if os.environ.get('QUORIVIO_CI_LOAD_TOKEN') else {}
  context=await browser.new_context(viewport={'width':1440,'height':950},extra_http_headers=headers)
  page=await context.new_page();page.set_default_timeout(12000)
  js_errors=[];page.on('pageerror',lambda e:js_errors.append(str(e)))
  try:
   await call(context,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
   title='CI RC193 editor focus and font regression'
   session=await call(context,'POST','/api/sessions',{'title':title},201)
   sid=session['id']
   activity=await call(context,'POST',f'/api/sessions/{sid}/activities',{'title':'Focus and font','type':'poll','options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]},201)
   aid=activity['id']
   question={'id':'focusq','kind':'question','label':'Domanda di verifica','answerMode':'single',
    'options':[{'id':'a','label':'Prima'},{'id':'b','label':'Seconda'},{'id':'c','label':'Terza'}],
    'position':{'x':10,'y':10,'width':70,'height':70,'rotation':0},
    'style':{'fontFamily':'Arial','fontSize':18,'fillNone':True}}
   await call(context,'PATCH',f'/api/sessions/{sid}/activities/{aid}/design',{'page_design':{'backgroundColor':'#FFFFFF','widgets':[question]},'result_design':{}})
   await open_editor(page,title)
   widget=page.locator('.widget-canvas-item[data-widget-id="focusq"]')
   await expect(widget).to_have_count(1)
   await widget.click(button='right',position={'x':14,'y':14})
   menu=page.get_by_role('group',name='Azioni widget question',exact=True)
   await menu.get_by_role('button',name='Modifica titolo').click()
   first=widget.locator('[data-widget-text-field="option:a"]')
   last=widget.locator('[data-widget-text-field="option:c"]')
   await expect(first).to_have_attribute('contenteditable','true')
   # First establish a remembered caret in the LAST option, then move to the
   # first one. The previous bug restored the stale last-option selection on
   # every parent rerender (first character went to the right place only).
   await last.focus();await page.keyboard.press('End');await page.keyboard.type(' memorizzata')
   await first.focus();await page.keyboard.press('End')
   await page.keyboard.type(' frase completa senza perdere focus',delay=12)
   await expect(first).to_contain_text('Prima frase completa senza perdere focus')
   owner=await page.evaluate("document.activeElement?.getAttribute('data-widget-text-field')")
   assert owner=='option:a',f'Editor caret moved unexpectedly to {owner!r}'
   await page.keyboard.type(' e altre parole',delay=15)
   await expect(first).to_contain_text('e altre parole')
   assert await page.evaluate("document.activeElement?.getAttribute('data-widget-text-field')")=='option:a'
   # Updating the inspector must not steal focus to the last answer either.
   await widget.click(button='right',position={'x':14,'y':14})
   await page.get_by_role('group',name='Azioni widget question',exact=True).get_by_role('button',name='Proprietà widget').click()
   option3=page.get_by_role('textbox',name='Testo opzione 3')
   option1=page.get_by_role('textbox',name='Testo opzione 1')
   await expect(option1).to_be_visible()
   await option3.fill('Ultima modifica precedente')
   await option1.fill('Testo iniziale')
   await option1.press('End')
   await page.keyboard.type(' scrivo tutta la frase',delay=12)
   await expect(option1).to_have_value('Testo iniziale scrivo tutta la frase')
   assert await option1.evaluate('e=>document.activeElement===e'),'Properties drawer lost the active answer input'
   # Return to whole-widget scope: selected option text can temporarily force
   # the Answer scope while the caret is active.
   await page.get_by_role('combobox',name='Ambito della formattazione').select_option('widget')
   # Numeric editing: an empty intermediate value is allowed; commit by Enter.
   size=page.get_by_role('spinbutton',name='Dimensione del testo selezionato')
   await expect(size).to_be_visible()
   await size.fill('')
   await expect(size).to_have_value('')
   await size.fill('27');await size.press('Enter')
   await expect(size).to_have_value('27')
   await page.get_by_role('button',name='Aumenta dimensione carattere di 1').click()
   await expect(size).to_have_value('28')
   font=page.get_by_role('combobox',name='Font del testo')
   await font.select_option('Georgia')
   family=await widget.locator('.widget-answer-option').first.evaluate('e=>getComputedStyle(e).fontFamily')
   assert 'Georgia' in family,f'Answer options did not inherit the whole-widget font: {family}'
   await font.select_option('Arial')
   family=await widget.locator('.widget-answer-option').first.evaluate('e=>getComputedStyle(e).fontFamily')
   assert 'Arial' in family,f'Answer options did not restore the default Arial: {family}'
   assert not js_errors,f'Unexpected browser JS errors: {len(js_errors)}'
  finally:
   await context.close();await browser.close()
 print('PASS RC193 real Chromium/PostgreSQL: stale-caret no-steal, continuous editor and drawer typing, numeric font arrows, Arial/whole-widget answer font parity')

if __name__=='__main__':asyncio.run(main())
