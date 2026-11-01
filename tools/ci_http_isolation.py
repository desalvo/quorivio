"""Guard the CI-only load-token header used by disposable loopback HTTP suites.

The server accepts this header only outside NODE_ENV=production. It is never
an authentication credential and must never be sent to a nonlocal host.
"""
from __future__ import annotations

import os
from urllib.parse import urlsplit


def ci_load_headers(base_url: str) -> dict[str, str]:
    """Require a strong ephemeral token and strict loopback URL before any request."""
    parsed = urlsplit(base_url)
    if (parsed.scheme != 'http' or parsed.hostname not in ('localhost', '127.0.0.1')
            or parsed.port is None or parsed.username or parsed.password
            or parsed.path not in ('', '/') or parsed.query or parsed.fragment):
        raise RuntimeError('CI HTTP acceptance requires a disposable loopback URL')
    token = os.environ.get('QUORIVIO_CI_LOAD_TOKEN', '')
    if not (32 <= len(token) <= 256) or any(ord(c) < 33 or ord(c) > 126 for c in token):
        raise RuntimeError('CI HTTP acceptance requires a strong ephemeral load token')
    return {'X-Quorivio-Load-Token': token}
