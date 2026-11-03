# RC152 Chromium result wrapping CI fix

## Evidence and root cause

GitHub Actions `41708756081`, commit `78f784a`, passed all 825 Node tests and the production TypeScript/Vite build. The production browser acceptance then failed in `tools/ci_rc141_widget_parity_chromium.py` because `pairNoWrap` expected `white-space:nowrap` on the entire result. Since RC143, long label rows must wrap rather than truncate; only the last word and bracketed count form an indivisible tail.

## Change

- Keep the real RC143 application CSS untouched, including the result label wrapping rule.
- Update RC141 Chromium synthetic markup to render the same `linked-result-label`/`linked-result-final` split that React produces, including `[28]`.
- At 1440px and 390px verify wrapping, the atomic last-word/count group, native checkbox geometry, reaction size and no unintended clipping for an authored 320px fixture across all four stage surfaces.
- Normalize the test fixture to the authored widget size and explicit 16px font property. The previous participant fixture omitted `--authored-widget-font-size`, producing an unrealistic 3.8px `1.25cqw` font instead of the user-authored font.
- Add browser negative-mutation regressions: restoring whole-label nowrap or allowing the tail count to detach must fail.
- Add RC152 inventory and preserve RC151 manifest as immutable historical evidence.

## Release and safety

No product or CSS runtime changes. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Completion remains 85.25% (43 accepted, 17 partial). Full GitHub CI, integration tests and browser device acceptance require a new commit and separate evidence; no assistant commit/push/release.
