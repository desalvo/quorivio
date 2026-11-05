# RC194 — Consistent question typography and rich-text selection

## Delivered changes

- Long answer choices wrap onto multiple lines in the editor, rehearsal and live projection. Native checkbox/radio ordering and hit targets remain unchanged.
- A highlighted range stays selected after applying a new font or text style in the Widget Format toolbar. The editor restores DOM focus and the original UTF-16 selection following the React render.
- Question/quiz widgets default to **Arial, bold 22 title and regular 16 answers**, including safe fallbacks for older widgets with missing defaults. Saved customized styles are preserved. Independent questions use the same hierarchy.
- Whole-widget typeface changes reach the base font, answer options and all inline runs, including independent questions; a legacy forced `font:inherit!important` no longer suppresses the selected family.
- Newly inserted text inherits font family, size and other typography from the glyph immediately before the caret, including segment boundaries and Unicode text.

## Evidence and limitations

- Complete Node frontend/API suites, targeted Python and TypeScript checks.
- Actual Chromium computed-style checks at 1440 and 390px show fonts, title hierarchy and full multi-line answers.
- An early RC194 preflight and a browser CSS regression are wired into GitHub Actions. Full compiled React/PostgreSQL/Chromium and Kubernetes checks await the next GitHub CI run. Do not claim these as passed locally.
- `0.1.0-dev` unchanged; certified completion **85.25%** (43 accepted gates, 17 partial). No assistant commit, push, tag, or Docker publish.
