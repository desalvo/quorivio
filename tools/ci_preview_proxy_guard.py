#!/usr/bin/env python3
"""Fail closed if the isolated compiled-browser preview forwards live traffic
into an unavailable API. Check the **captured preview server log**, not only
Playwright page errors; a Vite WS proxy rejection does not throw pageerror.

The CI preview is deliberately offline. Real /live connectivity has dedicated
PostgreSQL/WebSocket acceptance. This check must not be used to waive those.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

# Include both OS socket rejections and Vite/HTTP proxy errors. These are
# intentionally checked even if Chromium interactions otherwise pass.
# Vite colours the startup banner (including "Local" and its punctuation).
# GitHub runners capture the ANSI SGR sequences verbatim; normalize only for
# comparison, never alter the raw log in the diagnostic artifact.
ANSI_SEQUENCE = re.compile(r"\x1b(?:\[[0-?]*[ -/]*[@-~]|\][^\x07]*(?:\x07|\x1b\\))")

UNEXPECTED_PROXY = re.compile(
    r"ECONNREFUSED|\bEHOSTUNREACH\b|\bENETUNREACH\b|\[vite\].*(?:ws )?proxy error|\bproxy error:",
    flags=re.IGNORECASE,
)


def verify_preview_log(content: str) -> int:
    normalized = ANSI_SEQUENCE.sub('', content)
    matches = [line for line in normalized.splitlines() if UNEXPECTED_PROXY.search(line)]
    if matches:
        raise RuntimeError(
            f"offline compiled-preview emitted {len(matches)} upstream/proxy "
            "failure log lines; Chromium UI acceptance must fail closed"
        )
    # Require the actual loopback preview banner, but tolerate ANSI styles
    # inserted inside the URL or between `Local` and its colon.
    if not re.search(r"\bLocal:\s*http://127\.0\.0\.1:5173/", normalized):
        raise RuntimeError("compiled-preview readiness evidence is absent")
    return len(content.splitlines())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    lines = verify_preview_log(args.log.read_text(encoding='utf-8', errors='replace'))
    print(f'PASS compiled-preview upstream/proxy log guard: {lines} log lines, no hidden failures')


if __name__ == '__main__':
    main()
