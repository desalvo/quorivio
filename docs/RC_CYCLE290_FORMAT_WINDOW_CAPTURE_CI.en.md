# RC290 — Formatted-window screenshot acceptance correctly tests an actual resize

## Evidence

[Full CI 42670034364](https://github.com/desalvo/quorivio/actions/runs/42670034364) passed the previously missing PyMuPDF contract and advanced to the disposable PostgreSQL/Chromium real-screenshot job. Ten genuine images were captured. The job failed at `Widget Formatting changed outer size when switching tabs` because the browser script compared the initial content-dependent **auto size** on the Text and Contents tabs; it had never performed a resize. The user requirement concerns a window **after a user resize**.

## Fix

The screenshot workflow now locates the actual accessible Format widget resize handle, exercises Shift+ArrowRight and Shift+ArrowDown, verifies both dimensions visibly increase, then changes to Contents and asserts the manually set outer dimensions remain unchanged (2 px screenshot rounding tolerance). A new genuine `editor-widget-format-resized` frame is included in the CI screenshot catalog. Regression tests reject missing resize operations, lack of width/height checks, or tab switching before resizing. The current React/CSS sizing mechanism is retained and not bypassed.

## Validation and scope

The current UI behavior and the earlier visual comparison are not claimed as production-certified merely from static tests. GitHub's next full CI must execute the real browser capture through the remaining preview, schema and live-session screens. No change to application runtime, privacy scope, screenshot provenance or full release baseline: **85.25%** (43 accepted, 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag performed here.
