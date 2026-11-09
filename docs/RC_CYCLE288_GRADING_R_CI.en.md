# RC288 — CI fix: result grading and the R button

[Full CI 42662034657](https://github.com/desalvo/quorivio/actions/runs/42662034657) stopped at the historical RC221 contract: it still expected the obsolete “Highlight true answers below results widget” editor strip. That strip was **intentionally removed in RC287** because it covered the editor footer. The current behavior is the circular **R** button inside result widgets and a setting inside Widget Formatting.

## Changes

- Preserved RC221 editable PDF import, private grading keys and result text style checks, while validating the current UI rather than resurrecting the broken authoring strip.
- Added RC288 positive/negative regression tests for the R button, answer-key conditionality, private schema and removal of the overlapping control.
- Added an early CI gate preceding RC221; historical RC287 inventory remains immutable and RC288 is the active source inventory.
- Regenerated six bilingual manuals with RC288 build labels without misattributing archived authentic screenshots to this commit.

**Limits:** No application runtime changes. PostgreSQL/Chromium and container CI must still run on the user's committed changes. Baseline **85.25%** (43 accepted, 17 partial gates); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push or tag performed.
