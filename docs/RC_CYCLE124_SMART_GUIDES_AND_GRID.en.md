# RC124 — Smart alignment guides and absolute grid snapping (2 November 2026)

**Functional scope:** precise 16:9 canvas authoring in both page and master/scheme editors. Transient magnetic guides show edge/center alignment to other widgets and the slide centre. Guides never persist in the session or undo history, disappear after pointer release/cancel, and never intercept hit testing. Non-graphic widgets still reject collisions; graphic shapes/lines retain their deliberate overlap support.

**Functional fix:** the 5% grid previously rounded pointer movement *deltas*, leaving widgets whose starting positions were not on the grid misaligned. Grid mode now displays the actual 5% grid and snaps the selected bounding rectangle to absolute slide coordinates, including multi-selection. Grid mode takes priority over other magnetic snapping. Bounds, invalid geometry, visual-pointer safety and group relative offsets have dedicated tests.

**Local evidence:** 13 Node geometry/snap tests, 4 Python source contracts, production CSS rendered in Chromium at 1440 and 390 px. The full compiled React editor interaction and GitHub CI still require acceptance; a static CSS browser check alone is not sufficient for end-to-end certification.

**Progress:** certified **85.25%**, 43 accepted and 17 partial gates / 60; **85.75% provisional local engineering estimate**, +0.50 points *only if* the narrow proposed A1-SMART-GUIDES subgate carved out of partial A1 is formally accepted. The actual gate ledger remains unchanged. Physical devices, independent accessibility, and visual operator sign-off remain open.

**Baseline:** RC122 commit `a97b80b8d09ebd1a6054111bf88326581e2cc80f`, 11/11 automatic RC campaign jobs passed in GitHub run `41350047731`, final run `cancelled` due to a stuck Docker publication. RC123 remains uncommitted per maintainer. RC124 includes RC123; no commit, push or publication by the assistant.

**Suggested cumulative commit RC123–RC124:** `Unify safe editor image uploads, bound Docker publication, and add PowerPoint-like alignment guides with absolute grid snapping [full-ci]`.
