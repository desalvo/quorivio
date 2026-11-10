# RC296 development — mobile pie percentage readability

Baseline: RC295 merged into main at `f90fe76c0bf30b111b502c664d7904f284de156d`; mandatory GitHub CI [42801250135](https://github.com/desalvo/quorivio/actions/runs/42801250135) green. This is a targeted development increment, **not** a certified release.

## Defect

A fixed 500×320 SVG viewBox makes 17px pie percentage callouts about 6px high when the results chart is displayed in a 170px-wide phone widget. The existing RC295 outside-the-pie percentage leaders are correct but the phone-size text was not reliably legible.

## RC296 behavior

When the result widget's **Show percentages** preference is enabled, a separate mobile semantic legend associates each nonzero pie slice with its source option label, original color, optional option number, and percentage calculated by the common `resultPiePercent` helper. The responsive grid changes automatically from two columns to one when there is insufficient horizontal space. This prevents narrow-window overflow, and CSS sets a 14px computed-font minimum before any authored-stage transform. On mobile, SVG labels that would be tiny are hidden in favor of the readable legend; on desktop, the original SVG leaders remain visible. Disabled percentages do not produce a legend; the pie size setting, result rows and private R grading are unchanged.

The display rule applies to native narrow windows and the authored smartphone views of the editor, rehearsal and audience presentation.

## Verification

- Mandatory pre-npm Node contracts check conditional rendering, accessible list semantics, source/color association, optional numbering, view selectors and intact desktop pie size/leader behavior.
- Mandatory Playwright/Chromium CSS geometry acceptance, after the existing browser bootstrap, checks 360px and 390px windows plus phone previews in wider windows. Each case includes twelve options; tests assert no horizontal clipping, a 14px computed percentage floor and preserved pie aspect ratio.
- Local isolated Chromium geometry checks completed for desktop, narrow native phone, editor and audience preview with a representative DOM fixture. The new GitHub full CI is still to be verified.

This does not replace an actual app/PostgreSQL visual check or a physical iOS/Android screen-reader review. The independently reviewed RC gate ledger remains **43 accepted / 17 partial (85.25%)**. No strict release approval, Docker Hub publication, version tag or deployment is implied. External acceptance is governed by `docs/RC136_EXTERNAL_ACCEPTANCE_EN.md`.
