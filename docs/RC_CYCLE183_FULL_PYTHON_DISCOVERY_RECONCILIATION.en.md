# Quorivio 0.1.0-dev — RC183: full Python discovery CI reconciliation

## GitHub diagnosis

Run `41952294082` (commit `95ab635b6c856dadb4653a835013e7973199df4b`, production quality job `126998827097`) passed the earlier dependency preflights, compilation, Chromium editor and public/real PostgreSQL acceptance, then reached the **Kubernetes wizard and worker integration tests** step. The entire Python unittest discovery finished **1,948 tests in 44.102 seconds** with four failures. These were stale source-string assertions in three historical Python modules (RC139, RC141 and public stage 20261028), unrelated to failing Kubernetes provisioning:

- RC139 expected the older inline `['rating','reactions','results-button']` title mask; the actual shared `RatingStageContent` and `widgetTitleVisible()` policy now suppress duplicate edit headings while preserving author intent.
- RC141 expected that same inline mask rather than shared reaction content and title visibility in editor/preview/live.
- Public-stage tests assumed the former two-mode `aria-pressed` expression and automatic viewport-triggered phone mode; RC176+ has three explicit, independent modes. The other test expected direct `backgroundAssetId` string interpolation; RC173+ uses `slideBackgroundCss()` and activity-scoped `/api/join/.../activities/.../media/...` access.

## Repair and regression prevention

Updated the three legacy modules to assert current behavior rather than retired spelling. Added `test_rc183_projection_contract_reconciliation.py` with independent policy checks and deliberate negative mutations for title duplication, mode confusion, result-privacy filtering and media URL scoping. A new **dependency-free early CI step** runs all three old modules plus the new mutation guards, preventing a late failure after PostgreSQL/Chromium. No runtime application logic, credentials or user data changed.

## Acceptance boundary

The earlier GitHub CI had already passed the expensive authenticated browser and PostgreSQL sequence through the late Python discovery step. Only a new full post-commit CI can prove RC183 end-to-end acceptance. Keep the certified score **85.25% (43 accepted / 17 partial)** and flags `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag/deploy.
