# RC304 — Compact results pies

11 November 2026. Baseline RC303 e630b1ca1ae00f42d4cc62e6ef2b16de4d3c0e3c.

## Fix
Pie charts previously reserved a fixed 500x320 SVG aspect ratio regardless of author-selected pie size.
The new resultPieViewport computes the vertical bounds from the actual circle and visible outside callouts, including leader elbows and label padding.
React synchronizes the viewBox and CSS --pie-chart-ratio in desktop, editor, presenter, preview, and mobile overrides.
At 940px container width, isolated Chromium checks measured graph block heights of approximately 479px (100%), 382px (72%) and 269px (40%). The text below moved up as the pie was reduced.
Automated regression checks include three-to-twelve category layouts, tiny slices and no-label mode.

## Acceptance
Full CI, independent browser/device testing and Docker publication remain separate checks. Official RC completion remains 85.25% (43 accepted / 17 partial).
