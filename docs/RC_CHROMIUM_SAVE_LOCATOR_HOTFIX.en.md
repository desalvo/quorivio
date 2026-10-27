# Chromium exact Save-locator acceptance hotfix (2026-10-27)

## Confirmed GitHub failure

- Full GitHub run: 40479089027; quality job: 122104572150; commit: `238e184e16b658fa97f9ef57de5c3e352ce05615`.
- Browser bootstrap and actual desktop/mobile contextual CSS preflight PASSED.
- Browser fixture failed at `tools/ci_browser_editor.py:190`, **Playwright strict-mode violation**.
- `get_by_role('button', name='Salva layout')` matched both `Salva layout` and `Salva layout della pagina` (icon). This was an ambiguous test selector, not evidence of data loss or broken persistence.

## Changes

- Shared `editor_save_button(page)` scoped to `region=Editor grafico delle pagine`, `name='Salva layout'`, `exact=True`.
- Both mocked browser and real PostgreSQL browser tests use the shared locator for all save clicks and enable/disable checks. No `.first()` and no forced clicks.
- Dedicated real-browser isolated preflight validates deliberate accessible-label collision, exact matching, actual desktop click and mobile touch, and disabled state.
- Python AST/contract tests ensure neither flow reintroduces the ambiguous selector, and check CI executes the preflight before full editor acceptance.
- No production React, API, DB, Docker or publication changes.

## Gates

Full mocked frontend+Chromium and PostgreSQL-backed Chromium journeys require a **new opt-in GitHub run**. The isolated Chromium fixture proves only the strict locator behavior, not overall application health. No RC gate promotion.
