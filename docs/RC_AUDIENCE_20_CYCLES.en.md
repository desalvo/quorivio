# Quorivio 0.1.0-dev — 20-intervention audience journey batch

**User-confirmed committed baseline:** `quorivio-0.1.0-dev-editor-20-cycle-rc-evidence-cumulative.zip`. GitHub workflow `40143475939`: quality and container build SUCCESS, publication SKIPPED. Expanded editor Chromium passed in that run; 500-participant opt-in passed previously in `40141894130`.

## 20 delivered interventions

1. Safe typed session-code normalization with uppercase hexadecimal codes.
2. Paste full QR join URLs while preserving case-sensitive join secrets.
3. Reject malformed URL segments and invalid percent encoding.
4. Explicit public session loading state.
5. Unavailable-session error with retry and new-code navigation.
6. HttpOnly-cookie participation recovery API (`GET /api/join/:code/participation`).
7. Boolean-only private, non-cacheable recovery response; no token or pseudonym.
8. Honor anonymous-participation revocation during recovery.
9. Recover participation before showing the join form after reload.
10. Guard concurrent join requests; normalize pseudonym after functional-cookie consent.
11. Prevent concurrent/duplicate UI vote requests.
12. Validate required single/multiple/text/file inputs client-side, retaining server authority.
13. Accessible pressed-state answer buttons, labelled choice group, live confirmation.
14. Skip-to-main navigation and keyboard focus styling.
15. Reflow absolutely positioned audience widgets into a readable mobile stack.
16. Minimum 44px participant targets and forced-colors support.
17. Bounded WebSocket retry/backoff and online/offline awareness, stopping permanent retries.
18. Published-page pointer and active-session guards; server-controlled live-result disclosure.
19. New opt-in Chromium **against real PostgreSQL and the built production frontend**: two independent browser cookie jars, QR/short code, votes, privacy, idempotency, reload and mobile.
20. Expanded real PostgreSQL HTTP cookie-recovery/closure assertions, CI failure artifacts, Node/Python regressions and bilingual documentation.

## Verification and acceptance limits

- Local: **215/215 Node**, **282/282 Python**, backend TypeScript and frontend TypeScript/Vite production builds **PASS**.
- Local Chromium cannot reach localhost (`net::ERR_BLOCKED_BY_ADMINISTRATOR`); the **new** browser/PostgreSQL acceptance has not run in GitHub CI.
- Prior workflow `40143475939` quality/container SUCCESS; earlier `40141894130` 500-participant PASS. Neither proves production-grade capacity/SLA.
- A1 and B4 remain **partial**, A4 remains **open**. Screen-reader/device-lab and sustained staging acceptance are still required.
- Weighted RC score remains **45.5/100** until the new opt-in browser run is verified.
- No assistant-side commit, push, tag, release or deployment.

## Next gate

Commit the single cumulative package and dispatch with `browser_test=true`. The new Chromium participant step runs against `127.0.0.1:8080` (same-origin production build and real PostgreSQL 18), uploading `chromium-participant-failure` on failure for three days. Repeating the previously passing 500-participant opt-in is optional for this code change.
