#!/usr/bin/env python3
"""Opt-in Chromium + real PostgreSQL profile photo lifecycle acceptance.

Uses actual browser file input, actual authenticated HTTP and an isolated
anonymous request context. Requires disposable CI admin and the built app.
"""
import asyncio
import base64
import os
from pathlib import Path
from urllib.parse import urlsplit
from playwright.async_api import async_playwright,expect

BASE=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
assert urlsplit(BASE).scheme=='http' and urlsplit(BASE).hostname in ('localhost','127.0.0.1')
ART=Path(os.environ.get('QUORIVIO_BROWSER_ARTIFACT_DIR','/tmp/quorivio-browser-artifacts'))
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO6X7e8AAAAASUVORK5CYII=')

async def main():
 async with async_playwright() as pw:
  launch={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
  browser=await pw.chromium.launch(**launch,headless=True,args=['--no-sandbox'])
  headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']} if os.environ.get('QUORIVIO_CI_LOAD_TOKEN') else {}
  context=await browser.new_context(viewport={'width':1440,'height':1000},extra_http_headers=headers)
  page=await context.new_page();page.set_default_timeout(12000)
  try:
   login=await context.request.post(BASE+'/api/auth/login',data={'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
   assert login.status==200,(login.status,await login.text())
   await page.goto(BASE+'/',wait_until='domcontentloaded')
   notice=page.get_by_role('dialog',name='Informativa cookie funzionali')
   if await notice.is_visible():
    await notice.get_by_role('button',name='Ho capito').click()
   await page.get_by_role('button',name='Profilo presentatore').click()
   name=page.get_by_role('textbox',name='Nome visualizzato')
   await expect(name).to_be_visible()
   await expect(name).to_have_value('CI Presenter Profile')
   await name.fill('CI Browser Presenter')
   await page.get_by_role('button',name='Salva profilo').click()
   await expect(page.get_by_text('Profilo salvato')).to_be_visible()
   await page.get_by_label('Carica foto del profilo').set_input_files({'name':'ci-avatar.png','mimeType':'image/png','buffer':PNG})
   await expect(page.get_by_text('Foto aggiornata')).to_be_visible()
   await expect(page.get_by_role('img',name='Foto profilo')).to_be_visible()
   profile=await context.request.get(BASE+'/api/auth/profile')
   assert profile.status==200
   data=await profile.json();assert data['display_name']=='CI Browser Presenter' and data['profile_photo_url']
   # Public projection and public bytes are accessible without a session cookie.
   session=await context.request.post(BASE+'/api/sessions',data={'title':'CI browser public avatar'})
   assert session.status==201
   s=await session.json();sid=s['id'];code=s['join_code']
   activated=await context.request.post(BASE+f'/api/sessions/{sid}/status',data={'status':'active'})
   assert activated.status==200
   anonymous=await pw.request.new_context()
   try:
    projection=await anonymous.get(BASE+f'/api/join/{code}/presenter-profiles')
    assert projection.status==200
    profiles=await projection.json();assert len(profiles)==1
    assert profiles[0]['name']=='CI Browser Presenter' and profiles[0]['photo_url']
    assert 'email' not in profiles[0] and 'profile_photo_url' not in profiles[0]
    image=await anonymous.get(BASE+profiles[0]['photo_url'])
    assert image.status==200 and await image.body()==PNG
    private=await anonymous.get(BASE+data['profile_photo_url'])
    assert private.status==401
    await page.get_by_role('button',name='Elimina foto').click()
    await expect(page.get_by_text('Foto rimossa')).to_be_visible()
    await expect(page.get_by_role('img',name='Foto profilo')).to_have_count(0)
    removed=await anonymous.get(BASE+profiles[0]['photo_url'])
    assert removed.status==404
   finally:
    await anonymous.dispose()
   print('PASS Chromium + PostgreSQL presenter profile: atomic save, real photo upload/preview, anonymous scoped avatar, private access denial, deletion')
  except Exception:
   ART.mkdir(parents=True,exist_ok=True)
   await page.screenshot(path=str(ART/'profile-failure.png'),full_page=True)
   (ART/'profile-failure.html').write_text(await page.content(),encoding='utf-8')
   raise
  finally:
   await context.close();await browser.close()

if __name__=='__main__':asyncio.run(main())
