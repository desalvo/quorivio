# RC — accessible rehearsal background isolation and profile subgate (28 October 2026)

**Baseline:** Quorivio `0.1.0-dev`; last user-confirmed commit `a32ef78902a656262d346a0fa622604a4deda405`. The 60.0% cumulative package is **not yet committed**; do not commit, push, tag or publish images automatically.

## Product changes

- Presenter, participant and side-by-side rehearsals share the same dialog. `apps/web/src/rehearsal-dialog.ts` now applies reversible **inert** and `aria-hidden=true` isolation to all background sibling branches along the path from the modal to the body. The dialog itself remains interactive. Cleanup restores original values of `aria-hidden`, including explicit `false`, and prior `inert`, as well as focus and scroll locking.
- `tools/ci_rehearsal_keyboard_chromium.py` checks the actual compiled TypeScript helper in real Chromium at 1440×900 and 390×844: accessibility visibility, focus, cycling Tab, Escape, IME, original invoker and prior background properties.
- The opt-in `tools/ci_browser_editor.py` test now opens **side-by-side rehearsal** from the real editor with an API fixture and validates two 16:9 slides, relative widget geometry, switching to participant and back, Escape and restoring editor interaction. No force clicks.

## RC score — 61.0% (+1 percentage point)

Only **previously verified green GitHub Full CI** runs `40638652838` and `40595463258` support the bounded C4 split: `C4-PROFILE` (weight 2/100, **accepted** from real Chromium + PostgreSQL profile/photo/privacy/erasure tests) versus remaining C4 (weight 3/100, **partial** pending real multi-replica RWX/ClamAV, physical devices and independent assistive technologies). The original scoring rule (accepted=100%, partial=50%) yields **61.0%** versus 60.0%; 26 gates, 9 accepted and 17 partial. **No points for the new rehearsal behavior** before a new successful Full CI.

The **strict RC gate remains blocked**. The local Chromium sandbox cannot access localhost (`ERR_BLOCKED_BY_ADMINISTRATOR`), so the complete authenticated-app browser test is included but **not locally executed**. Offline browser tests do not substitute independent screen-reader and physical-device acceptance. Rerun opt-in GitHub Full CI with `browser_test=true`, `publish_image=false`.

See `docs/validation/RC_REHEARSAL_BACKGROUND_ISOLATION_PROFILE_CI_20261028.json` and `docs/RC_GATE_MATRIX.json`.
