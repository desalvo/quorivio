#!/usr/bin/env python3
"""Fail fast if Chromium cannot load the compiled application from Vite preview.

Do not use dev-server modules: the RC browser acceptance must exercise exactly
what the shipped container serves. Errors are limited to asset metadata; never
log private cookies, authentication payloads or session URLs.
"""
from __future__ import annotations

import asyncio
import os
import re
from urllib.parse import urlsplit
from playwright.async_api import async_playwright

BASE = os.environ.get('QUORIVIO_WEB_URL', 'http://127.0.0.1:5173/').rstrip('/')
assert urlsplit(BASE).hostname in ('127.0.0.1', 'localhost'), 'CI preview must remain loopback-only'


async def probe() -> None:
    async with async_playwright() as pw:
        opts = {'executable_path': os.environ['QUORIVIO_CHROMIUM_PATH']} if os.environ.get('QUORIVIO_CHROMIUM_PATH') else {}
        browser = await pw.chromium.launch(headless=True, args=['--no-sandbox'], **opts)
        try:
            page = await browser.new_page(viewport={'width': 1440, 'height': 900})
            page_errors: list[str] = []
            asset_statuses: list[tuple[str, int]] = []
            failed_assets: list[str] = []
            page.on('pageerror', lambda err: page_errors.append(type(err).__name__))

            def on_response(resp):
                path = urlsplit(resp.url).path
                if path.startswith('/assets/') and (path.endswith('.js') or path.endswith('.css')):
                    asset_statuses.append(('JS' if path.endswith('.js') else 'CSS', resp.status))

            def on_failure(req):
                path = urlsplit(req.url).path
                if path.startswith('/assets/'):
                    failed_assets.append('JS' if path.endswith('.js') else 'CSS' if path.endswith('.css') else 'asset')

            page.on('response', on_response)
            page.on('requestfailed', on_failure)

            async def mock_api(route):
                path = urlsplit(route.request.url).path
                if path == '/api/auth/me':
                    await route.fulfill(status=401, content_type='application/json', json={'error': 'not_authenticated'})
                elif path == '/api/auth/oidc/providers':
                    await route.fulfill(status=200, content_type='application/json', json={'providers': []})
                else:
                    await route.fulfill(status=404, content_type='application/json', json={'error': 'not_found'})

            await page.route('**/api/**', mock_api)
            response = await page.goto(BASE + '/', wait_until='domcontentloaded')
            html = await page.locator('html').inner_html()
            assert response and response.status == 200, 'production preview HTML was not served'
            assert re.search(r'/assets/index-[^"\s]+\.js', html), 'production JS is missing from preview HTML'
            assert '/src/main.tsx' not in html and '/@vite/client' not in html, 'dev HTML served instead of production HTML'
            try:
                await page.locator('#root .app').wait_for(state='attached', timeout=25000)
            except Exception as exc:
                root_children = await page.locator('#root > *').count()
                raise AssertionError(
                    'Production frontend failed to mount: '
                    f'root_children={root_children}, '
                    f'asset_statuses={asset_statuses}, failed_asset_types={failed_assets}, '
                    f'page_error_count={len(page_errors)}'
                ) from exc
            assert any(kind == 'JS' and status == 200 for kind, status in asset_statuses), (
                'production JS was not retrieved', asset_statuses
            )
            assert all(status == 200 for _, status in asset_statuses) and not failed_assets and not page_errors, (
                'production assets failed to load', asset_statuses, failed_assets, len(page_errors)
            )
            print('PASS Chromium built frontend: fingerprinted JS/CSS loaded; React mounted; dev HMR not used')
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(probe())
