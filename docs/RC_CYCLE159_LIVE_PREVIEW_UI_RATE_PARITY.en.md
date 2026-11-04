# Quorivio RC159 — Session controls, rating, rate budgets and live/preview parity

Status: local changes requiring full CI verification; no automatic commit or publication.

## Verified GitHub baseline

- Run 41730792802 against RC157 (`a1155ac`): **success**, including quality, browser, Kubernetes, Podman, native OCI and full RC campaign jobs.
- Run 41739841860 against the same RC157 commit: **success**, including container build, AMD64/ARM64 OCI and **multiarch Docker Hub publication**.
- RC159 retains RC158's preventive Chromium/Playwright manual-workflow fix.

## RC159 changes

- Dashboard **Terminate red**, **Pause light green**, **Reset to not started light blue**; text contrast preserved.
- Optional **rating comment** appears with white background/dark foreground in author canvas and read-only previews; editable in real participant voting.
- Submit button label is exactly **Invia risposta**.
- Authenticated presenter GET and navigation requests have independent shared PostgreSQL rate buckets (360 and 180 per minute respectively); sensitive/default requests retain 100/minute, fail closed and no production bypass.
- Public participant opens in **authored 16:9 slide view** by default, not auto-selected accessible/phone mode, and no longer inherits the 640px login form width. An accessible reading alternative remains opt-in.
- Removed an out-of-canvas, duplicate participant page title. Shared preview rendering and saved master-title typography now cover title/footer/text/notes/graphics, while live interactive controls keep participant endpoints.
- Fixed real presenter title font being overridden by `.projection h2` instead of the authored canvas-relative size.
- Public stage now also uses saved background color/URL when no background asset exists.
- Updated the RC131 historical check to validate the correct master-aware font expression rather than an obsolete literal.

## Verification limits

- Locally passed 586 API Node and 255 web Node tests; targeted RC159/RC131 Python contracts and negative mutations.
- Actual Chromium CSS fixture at 1440/390px passed: 16:9 stage, 8%/3% title coordinates, authored font scaling and session/rating contrast.
- Full TypeScript/Vite build, authenticated production page screenshot comparison, full new GitHub CI and real 500-participant load test remain **pending**. Fixture tests are not a production validation.
- Certified readiness remains 85.25% (43 accepted / 17 partial) until further acceptance evidence.
