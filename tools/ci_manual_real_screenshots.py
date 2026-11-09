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

# RC283: only the real editor toolbar opener is allowed. A generic accessible
# name containing 'Anteprima' also matches a disabled answer-submit mock inside
# the canvas; selecting that mock caused the RC282 GitHub CI timeout.
PRESENTER_REHEARSAL_OPENER='button.editor-preview-open.preview-presenter[aria-haspopup="dialog"]'


async def open_presenter_rehearsal(editor):
    button=editor.locator(PRESENTER_REHEARSAL_OPENER)
    await expect(button).to_have_count(1, timeout=12000)
    await expect(button).to_be_visible(timeout=12000)
    await expect(button).to_be_enabled(timeout=12000)
    await button.click(timeout=12000)
    dialog=editor.get_by_role('dialog',name='Anteprima interattiva della sessione')
    await expect(dialog).to_be_visible(timeout=12000)
    return dialog



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
            await expect(editor.locator('.page-editor-thumbnails')).to_be_visible(timeout=12000)
            await shot('editor-thumbnails-widgets',editor)
            # A true right-click (not an SVG or disabled mock action) must keep
            # the portaled, independently scrollable menu visible.
            first_widget=editor.locator('.widget-canvas-item').first
            await first_widget.click(button='right')
            context_menu=editor.locator('.canvas-context-menu')
            await expect(context_menu).to_be_visible(timeout=12000)
            await shot('editor-widget-context',editor)
            format_opener=context_menu.get_by_role('button',name='Formato widget')
            if await format_opener.count():
                await format_opener.click()
                floating=editor.get_by_role('toolbar',name='Formattazione rapida widget selezionato')
                await expect(floating).to_be_visible(timeout=12000)
                await shot('editor-widget-format',editor)
                contents=floating.get_by_role('tab',name='Contenuti')
                if await contents.count():
                    # RC290: this acceptance criterion applies AFTER a manual resize.
                    # An auto-sized panel can correctly change height between tabs;
                    # do not misreport that as a format-window regression. Drive the
                    # real accessible resize handle (keyboard is deterministic on
                    # Chromium even if the palette is docked near the screen edge).
                    original=await floating.bounding_box()
                    resize_handle=floating.get_by_role('button',name='Ridimensiona Formattazione rapida widget selezionato (trascina o usa le frecce)')
                    await expect(resize_handle).to_be_visible(timeout=12000)
                    await resize_handle.focus()
                    await resize_handle.press('Shift+ArrowRight')
                    await resize_handle.press('Shift+ArrowDown')
                    resized=await floating.bounding_box()
                    if (not original or not resized or
                        resized['width']-original['width'] < 24 or
                        resized['height']-original['height'] < 24):
                        raise RuntimeError('Widget Formatting resize handle did not enlarge both dimensions')
                    await shot('editor-widget-format-resized',editor)
                    await contents.click()
                    after=await floating.bounding_box()
                    if (not after or abs(resized['width']-after['width']) > 2 or
                        abs(resized['height']-after['height']) > 2):
                        raise RuntimeError('Widget Formatting changed resized outer size when switching tabs')
                    await shot('editor-widget-format-tabs',editor)
                await floating.get_by_role('button',name='Chiudi Formato widget').click()
            else:
                await editor.keyboard.press('Escape')
            await expect(context_menu).to_have_count(0,timeout=12000)
            # Select an authored widget and open the *real* inspector with
            # its own toolbar button; do not claim an unopened panel exists.
            await editor.locator('.widget-canvas-item').first.click()
            inspector_opener=editor.get_by_role('button',name='Mostra proprietà complete del widget')
            if await inspector_opener.count() and await inspector_opener.first.is_visible():
                await inspector_opener.first.click()
                inspector=editor.get_by_role('region',name='Proprietà widget selezionato')
                await expect(inspector).to_be_visible(timeout=12000)
                await shot('editor-widget-properties',editor)
                # Dismiss this floating region before opening the rehearsal;
                # it may overlay toolbar click targets on smaller viewports.
                await inspector.get_by_role('button',name='Chiudi proprietà widget').click()
                await expect(inspector).to_have_count(0,timeout=12000)
            # Capture the actual session-rehearsal dialog, not a disabled
            # 'Anteprima' submit-button drawn as part of the widget canvas.
            dialog=await open_presenter_rehearsal(editor)
            await shot('rehearsal-presenter',editor)
            await dialog.get_by_role('button',name='Partecipante').click()
            await expect(dialog.locator('.rehearsal-mode-participant')).to_be_visible(timeout=12000)
            await shot('rehearsal-participant',editor)
            await dialog.get_by_role('button',name='Affiancate').click()
            await expect(dialog.locator('.rehearsal-mode-both')).to_be_visible(timeout=12000)
            await shot('rehearsal-side-by-side',editor)
            await dialog.get_by_role('button',name='Smartphone').click()
            await expect(dialog.locator('.rehearsal-mode-mobile')).to_be_visible(timeout=12000)
            await shot('rehearsal-smartphone',editor)
            await dialog.get_by_role('button',name='Chiudi anteprima').click()
            # Master editor is a genuinely separate work surface: capture it
            # through the real toolbar instead of drawing a simulated flowchart.
            await editor.locator('button.editor-schemes-open').click(timeout=12000)
            scheme=editor.get_by_role('region',name='Editor degli schemi PowerPoint')
            await expect(scheme).to_be_visible(timeout=12000)
            await shot('editor-schema',editor)
            master_widgets=scheme.locator('.widget-canvas-item')
            if await master_widgets.count():
                await master_widgets.first.click()
                await shot('editor-schema-inspector',editor)
            await scheme.get_by_role('button',name='Esci dagli schemi').click()
            attachments=editor.locator('details.dashboard-attachments-collapsible')
            if await attachments.count() and await attachments.is_visible():
                if await attachments.evaluate('(el)=>el.open'):
                    raise AssertionError('Session attachments must start collapsed')
                await shot('session-attachments-collapsed',editor)
                await attachments.locator('summary').click()
                await expect(attachments).to_have_attribute('open','',timeout=12000)
                await shot('session-attachments-expanded',editor)

            live=await ctx.new_page()
            await live.goto(BASE+'/screen/'+sid,wait_until='domcontentloaded')
            await live.wait_for_timeout(900)
            await shot('presenter-live',live)
            await live.wait_for_timeout(350)
            await shot('presenter-live-secondary',live)

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
            await shot('participant-widescreen',phone)
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
    evidence(DEST,expected_commit=md['commit'] or None,minimum=18)
    role_counts={r:sum(r in CATALOG[s] for s in shots) for r in ('user','presenter','admin')}
    if min(role_counts.values())<4:raise AssertionError('Insufficient manual screenshot coverage: '+str(role_counts))
    print('CAPTURE SUCCESS',len(shots),role_counts,flush=True)

if __name__=='__main__': asyncio.run(main())
