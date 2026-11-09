# RC291 — Two distinct Smartphone controls in the real rehearsal

## Evidence

The [full CI #42674623251](https://github.com/desalvo/quorivio/actions/runs/42674623251) passed the RC290 explicit-resize test and captured fifteen authentic PostgreSQL/Chromium screenshots, including presenter, participant and side-by-side rehearsal. It then stopped with a Playwright strict-locator error: two `Smartphone` buttons are visible in the same dialog when the preview is side by side. Their separate accessible groups are **Preview mode** (`Modalità anteprima`) and **Participant device** (`Dispositivo partecipante`). The unscoped button locator was ambiguous; this is a test-infrastructure problem, not a demonstrated app failure.

## Fix and screenshots

The capture now selects the Smartphone button under `Dispositivo partecipante`, verifies the side-by-side participant pane switches to a phone and captures that state. It then selects Smartphone under `Modalità anteprima`, verifies the entire rehearsal enters its separate mobile mode and captures it. Both buttons are checked for uniqueness, enabled state and `aria-pressed`; broad ambiguous selectors are rejected in early fail-closed regression tests. New `rehearsal-side-by-side-smartphone` screenshot and bilingual captions are included in the evidence catalog.

## Validation and limits

Local tests exercise both accessible groups, reject wrong selectors and verify exact source component wiring. The **full Chromium/CI path after these previews**, including master editor, live presenter and participant screen captures, still requires verification in the next run. No runtime code changes, production data access, authentication bypass, or silent reuse of stale screenshots. Overall product baseline remains **85.25%** (43 accepted / 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag performed.
