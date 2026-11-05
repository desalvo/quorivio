#!/usr/bin/env python3
"""Regression for the in-memory MFA browser fixture on about:blank.

No credentials or network are involved. The built-React MFA test exercises
actual submit/retry flows separately, after npm/Vite builds the frontend.
"""
from __future__ import annotations

import asyncio
import os
from playwright.async_api import async_playwright
from ci_rc186_mfa_enter_chromium import API, HTML


async def verify() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            executable_path=os.getenv('QUORIVIO_CHROMIUM_PATH', '/usr/bin/chromium'),
            headless=True, args=['--no-sandbox'])
        try:
            for width, height in ((1440, 900), (390, 844)):
                context = await browser.new_context(viewport={'width': width, 'height': height})
                page = await context.new_page()
                await page.set_content(HTML)
                await page.evaluate(API)
                result = await page.evaluate('''() => {
                    const before = {
                        cookie: document.cookie,
                        local: localStorage.getItem('quorivio_pseudonym'),
                        session: sessionStorage.getItem('fixture-only')
                    };
                    localStorage.setItem('quorivio_pseudonym', 'participant');
                    sessionStorage.setItem('fixture-only', 'session');
                    document.cookie='q_cookie_notice=ack; Max-Age=31536000; Path=/; SameSite=Lax';
                    const after = {
                        cookie: document.cookie,
                        local: localStorage.getItem('quorivio_pseudonym'),
                        session: sessionStorage.getItem('fixture-only')
                    };
                    return {before, after};
                }''')
                assert result == {
                    'before': {'cookie': '', 'local': None, 'session': None},
                    'after': {'cookie': 'q_cookie_notice=ack', 'local': 'participant', 'session': 'session'}
                }, result
                await context.close()
                print(f'PASS RC190 isolated Chromium {width}px: opaque-origin storage and functional cookie fixture')
        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(verify())
