#!/usr/bin/env python3
"""Use the Chromium/Chrome already present on a GitHub Ubuntu runner.

This preflight intentionally never invokes apt, installs OS packages, or downloads
browsers. Ubuntu 24.04 GitHub-hosted runners ship with Chromium and Google Chrome;
installing them again in an eight-minute UI gate can block in apt mirrors.

Export QUORIVIO_CHROMIUM_PATH so every editor, presenter and participant browser
acceptance test uses the *same* validated executable. Fail closed if unavailable.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess

CANDIDATES = ('chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable')


def installed_browser() -> Path:
    """Find an executable Chromium-family browser, no install/network fallback."""
    options = [shutil.which(name) for name in CANDIDATES]
    options += [os.environ.get('CHROME_BIN'), '/usr/bin/chromium', '/usr/bin/google-chrome']
    for path in options:
        if not path:
            continue
        exe = Path(path)
        if not exe.is_file() or not os.access(exe, os.X_OK):
            continue
        try:
            p = subprocess.run((str(exe), '--version'), check=True, timeout=8,
                               capture_output=True, text=True)
        except (OSError, subprocess.SubprocessError):
            continue
        version = (p.stdout or p.stderr).strip()
        if not any(v in version.lower() for v in ('chromium', 'chrome')):
            continue
        print(f'Browser preinstalled: {exe} ({version})', flush=True)
        return exe.absolute()
    raise RuntimeError(
        'Chromium/Google Chrome not found on the runner. Use the Ubuntu 24.04 '
        'GitHub-hosted image (which preinstalls a browser). Refusing apt '
        'installation: previous Chromium gate timed out downloading dependencies.'
    )


def probe_playwright(path: Path) -> None:
    """Check that the installed executable works with the selected Playwright."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=str(path), headless=True, args=['--no-sandbox'])
        try:
            page = browser.new_page()
            page.set_content('<main id="probe">Quorivio browser acceptance</main>')
            assert page.locator('main#probe').inner_text() == 'Quorivio browser acceptance'
            assert page.evaluate('1 + 1') == 2
            print('PASS preinstalled Chromium/Chrome Playwright headless smoke', flush=True)
        finally:
            browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--github-env', type=Path, help='Append the validated browser path to GITHUB_ENV')
    parser.add_argument('--smoke', action='store_true', help='Exercise a real Playwright browser launch')
    args = parser.parse_args()
    path = installed_browser()
    if args.smoke:
        probe_playwright(path)
    if args.github_env:
        # GITHUB_ENV is supplied by the job; the value is a single absolute path.
        with args.github_env.open('a', encoding='utf-8') as handle:
            handle.write(f'QUORIVIO_CHROMIUM_PATH={path}\n')
    print(f'PASS browser preflight: {path}', flush=True)


if __name__ == '__main__':
    main()
