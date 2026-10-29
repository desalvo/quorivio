# RC cycle 11 — recovery fragment links, accessible preview focus and immutable inventories

**Quorivio 0.1.0-dev / EUPL-1.2 / 29 October 2026**

## What changed

- New single-use password reset emails use an HTTPS URL fragment `#reset_token=…` (a token is not sent in the HTTP request target). The React application removes the fragment with `history.replaceState` before normal navigation and keeps the bearer only in component state. Legacy email URLs using a query parameter continue to work and both query/fragment bearer components are erased.
- The loopback PostgreSQL 18/TLS-SMTP fixture checks fragment-only issuance, without weakening real server token expiration, hashing, single use or revocation assertions. HTTP is allowed only for loopback disposable CI; non-loopback links must use HTTPS. This fixture has **not yet run in GitHub CI for these changes**.
- `activateRehearsalDialog` now traps focus changes made by scripts or assistive interaction as well as keyboard Tab. It restores original focus and aria/inert values when closed. Only automated Chromium verification is available; independent screen-reader certification remains outstanding.
- Historical SHA-256 cycle-10 manifests remain untouched. Decoding/format checks are always valid; verifying **current** source requires the separate cycle-11 manifest. The CI validates both appropriately.

## Boundaries

Local TypeScript/Vite and Node, Python, Chromium pass. No locally available PostgreSQL 18 service or independent Firefox/WebKit/physical-device/operator/legal review. **Do not mark any of the 17 residual partial RC gates accepted** solely from this uncommitted batch. The last verified green remote run is GitHub Actions `40717525524` on the earlier commit `f6738592c648bc620e01b92d2bbaa6b90b459287`.

**Score: 74.0% (unchanged), 40 gates, 23 accepted, 17 partial.** Strict RC is blocked.

After the maintainer commits, run Full CI manually with `browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`. Confirm PostgreSQL/SMTPS real link acceptance and Chromium gates before reconciling evidence. No automatic git or Docker action was taken.
