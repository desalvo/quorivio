# RC146 — CI release-header consistency hotfix

## Root cause

GitHub Actions run [41674561888](https://github.com/desalvo/quorivio/actions/runs/41674561888), push commit `04b124a381cc63a54ad1a584144ba7479a5aa706`, failed in **Production quality gate**, at `Validate active RC release headers against the current inventory`. The active inventory was RC145 but `docs/COMPLETION_HANDOFF.md` still began with RC144 and `docs/COMPLETION_HANDOFF.it.md` with RC143. CI stopped before dependency installation, TypeScript compilation, Node tests, PostgreSQL acceptance or Docker publication. Real ClamAV acceptance passed independently; final RC campaign summary failed downstream because a required job failed.

## Correction

- Update all four active status/handoff headings to RC146 and preserve historical sections as-is.
- Keep the original RC145 inventory immutable. Record RC146 as a new cumulative receipt, and mark RC145 as historical in the CI workflow.
- Add `tools.tests.test_rc146_release_header_fix` to verify active headings, flags, localized percentages and current workflow references.
- No runtime code changes: all RC145 phone-background and Arial fixes remain included.

## Validation and gate

Run `python3 -m unittest tools.tests.test_rc_cycle100_release_status_guard tools.tests.test_rc146_release_header_fix -q`, `python3 tools/ci_inventory_reference_guard.py`, `python3 tools/verify_rc_release_status.py` and `python3 tools/verify_rc_cycle146_inventory.py` after the new manifest is produced. Run full CI on a user commit before considering Docker publication or formal RC promotion. Certified 85.25% (43 accepted/17 partial) unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

Suggested one-line commit after last RC145 commit: `Fix RC146 release headers and CI inventory continuity [full-ci]`.
