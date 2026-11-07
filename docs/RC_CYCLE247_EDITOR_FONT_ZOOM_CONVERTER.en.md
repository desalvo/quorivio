# RC247 — Widget typography parity, canvas space and converter tags

## Reproduced defects

The deployed screenshots reveal disproportionate independent result fonts between authoring and previews, non-Arial widget heading/choice rendering, a selected text range taking precedence over the explicit Whole widget scope, and document zoom shrinking a fullscreen overlay to reveal the dashboard underneath. Newly freed space must benefit the 16:9 canvas, not turn into blank bands.

## RC247 changes

- Independent result row text sizes now use stage-relative `cqw` units on the logical 1280px stage, not fixed screen pixels; independently saved styles remain honored.
- The explicit **Whole widget** scope takes precedence over a residual text selection and propagates to title, answers, submit text, nested subquestions and persisted rich-text spans. Scoped formatting still supports user-selected text.
- Both authoring editors default every type of widget text to Arial, while user-authored per-element typefaces remain authoritative. Chromium fixtures do not inject the Arial default.
- Displayed UI **100% is the former 80%**, using a new zoom persistence key. Fixed overlays compensate for physical viewport size; the editor stays fullscreen, the 16:9 canvas uses freed space and the dashboard expands to full width.
- Explicitly authorized converter publishing uses **`desalvo/quorivio-converter:latest` on `main`** and **`desalvo/quorivio-converter:<git-tag-name>`** on a tag ref. No automatic push trigger. The non-destructive wizard accepts `latest`, release tags or full digests and retains its reviewed patch procedure.

## Evidence and limits

Node and Python regressions, real Chromium 390/760/1440 at zoom 80/100/120 and checksummed inventory. Full RC247 GitHub CI (including strict React typecheck and PostgreSQL) is still required on the maintainer's commit. No live Kubernetes edits, Docker publication or assistant commit/tag. Certified **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
