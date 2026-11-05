# RC193 — Editor focus stability and answer typography (Quorivio 0.1.0-dev)

## Changes

- Fixed an intermittent caret jump that disappeared on refresh: previously focused rich-text siblings used stale remembered selections when any answer changed. Only the actually focused contenteditable may restore its selection; blur clears stale caret memory, and unchanged siblings avoid unnecessary DOM rewrites.
- Widget Format now offers an always-visible numeric font-size input (10–96) at every formatting scope, explicit up/down arrow controls, Enter/blur commit and safe temporary empty input. Whole-widget A−/A+ proportional scaling is preserved.
- Arial remains the default question/answer font, including older styles without explicit authored values. Whole-widget font selection propagates to answer options and independent subquestions, defeating historical forced `font:inherit!important` CSS while preserving separately configurable answer sizes.

## Validation

- Complete local Node frontend/API suites, targeted RC193 Python tests and isolated TypeScript syntax checks.
- Added mandatory real Chromium/PostgreSQL integration test in the existing opt-in editor acceptance path to test continuous typing without reload in editor and properties, plus font-size steppers and Arial/Georgia answer parity. This must pass the next GitHub CI before being claimed as certified.
- No changes to the response API, persisted answers, answer-key privacy, or authorization.
- `0.1.0-dev` unchanged; certified score remains **85.25%**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag.
