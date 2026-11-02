# RC140 — Widget typography scopes and stage parity (2 November 2026)

Baseline: committed RC137 (successful GitHub Actions run `41475936282`); RC138–RC140 are cumulative **and not committed yet**.

## Resolved editor behavior

- Remove intrusive per-widget duplicate/bring-forward/send-back icons from the canvas itself; the same actions remain in the widget context menu and accessible organization controls. The title remains selectable and editable.
- The floating **Formato widget** ribbon offers a precise scope: entire widget, title, description or answers. Double-clicking the actual text field edits that field rather than forcing focus to the first title field.
- Entire-widget size adjustments use relative A−/A+ operations, preserving authored differences in base, answer, submit, and per-character sizes (bounded by server schema limits). No misleading single universal font size.
- Whole-widget font family, text color and emphasis update the answer styles and existing inline spans, as well as the base text. When only a field or selection is targeted, it applies there without affecting unrelated text.
- Editor answer-choice text receives the same `answerOptionStyle` helper as real presenter, rehearsal, and public participant layouts: face, color, size and emphasis are shared values. Wrapping is allowed to avoid mismatched overflow.
- Formatted title, descriptions and independent question/option spans keep the server-validated plain-text + inline-mark contract. Native keyboard arrows in text and number controls are not intercepted by the canvas.

## Verification and release status

Local tests: the full `apps/web/test` Node suite, targeted historical Python contracts, TypeScript parser, source manifest closure and package SHA-256. `npm ci --offline` cannot complete because a registry tarball is not cached; full `npm run build`, real application browser comparison and GitHub CI remain mandatory. The app's distinct presenter/participant permissions remain unchanged.

**Certified 85.25%** (43 accepted / 17 partial): `rc_strict=false`, `publish_image=false`, `publish_latest=false`. External acceptance pending; no assistant commit, push, tag or release.
