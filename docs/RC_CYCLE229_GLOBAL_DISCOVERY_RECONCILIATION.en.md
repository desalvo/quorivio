# RC229 — Full Python discovery reconciliation and upload diagnostics

## Provenance

After RC227 was committed by the maintainer (`ec9de12e8f7e39cbc90d573bc2758b7fdf034ce2`), GitHub Actions run `42226572219` failed the pre-npm RC225 schema background gallery label. The RC228 cumulativo repairs that immediate failure. An additional local discovery run of the extracted archive (2168 tests) exposed 9 additional failures and 20 errors. Most errors require Git metadata and cannot be evaluated correctly in a ZIP-only working tree; two of the nine failures likewise arise from that same missing-Git context.

## RC229 improvements

- Retained the RC228 historical gallery fix and its three mutation/compatibility regressions.
- Reconciled six historical UI tests with current semantic behavior: page JSON imports now include a descriptive aria-label; QR URLs are accessible safe links rather than plain text spans; smartphone fonts are protected by the more selective `allowScale` rule; background uploads use a shared named-file helper rather than a literal inline fetch; dialog stays open on upload failure.
- Restored actionable, sanitized HTTP/server-error messages for background uploads by applying `backgroundUploadError()` in the shared `uploadNamedFile()` helper only for the `backgrounds` route. Duplicate filename confirmation and fail-closed handling remain in place.
- Corrected the portable converter oversized JSON test to stub PPTX fidelity inspection (independent of the size guard), so it actually reaches and validates the 2 MiB JSON limit instead of failing prematurely on the deliberately fake PPTX fixture.
- Added an early RC229 CI step exercising 101 regression tests to catch stale contracts before npm, PostgreSQL integration, browsers or Kubernetes; no change to publishing or user authentication.

## Evidence and follow-up

- Local RC229 consolidated preflight **101/101** Python tests green, including conversion security tests. Consolidated editor/gallery Python tests **29/29**, web Node **398/398**, API Node **628/628** pass after the fix.
- The 20 inventory errors on the extracted ZIP are not evidence of GitHub CI failures; they arise from Git-dependent checks without `.git`. GitHub integrated CI after the new commit is still necessary. Do not mark full CI successful until GitHub jobs finish.
- Certified **85.25%** (43 accepted, 17 partial), unchanged. Last verified green GitHub full CI RC219 `42197607753`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, tag or image publication. Next suggested commit covers only RC228–229, after the user's RC227 commit.
