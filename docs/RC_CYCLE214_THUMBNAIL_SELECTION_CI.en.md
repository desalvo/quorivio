# RC214 — Selection-aware thumbnail CI contracts and Escape focus recovery

## GitHub diagnosis
Run `42142002249`, production gate job `127644319112`, failed at `RC106 isolated compiled-preview and floating portal contracts` because the historical `test_editor_contextual_layout_v2.py` still required the pre-RC206 `onClick={()=>beginPageDesign(a)}` literal. RC206 intentionally replaced it with a click handler that distinguishes normal navigation from Ctrl/Cmd multi-selection. ClamAV passed and downstream jobs skipped. RC213 frontend TypeScript stage passed in this run.

## Reconciliation and corrections
Updated three historical source tests: contextual editor, thumbnail keyboard reordering, and page editor follow-up. They now check normal click opening, Ctrl/Cmd selection without navigation, D/R/Backspace shortcuts, Alt+Arrow ordering, closed-session restrictions, dynamic multi-page action labels and accessible state. Fixed a genuine keyboard focus regression: Escape now captures the thumbnail menu trigger *before* unmounting the portalled menu, and restores focus afterwards. New RC214 fail-closed test includes negative mutations that break modifier handling, navigation, accessible selection, or Escape focus; registered in an early pre-npm quality gate. Existing multi-page business logic is unchanged.

## Release and safety
Version `0.1.0-dev`; **85.25%** certified (43 accepted / 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full cumulative from RC213, grouped per-file SHA-256 inventory and 201 historical/current CI verifier references. GitHub full RC214 CI and complete integrated frontend compile still pending; last full green is RC203 `42110429701`. No assistant commit/push/tag.
