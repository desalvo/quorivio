# Quorivio 0.1.0-dev — RC177: reconcile historical live presentation CI contracts

GitHub Actions run 41865155281, job 126697411992 (2026-11-04) first fails in `tools.tests.test_rc167_live_preview_fidelity`, `test_shared_policy_is_used_in_all_projection_surfaces`. RC167 expected the legacy two-way phone/desktop selector while RC176 uses three separate modes (phone, accessible reading, faithful 16:9). The job has not identified a new rendering regression: its literal contract is stale.

Reconciled RC144/167/168/169 with the current three-mode selection. RC168/169 also demanded the old 1174px PostgreSQL fixture height, while RC176 calculates 998px from public widgets after excluding presenter-only elements. Kept negative guards on privacy, QR, decorative graphics and redacted browser diagnostics. Added RC177 negative regression and early CI preflight before npm installation. All pre-RC177 source inventories remain immutable; RC177 establishes a new cumulative source SHA-256 inventory.

Local evidence: 65 focused tests passed; an initial 579-test preflight sweep found only four expected checksum errors before the new inventory was generated. After generating the RC177 receipt, **589 preflight tests** (no failures, one skipped), **313/313 web tests** and **588/588 API tests** passed. Release headers and the 1770-member cumulative ZIP checksum inventory were also verified.

**Global gates:** certified 85.25% (43 accepted, 17 partial); this fix alone earns no additional gate credit. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/deploy. npm/Vite build, authenticated Chromium/PostgreSQL end-to-end and post-commit GitHub CI remain pending.
