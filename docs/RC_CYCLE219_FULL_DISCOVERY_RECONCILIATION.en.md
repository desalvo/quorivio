# RC219 — Python global discovery recovery (English)

## GitHub failure and cause
Run `42194028262` (RC218), `Production quality gate` / `Kubernetes wizard and worker integration tests`, executed `PYTHONPATH=tools python3 -m unittest discover -s tools/tests -v` and reported **2,115 tests: 4 failures, 2 errors**. The other CI gates progressed through Chromium/PostgreSQL before this failure. ClamAV succeeded; image publishing did not run.

Two old test modules imported `verify_thumbnail_click` relatively from `.test_rc214_thumbnail_selection_ci`. Dotted `python -m unittest tools.tests...` resolved these, but `discover -s tools/tests` imports bare names and failed with `ImportError: attempted relative import with no known parent package`. Both now import the shared helper by its absolute `tools.tests...` name.

Four other obsolete string checks referred to before RC205/206: opening the selected thumbnail directly rather than through `beginPageDesign()` (which enforces `confirmPageNavigation()` centrally); footer font/size/color controls labeled individually instead of the shared typography ribbon's `Numero pagina` scope; and two RC198 tests expecting an obsolete two-item boolean array plus separate answer-decorations buttons. Checks now validate the real current behavior: an unsaved-draft fence, shared footer-number style mapping, and independent underline/strikethrough toggles with API boolean validation.

## Changes
- Updated `tools/tests/test_editor_contextual_layout_v2.py` and `test_editor_thumbnail_keyboard_rc.py` to use absolute imports, supporting package and bare-module discovery.
- Reconciled `test_page_editor_unsaved_guard.py`, `test_rc142_editor_clipboard_mobile_footer.py`, and `test_rc_cycle198_answer_decorations.py` with the current UX, while retaining regression assertions.
- Added `tools/tests/test_rc219_full_discovery_contract.py` with both import namespaces, fail-closed source mutation checks, and a check for its own CI integration.
- Added a pre-npm CI step that runs the new contract and each affected historical module *in exact discovery mode*; retained the full `unittest discover` integration stage.
- Preserved all prior SHA-256 manifests and workflow inventory verifiers; new active RC219 inventory, source/package integrity and release metadata guards.

## Validation, limitations and release safety
Targeted tests and exact `unittest discover` modes are locally verified. The entire 2,115-case suite could not be completed locally because a separate integration test stalled; it must run in GitHub CI, as must full Chromium/PostgreSQL/Kubernetes and TypeScript checks. No changes to React runtime, API, PostgreSQL schema, permissions, or Docker image behavior.

Version `0.1.0-dev`; certified completion **85.25%**, unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag.
