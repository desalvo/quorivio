# Quorivio 0.1.0-dev — RC251 — Preserve public native-size touch targets

**Baseline:** original RC250 cumulative (`f4c83c2316f39554cac75868bdc906b647c8a151940cc26a37488e398a6f2eec`, 68,381,628 bytes) retrieved from Dropbox and verified before making changes. All historical inventories, including RC250, are preserved byte-for-byte.

**CI failure:** GitHub [42412981696](https://github.com/desalvo/quorivio/actions/runs/42412981696), commit `63e877449bb4821be14292f3f4cf8cc8770922a0`, failed `tools/ci_browser_participant.py` with `AssertionError: RC207 44px answer targets shrank`. Root-level studio CSS zoom at 80% reduced nominal 44px answer rows to 35.2 physical pixels on real joined participants.

**Fix:** The compact persisted zoom continues to control dashboard, page editor and slide-master editor. Public `/join/*` and `/screen/*` routes are rendered at native 100% document zoom independent of stored studio preferences. Studio zoom buttons are hidden on those public routes without changing the stored preference. No slide data or canvas dimensions were altered.

**Validation:** Node tests of route/zoom selection; fail-closed Python source and CI checks; independent Chromium physical `getBoundingClientRect` baseline/fixed comparison at two viewport widths. Original real React+PostgreSQL participant browser acceptance, editor tests and all historical integrity receipts remain mandatory. A new GitHub full CI is required before any RC acceptance claim.

**Status:** **85.25%** (43 accepted, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag or Docker publication. The maintainer may run CI by committing with `[full-ci]`.
