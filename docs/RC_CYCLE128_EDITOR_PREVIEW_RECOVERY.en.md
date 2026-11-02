# RC128 — Editor, rehearsal geometry, reload recovery and collision boundary

Date: 2026-11-02. Base: RC127 cumulative. Screenshot-driven regression repairs without external operator approvals.

## Symptoms and source correction

- **Incorrect text below the presenter rehearsal question**: the old presenter-only branch placed simulated answer rows over the question input area. Presenter and participant rehearsals now use the *same* question layout: label, answer controls and submit button. The presenter sees controls disabled, with no real submission; aggregated simulated answers remain only in linked `results-button` widgets.
- **Dual preview sizes and text style**: preview widgets preserve editor percentages for x/y/width/height and authored typography and shape styles. Font and answer control dimensions use the 1280-wide stage-relative `cqw` rather than different absolute pixels on large and split stages. Title and footer inherit widget font family, weight, size, colour and text formatting instead of default browser heading/footer styles.
- **Free-text answer control**: the editor now has a separate drag handle on each answer box to change its height within validated limits, 48–400 design-space px; saved `style.answerFieldHeight` is used by the editor, rehearsal and live audience control. This is independent of widget frame resizing.
- **Top ruler**: correct grid placement and overflow rules so the horizontal ruler is not cropped by the previous editor wrapper.
- **Browser reload**: only a non-sensitive, per-tab workspace location (selected session, dashboard section/tab and page ID) is stored in `sessionStorage` and restored after authentication and successful server session lookup. It stores no tokens, answers or unsaved drafts. Invalid, forbidden or deleted sessions reset safely to the workspace; explicit logout clears the state.
- **Drag collision**: move a selected widget group toward the pointer along a continuous path, stopping at the first blocking widget boundary. Prevent passing through thin blockers when the final pointer target is unoccupied. Free graphic overlays keep their overlap allowance; resizing remains subject to existing collision safety.

## Local verification

- `node --experimental-strip-types --test apps/web/test/*.test.ts`: **185/185 passed**.
- `python3 -m unittest tools.tests.test_rc128_rehearsal_parity_contract -q`: **5/5 passed**.
- Regression coverage: fixed position and thin-blocker sweeps, rigid grouped movement, free shapes, storage sanitization and typography coordinate parity; legacy presenter test updated to require disabled presenter submit controls rather than an obsolete presenter-only markup branch.
- TS/JS syntax checked with global TypeScript transpiler; **full npm/Vite compile unavailable locally due npm dependency installation not completing**. Chromium visual screenshots and CI remain pending; no claim of live-environment validation.

## RC safety and release tracking

This cumulative RC128 also preserves all RC127 native OCI runtime gates and its 17-item external-acceptance plan. Certified completion remains **85.25%** (43 accepted, 17 partial out of 60), provisional engineering estimate 85.75%, without invented approvals. Full RC remains **not accepted**. On the next CI use `[full-ci]`, not `[publish-docker]`; keep `publish_image=false`, `publish_latest=false`, `rc_strict=false`. No commit/push/release by assistant.

Cumulative commit suggestion since the last confirmed RC126 commit: `Add native OCI runtime gates and fix editor-preview parity, reload recovery and collision boundaries [full-ci]`.
