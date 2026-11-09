#!/usr/bin/env python3
"""Capture REAL Quorivio UI for six manuals using the CI PostgreSQL instance.

Only permitted against disposable HTTP loopback, using synthetic fixture users,
not a production account/session. The script does not mock routes or render a
facsimile. An evidence manifest and PNG hashes accompany every CI artifact.
"""
from __future__ import annotations
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import struct
from urllib.parse import urlsplit

from playwright.async_api import async_playwright, expect
from ci_browser_participant import prepare, enter, vote, validate_disposable_origin
from ci_browser_editor_postgres import call, open_editor
from manual_screenshot_catalog import CATALOG, evidence, validate_capture_environment
from manual_release_metadata import metadata

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'docs/assets/manual-screenshots'
BASE=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')


async def dismiss_cookies(page):
    dlg=page.get_by_role('dialog',name='Informativa cookie funzionali')
    if await dlg.count() and await dlg.is_visible():
        await dlg.get_by_role('button',name='Ho capito').click()


def mark_capture(path, name):
    # Keep the actual screenshot pixels untouched. Provenance stays in the
    # manifest/PDF caption; do not place explanatory mock elements on the UI.
    data=path.read_bytes()
    if data[:8]!=b'\x89PNG\r\n\x1a\n' or data[12:16]!=b'IHDR':
        raise ValueError('Chromium returned an invalid PNG')
    return struct.unpack('>II',data[16:24])


async def main():
    validate_capture_environment(BASE)
    DEST.mkdir(parents=True,exist_ok=True)
    for png in DEST.glob('*.png'):
        png.unlink()  # No stale photo can be misattributed to the current run.
    (DEST/'capture.json').unlink(missing_ok=True)
    md=metadata()
    shots={}
    async with async_playwright() as pw:
        opts={'executable_path':os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser=await pw.chromium.launch(**opts,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            async def shot(stem,page,selector=None):
                assert stem in CATALOG
                if selector:
                    element=page.locator(selector)
                    await expect(element).to_be_visible(timeout=12000)
                    target=element
                else:
                    target=page
                await page.evaluate("document.activeElement?.blur()")
                # Hide join secrets and email fields; redact, never record passwords.
                masks=[page.locator('input[type="email"]'),page.locator('input[type="password"]'),
                       page.locator('a[href*="/join/"]'),page.locator('.participant-access-qr')]
                path=DEST/(stem+'.png')
                options={'path':str(path),'animations':'disabled','timeout':12000,'mask':masks,'mask_color':'#d2d9e5'}
                if not selector: options['full_page']=False
                await target.screenshot(**options)
                width,height=mark_capture(path,stem)
                shots[stem]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'width':width,'height':height}
                print('CAPTURED',stem,width,height,flush=True)

            # Capture login before any authentication, using the shipped production UI.
            guest=await browser.new_context(viewport={'width':1440,'height':940},locale='it-IT')
            page=await guest.new_page()
            await page.goto(BASE+'/',wait_until='domcontentloaded')
            await dismiss_cookies(page)
            await expect(page.locator('header .brand img').first).to_be_visible()
            await shot('login-desktop',page)
            await guest.close()

            # The fixture creates a REAL session, page and persisted widgets.
            _admin,sid,code,secret,_aid=prepare()
            headers={'X-Quorivio-Load-Token':os.environ['QUORIVIO_CI_LOAD_TOKEN']}
            ctx=await browser.new_context(viewport={'width':1440,'height':940},locale='it-IT',extra_http_headers=headers)
            r=await ctx.request.post(BASE+'/api/auth/login',data={'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
            if r.status!=200:raise AssertionError('Synthetic platform administrator login failed')
            admin=await ctx.new_page()
            await admin.goto(BASE+'/',wait_until='domcontentloaded')
            await dismiss_cookies(admin)
            await expect(admin.get_by_role('button',name='Apri sessione').first).to_be_visible()
            await shot('workspace-desktop',admin)
            nav=admin.get_by_role('region',name='Navigazione funzionalità')
            await nav.get_by_role('button',name='Impostazioni server').click()
            await expect(admin.get_by_role('heading',name='Configurazione server')).to_be_visible()
            await shot('admin-server-settings',admin)
            await shot('admin-backups',admin,'[aria-label="Backup completo dell’istanza"]')
            await shot('admin-audit',admin,'[aria-label="Audit amministrativo"]')
            await nav.get_by_role('button',name='Gestione utenti').click()
            await shot('admin-users',admin)

            editor=await ctx.new_page()
            await open_editor(editor,'CI Chromium real audience acceptance')
            await shot('editor-canvas',editor)
            # When a widget is selected, capture its genuinely rendered inspector.
            await editor.locator('.widget-canvas-item').first.click()
            if await editor.get_by_role('region',name='Proprietà widget').count():
                await shot('editor-widget-properties',editor)
            # Rehearsal is a genuine app dialog, never screenshot a fake fixture.
            preview=editor.get_by_role('button',name=re.compile('Anteprima',re.I)).first
            if await preview.count():
                await preview.click()
                dialog=editor.get_by_role('dialog',name='Anteprima interattiva della sessione')
                if await dialog.is_visible():
                    await shot('rehearsal-presenter',editor)
                    await dialog.get_by_role('button',name='Smartphone').click()
                    await shot('rehearsal-smartphone',editor)
                    await dialog.get_by_role('button',name='Chiudi anteprima').click()

            live=await ctx.new_page()
            await live.goto(BASE+'/screen/'+sid,wait_until='domcontentloaded')
            await live.wait_for_timeout(900)
            await shot('presenter-live',live)

            mob=await browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,is_mobile=True,has_touch=True,locale='it-IT',extra_http_headers=headers)
            phone=await mob.new_page()
            await phone.goto(BASE+'/join/'+secret,wait_until='domcontentloaded')
            await dismiss_cookies(phone)
            await expect(phone.get_by_role('heading',name='Partecipa alla sessione')).to_be_visible()
            await shot('participant-entry-smartphone',phone)
            await enter(phone,code,'Demo Partecipante',default_phone=True)
            await phone.get_by_role('button',name='Layout smartphone').click()
            await shot('participant-question-smartphone',phone)
            await phone.get_by_role('button',name='Diapositiva 16:9').click()
            await vote(phone,'Yes')
            await shot('participant-feedback-smartphone',phone)
            await mob.close();await ctx.close()
        finally:
            await browser.close()
    manifest={'source':'disposable-postgresql-chromium-live-app','fixture':'synthetic-only',
              'commit':md['commit'],'version':md['version'],'build':md['build'],
              'captured_at':datetime.now(timezone.utc).isoformat(),
              'shots':shots}
    (DEST/'capture.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf8')
    evidence(DEST,expected_commit=md['commit'] or None,minimum=9)
    role_counts={r:sum(r in CATALOG[s] for s in shots) for r in ('user','presenter','admin')}
    if min(role_counts.values())<3:raise AssertionError('Insufficient manual screenshot coverage: '+str(role_counts))
    print('CAPTURE SUCCESS',len(shots),role_counts,flush=True)

if __name__=='__main__': asyncio.run(main())
