# RC248 — Dynamic editor canvas containment after RC247 UI zoom

## Verified GitHub failure

RC247 was committed as `6a7f8e5eae6a972a218fca4b45348067ef58307d`. GitHub full CI [42401914583](https://github.com/desalvo/quorivio/actions/runs/42401914583), production quality job `128491331054`, passed strict TypeScript and preceding browser probes, then failed `tools/ci_editor_mock_layout_chromium.py` at **1440×900**. The 16:9 canvas ended at y=914.92 while the editor stage ended at y=900.00. ClamAV passed; subsequent campaign jobs skipped after the quality gate failure.

## RC248 correction

The RC247 canvas max-width used the overall CSS viewport height (`100dvh`) instead of the remaining row after the responsive header and widget palette. On desktop, the stage is now a CSS size container. The canvas width is bounded by **100cqh**, subtracting horizontal ruler height and a small safety margin; the 28px vertical ruler is included in the width calculation. The slide expands to the largest available 16:9 rectangle without vertical clipping, excessive blank strips, or duplicate scaling. The intentionally scrollable mobile/phone canvas remains unchanged.

A new mandatory pre-npm negative-source contract protects the CSS stage-height rule. Chromium acceptance runs across 1440×900, 1200×900, 960×760, 760×820 and 390×844 at physical UI scales 0.64/0.80/0.96, asserting viewport coverage, stage bounds, proportional canvas, and no unintended desktop stage scrolling. The historical RC178 editor layout acceptance remains mandatory and unchanged. No changes to API, DB, Helm, Kubernetes, worker or Docker publisher.

## Acceptance and limitations

RC247 remains immutable in the source inventories. RC248 full GitHub CI is **pending**. A local Chromium pass must not be presented as full GitHub CI certification. Progress remains **85.25%** (43 accepted, 17 partial): `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, tag or publication.
