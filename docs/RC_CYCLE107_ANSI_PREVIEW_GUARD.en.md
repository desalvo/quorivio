# RC107 — ANSI-aware compiled-preview startup CI fix

GitHub full-CI logs `logs_111954785384.zip`: all Chromium UI acceptance checks succeeded, yet the `EXIT` trap failed with `compiled-preview readiness evidence is absent`. The actual Vite server banner shows `Local` and the loopback URL interleaved with ANSI SGR formatting. The RC106 readiness regex looked for plain `Local: http://` in the raw log and failed incorrectly.

## Change

- Strip ANSI escape codes in the copy used for regex matching; do not alter the original diagnostic log.
- Preserve fail-closed detection of colorized `ECONNREFUSED`, proxy failures and unstarted/wrong-host/wrong-port preview.
- Run RC107 unit regressions early in the quality gate, before npm. Preserve the existing final EXIT-trap check and the real PostgreSQL/WebSocket tests.

## Status

No runtime frontend or API behavior is changed. The fix has local unit and negative tests but still needs GitHub full-CI verification. RC completion remains 85.25%; no Docker publication is authorized or performed.
