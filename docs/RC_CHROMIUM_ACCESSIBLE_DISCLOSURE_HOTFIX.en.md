# RC Chromium accessibility disclosure and overlay hotfix (2026-10-27)

## Evidence

- GitHub workflow run `40510491774`, quality job `122210785185`, commit `a26ce48ea7d90bfdfe06e114398e2971e7846810`, failed in `tools/ci_browser_editor.py:248` during the 390 × 844 mobile/touch acceptance.
- `Locator.click` timed out on `.canvas-accessible-controls > summary`: a disabled **Stessa altezza** button in the open `.canvas-editor-tools` alignment overlay intercepted pointer events. No JavaScript page errors were reported.
- Prior independent real-browser preflights **passed**: nested contextual CSS and the strict Save locator. The failure was not a startup, PostgreSQL, backend, or publishing problem.

## Fix

1. A collapsed `.canvas-accessible-controls` disclosure now creates a local stacking context above the floating arrangement overlay; when expanded, this temporary priority is released so context commands can be reopened.
2. The React `<details>` `onToggle` dismisses the contextual background menu when the alternative keyboard/touch panel is expanded.
3. The mobile browser acceptance now verifies the actual hit target with `document.elementFromPoint` and uses a real touch tap, then checks that the overlay closes and that widget selection and contextual actions remain operational.
4. The real PostgreSQL Chromium editor acceptance closes the contextual arrangement overlay before expanding its accessible panel (two call sites).
5. Mandatory Chromium CI preflight `tools/ci_accessible_disclosure_chromium.py` reproduces a deliberate overlap with the **production CSS** in mobile/touch and desktop contexts. It verifies a normal hit target, disclosure, checkbox, overlay dismissal and re-entry into the context menu. No `force=True` or bypasses.

## Local evidence / remaining gates

- Regression reproduction using the previous CSS: **FAIL as expected** (`Canvas overlay intercepts pointer ...`). With the fixed stylesheet: **PASS** both desktop/mobile cases using `/usr/bin/chromium`.
- `tools/ci_nested_context_css_chromium.py`: PASS desktop/mobile.
- Python focused 182/182 PASS, six new regressions PASS; Node 447/447 PASS; modified Python syntax PASS.
- Full app Vite/React browser E2E and real PostgreSQL E2E not run locally (complete npm dependencies unavailable). New GitHub opt-in `browser_test=true` run and build required before claiming the full CI green or promoting RC gates. `publish_image` must remain false.
- Overall RC score remains **48.0%**; previous accepted gates unchanged. No commits/tags/pushes/releases executed by the assistant.
