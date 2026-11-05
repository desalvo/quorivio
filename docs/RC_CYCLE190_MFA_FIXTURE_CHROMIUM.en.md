# RC190 — Compiled Chromium MFA fixture and cookie modal

## Failed run and cause

GitHub Actions run `42023471301`, job `127231773092`, failed in “Chromium editor UI acceptance” in `ci_rc186_mfa_enter_chromium.py`, before testing Enter. The expected “Informativa cookie funzionali” dialog never rendered. The original RC186 fixture injected compiled React into `about:blank` (opaque origin), where `localStorage`/`sessionStorage` can raise `SecurityError`, but did not mock those browser APIs as the already-green password recovery/preview fixtures did.

## Fix

- Isolated in-memory functional cookies, initially empty; await and acknowledge the actual React cookie notice.
- Independent `localStorage` and `sessionStorage` with `getItem/setItem/removeItem/clear/key/length`, installed **before** injecting the compiled Vite bundle.
- Explicit browser-state preflight and pageerror diagnostics on mount failure; standalone Chromium fixture smoke at 1440/390 px.
- Early Python contract preflight and same-block Chromium smoke **before** the complete built-React MFA test.
- Preserve true Enter submission for TOTP/email/recovery, rapid-submit deduplication and retry after a failed code. No production cookie, consent logic, authentication API or security gate changes.

## Local evidence and limits

`python3 -m unittest tools.tests.test_rc190_mfa_fixture_reconciliation tools.tests.test_rc186_totp_keyboard -q`: **9/9**.

`python3 tools/ci_rc190_mfa_fixture_chromium.py`: **2/2** at 1440x900 and 390x844.

The compiled-React bundle cannot be rebuilt locally because npm registry DNS failed (EAI_AGAIN); only the next GitHub CI will validate the actual MFA form and all downstream gates. Certified readiness remains **85.25%** (43 accepted, 17 partial). No assistant commit, push, tag or image publication.
