# Quorivio 0.1.0-dev — RC 53 — production Content Security Policy and browser permissions (30 October 2026)

**Baseline:** cycle 52 cumulative, no maintainer commit since `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`. This package includes cycles 49–53. **Certified RC remains 81.25%**: security approval requires real GitHub runtime acceptance and independent review.

## Product changes

`apps/api/src/security-headers.ts` defines an enforcing production CSP (only when `NODE_ENV=production`), disallowing inline/eval scripts and executable objects, binding WebSocket endpoints to the configured browser-facing origin, and retaining same-origin frames required for presenter/rehearsal previews. Image/media schemes preserve local uploads, QR/data images, optional HTTPS background media, PDFs and blob resources. Widget-specific React inline CSS remains explicitly allowed; no relaxation is made to script execution. `Permissions-Policy` disables camera, microphone, location, payment, USB and browsing-topics but leaves presenter fullscreen unaffected. The Vite development server does not use this production policy.

## Verification

Five Node tests enforce policy boundaries and URL validation; four Python contracts cover API integration, unsafe-script denial, media compatibility, and real-container smoke checks. Both `ci_oci_runtime_smoke.sh` and `ci_rootless_podman_smoke.sh` now **fail closed** unless a running production container actually serves both headers. Existing backend/frontend Node tests must remain green; GitHub container gates, real browser integration and external security sign-off **have not yet been run** for this change.

The `81.25%` certified RC score is unchanged; B4 HTTPS KIND, B4 global 500-user SLO, external RWX and D4/D6 independent approvals remain pending. Recommend standard CI first, extended OCI+Podman+browser tests next, with `publish_image=false` and `rc_strict=false`.
