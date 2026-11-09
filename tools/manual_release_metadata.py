#!/usr/bin/env python3
"""Authoritative, non-secret metadata shared by every published manual.

Do not hardcode the author's contact in six files: resolve the copyright notice
and version from checked-in project sources. CI may add its exact Git commit.
"""
from __future__ import annotations
import json
import os
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CYCLE = 282
PUBLICATION = '2026-11-09'
REPOSITORY = 'https://github.com/desalvo/quorivio'


def metadata(root: Path = ROOT, *, commit: str | None = None) -> dict[str, str]:
    package = json.loads((root / 'package.json').read_text(encoding='utf8'))
    licence = (root / 'LICENSE').read_text(encoding='utf8')
    match = re.search(r'^Copyright \(c\) \d{4} (.+?) <([^<>\s]+@[^<>\s]+)>', licence, re.M)
    spdx = re.search(r'^SPDX-License-Identifier:\s*([A-Za-z0-9.\-]+)', licence, re.M)
    if not match or not spdx:
        raise ValueError('Creator, email or SPDX licence missing in LICENSE')
    sha = commit if commit is not None else os.environ.get('GITHUB_SHA', '')
    if sha and not re.fullmatch('[0-9a-f]{40}', sha):
        raise ValueError('Build commit must be a full 40-digit hexadecimal Git SHA')
    return {
        'name': 'Quorivio', 'version': package['version'],
        'build': f'RC{CYCLE}' + (f' · {sha[:12]}' if sha else ' · commit not recorded'),
        'cycle': f'RC{CYCLE}', 'commit': sha or '', 'published': PUBLICATION,
        'author': match.group(1).strip(), 'email': match.group(2),
        'license': spdx.group(1), 'repository': REPOSITORY,
        'server_platforms': 'Linux containers (amd64 / arm64), Docker / Podman / Kubernetes; external PostgreSQL 18 supported',
        'client_platforms': 'Web: desktop and mobile Chromium, Firefox, Safari/WebKit; OS Windows, macOS, Linux, iOS, Android (browser)',
        'minimums': 'Indicative evaluation sizing: 2 vCPU, 4 GiB RAM, 20 GiB disk + database and media storage; production sizing requires measurements',
    }


def validate_release(md: dict[str, str]) -> None:
    if md['published'] != date.fromisoformat(md['published']).isoformat():
        raise ValueError('Publication date invalid')
    if md['license'] != 'EUPL-1.2':
        raise ValueError('Unexpected licence; update manual publication before proceeding')
    if not (ROOT / 'docs/assets/quorivio-logo.svg').is_file():
        raise ValueError('Official logo unavailable')
