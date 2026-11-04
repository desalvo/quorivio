# RC175 — Faithful media within live participant widgets

**Date:** 2026-11-04. **Cumulative base:** RC174. Product `0.1.0-dev`, EUPL-1.2 unchanged.

## Verified regression and correction

A standalone Chromium fixture using the shipped `style.css` reproduced a **real CSS geometry bug**: on narrow participant viewports the generic responsive `height:auto` rule resized a media image to its source aspect ratio, while the authored widget rectangle stayed fixed. Independently, the `.widget-fit-content` element in media-only widgets had no definite block height, leaving images to use intrinsic dimensions and `<video>` to use a 150px default height. This also affected desktop layouts with unusual aspect ratios.

The fix makes **image, logo and video** fit-content blocks fill the entire widget frame in the 16:9 public stage and separately authored phone stage; ordinary image/video elements have equal CSS height and width, with `object-fit:contain` to avoid distorting their content. Source-cropped PowerPoint images keep their normalized crop positions. Live participant `<video>` uses the shared `projection-media` class. **Accessible reading** remains in normal document flow with its neutral white background, and does not inherit these fixed presentation-stage dimensions.

## Local evidence

- Frontend Node tests: **309/309**; API Node tests: **588/588**.
- New Node and Python negative-mutation tests plus Chromium DOM/CSS checks at **1280, 390 and 320 px**.
- Verified image and video rendered height follows the authored rectangle at all three sizes; crop area also remains visible; accessible background remains neutral.
- The Chromium acceptance is a real browser **DOM/CSS fixture**, not a logged-in session. Full Vite/TypeScript build, authenticated React/PostgreSQL, screenshot parity against the reporter's five examples, physical smartphone UX and 500-user server load test remain pending.

**Release governance:** 85.25% certified (43 accepted / 17 partial), unchanged pending independent gate evidence. Keep `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push, tag, deployment or publication.
