# Quorivio 0.1.0-dev — RC167 — Live/preview parity and safe browser evidence

## Verified baseline

GitHub Actions run **41808754419**, RC166 commit `7138cecc2260`, completed successfully, including the full automatic RC campaign and AMD64/ARM64 Docker Hub publication. The operator marked the GitGuardian “Generic Password” incident **ignore**. This is an administrative disposition, not proof the finding was false or that the repository has no other secrets. Security scanners remain enabled.

## Application corrections

1. `apps/web/src/live-slide-policy.ts` centralizes the title policy for editing, rehearsal and real projection, the opt-in QR title and the participant-visible widget catalog.
2. Line and Shape widgets render **SVG only**, even if legacy records include a caption and `showTitle: true`; the live participant used to show such labels while previews did not.
3. Presenter-only Results and Connected Participant Count widgets are excluded entirely from the public DOM, not rendered as empty overlapping widget shells. Presenter projection retains both.
4. The mobile layout, authored widget positions, slide-master inheritance, QR URL and existing question interactions are preserved.

## Real browser / PostgreSQL acceptance

The disposable browser fixture now authors Title, Question, Topic Question, legacy-caption Line, legacy-caption Shape, Results and Participant Count. Chromium desktop (1366 px) and mobile (390 px) assert SVG visibility, caption absence and no presenter-only widget shells. Existing independent participants, PostgreSQL answer persistence, reload, idempotency, topic question privacy, QR and session revocation checks remain in place.

## Hardened diagnostic artifacts

- The browser fixture accepts only parsed loopback HTTP origins with an explicit port. Credential-bearing origin confusion, non-root paths, query strings and external hosts are rejected before mutating the CI session.
- Failure evidence contains no raw `/join/<secret>` URLs, complete authenticated HTML, response payloads or raw browser errors. It retains only a screenshot with QR content masked and aggregate error counts.
- Deterministic positive/negative regression checks run before npm in CI. No scanner or acceptance gate was disabled.

## Remaining acceptance

Certified completion is **85.25%** (43 accepted, 17 partial gates), with `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Independent live visual comparison, real mobile devices, and human review are still required for A3 certification. GitHub CI on RC167 and a deployed authenticated E2E check remain pending. No commit, push, tag or deployment was performed.
