# RC106 — Chrome preview WS fail-closed and page-settings portal contract

**Run inspected:** GitHub Actions `41305315027`, push commit `454eaf729c9487146f2c89a47178a64161d5683b`, quality gate failed. Its downstream campaign summary failure followed the main gate failure.

## Independent causes

1. The Python `test_page_context_not_ribbon` demanded the historical `pageContextOpen&&<section className="editor-context-drawer"` structure. The page settings are now correctly wrapped in `EditorFloatingWindow portal placement="page"`. Tests now assert the actual draggable viewport-floating portal, and reject the old inline section.
2. During the **offline built-bundle Chromium** step, Vite preview inherited `/live` WebSocket proxy settings targeting `localhost:8080`, but the real API starts only in the subsequent PostgreSQL stage. The Vite server wrote `AggregateError [ECONNREFUSED]` messages without Playwright `pageerror`, so Chromium continued successfully. We no longer ignore such infrastructure errors.

## Fix and security

- `apps/web/vite.config.ts`: preserve `server.proxy` for local integrated development; explicitly use `preview.proxy={}` for disconnected built-frontend acceptance. Chromium route fixtures must not require a real backend, while live/PostgreSQL integration remains a separate mandatory gate.
- `.github/workflows/ci.yml`: `cleanup_preview` trap always invokes `ci_preview_proxy_guard.py` (including after test failure/early exit), then shuts down preview; failures propagate.
- `tools/ci_preview_proxy_guard.py`: fail on `ECONNREFUSED`, `EHOSTUNREACH`, `ENETUNREACH`, and Vite/HTTP proxy errors; require actual preview startup evidence. Print counts only, not private URLs or credentials.
- Updated source contract + new negative tests ensure future editor refactors cannot silently break the CI again.

## Residual risk

New push `[full-ci]` is required for production bundle, real Chromium end-to-end, API WebSocket connectivity under PostgreSQL, Kubernetes and cross-browser confirmation. This correction does not certify independent audits, production networks, or physical devices. No gate advance or Docker publication.
