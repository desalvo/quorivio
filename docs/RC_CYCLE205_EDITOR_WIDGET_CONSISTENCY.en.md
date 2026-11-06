# RC205 — Editor and master widget parity / imported presentation pages

## User-reported defects and changes

1. The canvas editor and scheme editor share one typography inheritance path. Arial and persisted whole-widget family/face/size/color now apply to title, free text, choices, submit text and footer numbering. Explicit answer styles remain independently selectable. The format dialog uses a single text style control group rather than duplicated answer/footer selectors.
2. Switching single/multiple choice back to text restores the textarea immediately; existing options may remain in stored data for later editing but are not rendered in free-text mode. Long options wrap without one-line truncation. Graded options show non-revealing selection instructions beneath the submit button.
3. Footer formatting floating palette is constrained to a compact maximum height and scrolls within that palette; it must not stretch across the entire canvas.
4. The editor resolves linked results against source widgets on the selected other page, displaying the source question and deterministic sample statistics; participant/presenter preview confidentiality remains unchanged.
5. Thumbnail PDF/PPTX import requires explicit isolation. Converted pages are now saved as full-slide image widgets, rather than a legacy-only media field invisible to the canvas editor. The first new page opens after pending-change confirmation; failure is shown in the sidebar. Native PPTX export avoids re-embedding the same converted image twice.

## Operational dependency and limits

The import API intentionally fails closed when `QUORIVIO_ENABLE_CONVERTER` is not `true` or a private conversion worker URL/token and shared media volume are absent. PDF/PPTX slide content is rasterized for reliable visual fidelity; users can overlay native Quorivio widgets but the original slide text/shapes are not automatically made individually editable. Do not enable unisolated LibreOffice execution inside the API.

## Verification

The early regression guard `tools/tests/test_rc205_editor_consistency.py` runs without npm or Python conversion dependencies. The native image snapshot roundtrip `tools/tests/test_rc205_native_slide_roundtrip.py` runs after Pillow and python-pptx are installed. Existing RC193/RC194/RC200/RC203/RC204 regressions retained; TS/TSX parsing can be verified locally without the full dependency graph. Full Node build, Chromium interactions, PostgreSQL import, Kubernetes acceptance and release approval remain for GitHub CI.

**Release policy:** `0.1.0-dev`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`; certified 85.25% unchanged. No assistant commit/push/tag.
