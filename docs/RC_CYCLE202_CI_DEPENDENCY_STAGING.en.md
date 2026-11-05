# RC202 — Keep optional PowerPoint dependencies after installation

## Root cause

GitHub Actions run `42105427044`, Production quality gate job `127518865236`, failed at `Validate active RC release headers against the current inventory`, though the four active status headers and historical inventories were valid. After three successful release-header tests, `tools.tests.test_rc200_editor_portability` failed because `python-pptx` and Pillow were not installed yet. The workflow intentionally installs Python conversion dependencies later, prior to native export fidelity and the complete Python suite.

## Change

- Retain the four dependency-free RC200 source/API/UI assertions in `RC200EditorPortability` and run them early.
- Move the two actual native image/PPTX fidelity tests to a separate `RC200NativePowerPointPortability` class and run explicitly *after* installation and fail-closed import checks for `pptx`, `PIL`, and `aiohttp`. These same tests remain in full `unittest discover`.
- Add `tools.tests.test_rc202_dependency_staging` to early CI to reject inadvertent reintroduction of native cases into the no-dependency phase.
- Preserve the historical RC97 staging preflight and all prior manifest receipts unchanged.

No application/runtime, schema, OAuth, public QR/URL rotation, Docker-publish, or strict release semantics changed. `rc_strict=false`, `publish_image=false`, `publish_latest=false` remain unchanged. No assistant commit/push/tag.

## Validation & handoff

Local pure-source RC200, native PPTX RC200, legacy RC97 and RC202 staging tests passed. The full GitHub CI of RC202 must still verify the entire chain: early preflight → npm/TypeScript → install Python conversion dependencies → native PPTX → complete Python suite → Chromium/PostgreSQL → Kubernetes/OCI. Last fully green RC199 run `42096705867`. Certified completion 85.25% (43 accepted, 17 partial), unchanged.
