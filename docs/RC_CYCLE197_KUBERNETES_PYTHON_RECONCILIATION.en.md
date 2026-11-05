# RC197 — Reconcile the late Kubernetes Python integration contracts

**Version:** Quorivio 0.1.0-dev (unchanged)  
**Date:** 2026-11-05  
**Source:** RC196 cumulative / committed run #297 (`42085779348`, `1a5e9cd9c6b3a0ace506514ea57a0dfe07d31234`).

## GitHub evidence

Run #297 completed with conclusion `failure`. The Production Quality Gate passed the Python pre-npm checks, `603` API Node tests, `345` frontend Node tests and both strict TS compilers. It failed later in the `Kubernetes wizard and worker integration tests` step (`2,024` Python cases, six failures). The failed tests compared source code against pre-RC185 single-page preview and pre-RC194 typography conventions. The ClamAV job succeeded; dependent jobs were skipped.

## RC197 reconciliation

Six historical Python test modules were updated to inspect the **current** behavior rather than stale source strings:

- `test_page_rename_preview_contract_20261027`: the empty-preview title belongs to `viewActivity`, and navigation is over presenter-visible pages.
- `test_rc143_phone_result_ribbon`: mobile layout and background selection belong to `viewActivity`/`viewWidgets` and the independent participant phone layout.
- `test_rc75_typescript_ci`: typed subquestions may include the optional `description` property, while `answerMode`, free text rows and result source properties stay typed.
- `test_rc_presenter_linked_preview_20261028` and `test_rehearsal_send_parity_20261028`: reaction state is keyed by **audienceActivity.id**, not the presenter page.
- `test_visual_parity_rehearsal_20261028`: the shared `widgetTextDefaults(widget.kind,widget.style)` precedes `widgetTypographyStyle`; user-selected fonts remain effective.

A new fail-closed `RC197` test checks the routing, reaction key, source-question type and actual CI ordering. All six legacy modules and the RC197 guard run **before npm**, in addition to their original late-suite execution. Their functional assertions were retained and strengthened where possible; the application code, DB schema, public endpoints, and UI behavior were not changed.

## Local verification and release conditions

- Six historical modules plus RC197 guard: `35/35` Python tests passed.
- API `603/603` and frontend `345/345` Node tests passed.
- The complete Python discovery repeated against the generated RC197 SHA manifest: **2,027 tests run: 2,026 passed, 0 errors/failures, 1 skipped** (82.078 seconds). The first intermediate run without a manifest is not a release result.
- Full integrated PostgreSQL/Chromium/Kubernetes acceptance **must be verified by a new GitHub Actions run**, not inferred from local preflights.

**Governance:** `0.1.0-dev` unchanged; certified completion **85.25%**, 43 accepted and 17 partial; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Last fully green/published reference is RC190 (`42027634427`, `42032833536`). No assistant commit, push or tag.
