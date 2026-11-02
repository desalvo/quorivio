#!/usr/bin/env python3
"""Real Chromium + PostgreSQL JPG background and Logo file-picker acceptance.

Runs only against the disposable authenticated CI deployment. It uses genuine
browser file chooser events and reads back the persisted design and private
asset content; it must not rely on mocked fetch routes or local state alone.
"""
import asyncio
import os
from pathlib import Path
from playwright.async_api import async_playwright, expect
from ci_browser_editor_postgres import BASE, call, open_editor, draft
from ci_editor_context_tools import open_canvas_context, uncovered_widget_context_point
from ci_http_isolation import ci_load_headers

JPG = Path(__file__).resolve().parents[1] / 'apps/api/test/fixtures/profile-valid.jpg'


async def persisted_widget(context, sid, aid, kind, attempts=65):
    for _ in range(attempts):
        snapshot = await call(context, 'GET', f'/api/sessions/{sid}')
        activity = next(a for a in snapshot['activities'] if a['id'] == aid)
        candidates = [w for w in activity['page_design'].get('widgets', []) if w['kind'] == kind]
        if candidates and candidates[0].get('assetId'):
            return candidates[0]
        await asyncio.sleep(.2)
    raise AssertionError(f'{kind} asset was not associated and persisted in PostgreSQL')


async def main():
    ci_load_headers(BASE)  # Reject non-disposable servers, including production.
    assert JPG.is_file() and JPG.read_bytes().startswith(bytes.fromhex('ffd8ff'))
    async with async_playwright() as pw:
        launch = {'executable_path': os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser = await pw.chromium.launch(**launch, headless=True, args=['--no-sandbox'])
        headers = {'X-Quorivio-Load-Token': os.environ['QUORIVIO_CI_LOAD_TOKEN']} if os.environ.get('QUORIVIO_CI_LOAD_TOKEN') else {}
        context = await browser.new_context(viewport={'width': 1440, 'height': 950}, extra_http_headers=headers)
        page = await context.new_page()
        page.set_default_timeout(15000)
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        title = 'CI real browser JPG backgrounds and logo picker'
        try:
            await call(context, 'POST', '/api/auth/login', {
                'email': os.environ['QUORIVIO_CI_ADMIN_EMAIL'],
                'password': os.environ['QUORIVIO_CI_NEW_PASSWORD'],
            })
            session = await call(context, 'POST', '/api/sessions', {'title': title}, 201)
            sid = session['id']
            activity = await call(context, 'POST', f'/api/sessions/{sid}/activities', {
                'title': 'JPG media picker page', 'type': 'poll',
                'options': [{'id': 'yes', 'label': 'Yes'}, {'id': 'no', 'label': 'No'}],
            }, 201)
            aid = activity['id']
            await call(context, 'PATCH', f'/api/sessions/{sid}/activities/{aid}/design', draft('Editor background'))
            await open_editor(page, title)
            canvas = page.get_by_role('group', name='Canvas grafico widget')
            await open_canvas_context(page)
            background_menu = page.get_by_role('group', name='Menu contestuale sfondo canvas')
            await expect(background_menu).to_be_visible()
            async with page.expect_file_chooser() as chooser:
                await background_menu.get_by_role('button', name='Carica immagine nello sfondo e nella libreria…').click()
            # Some desktop file pickers return a generic binary MIME. The UI
            # must use the JPG extension while the server validates real bytes.
            await (await chooser.value).set_files({'name': 'background.jpg', 'mimeType': 'application/octet-stream', 'buffer': JPG.read_bytes()})
            await expect(background_menu).to_have_count(0, timeout=15000)
            background_id = ''
            for _ in range(65):
                state = await call(context, 'GET', f'/api/sessions/{sid}')
                design = next(a for a in state['activities'] if a['id'] == aid)['page_design']
                background_id = design.get('backgroundAssetId', '')
                if background_id:
                    break
                await asyncio.sleep(.2)
            assert background_id, 'JPG background selection did not persist to the page'
            background_file = await context.request.get(BASE + f'/api/sessions/{sid}/assets/{background_id}')
            assert background_file.status == 200 and await background_file.body() == JPG.read_bytes()
            private_library = await call(context, 'GET', f'/api/sessions/{sid}/backgrounds')
            assert any(item['mine'] for item in private_library), 'Uploaded image missing from presenter background library'
            await expect(canvas).to_have_attribute('style', __import__('re').compile(r'--editor-page-background:.*assets/'))

            await page.get_by_role('button', name='Aggiungi widget: Logo').click()
            logo = page.locator('.widget-canvas-item[data-widget-kind="logo"]')
            await expect(logo).to_have_count(1)
            spot = await uncovered_widget_context_point(logo)
            await logo.click(button='right', position={'x': spot['offset_x'], 'y': spot['offset_y']})
            logo_menu = page.get_by_role('group', name='Azioni widget logo')
            await expect(logo_menu).to_be_visible()
            async with page.expect_file_chooser() as chooser:
                await logo_menu.get_by_label('Carica file logo').click()
            await (await chooser.value).set_files({'name': 'logo.jpg', 'mimeType': 'application/octet-stream', 'buffer': JPG.read_bytes()})
            stored_logo = await persisted_widget(context, sid, aid, 'logo')
            assert stored_logo['assetId'] != background_id, 'Logo and background must be independent attachments'
            logo_asset = await context.request.get(BASE + f'/api/sessions/{sid}/assets/{stored_logo["assetId"]}')
            assert logo_asset.status == 200 and await logo_asset.body() == JPG.read_bytes()
            await open_editor(page, title, session_id=sid, activity_id=aid)
            await expect(page.locator('.widget-canvas-item[data-widget-kind="logo"]')).to_have_count(1)
            assert not errors, f'Browser JavaScript errors: {errors[:4]}'
            print('PASS real PostgreSQL Chromium JPG background picker, private library, Logo upload and persisted reload')
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
