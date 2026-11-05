# Quorivio 0.1.0-dev — RC186 — Enter-to-submit TOTP challenge

## Implementation

The second-factor challenge is now a native HTML `<form>` with React `onSubmit`. With focus in **Authenticator code**, **Enter** sends a six-digit TOTP to the exact same verification function as the existing **Verify** button. No pointer interaction is required.

The shared form also allows Enter for email MFA and recovery codes. Method selection, switching to recovery and cancelling remain explicit `type="button"`; the Verify control is the sole `type="submit"`. A synchronous `useRef` guard and busy state block repeated Enter/click MFA verification requests. Invalid-length codes cannot submit. A rejected code leaves the form interactive for retries. No server auth or TOTP cryptography changes.

## Verification

- Early Python source contracts and negative mutation guards enforce form semantics, explicit control types, validation and duplicate protection.
- A production-React Chromium fixture runs **after the Vite build** in CI at 1440 and 390 px: Enter, incomplete TOTP, rapid repeat, rejected code and retry, email MFA, recovery codes and the legacy Verify button.
- The browser fixture uses disposable mocked HTTP; it does not certify a physical authenticator or SMTP provider.

## Baseline and release safety

RC185 is the cumulative development baseline (dual projection pending fresh CI); the last independently checked fully green GitHub campaign is RC184 run `41993094578`. No changes to databases or presentations. No assistant commits, pushes, tags or deployments. Certified completion **85.25%** (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
