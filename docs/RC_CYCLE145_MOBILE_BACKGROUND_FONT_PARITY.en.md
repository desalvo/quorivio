# Quorivio 0.1.0-dev — RC145 — Isolated smartphone background upload and Arial parity

## Baseline, fix, and behavior

This cumulative continues the RC144 independent 390px phone canvas, 0–9 ratings, independent phone widget positions, participant/rehearsal parity, and shared Arial defaults. It fixes a real RC144 routing bug: **a freshly uploaded image selected from the smartphone canvas context menu was incorrectly applied to the desktop page background**. The upload now writes exclusively to `page_design.mobile.backgroundAssetId` when the phone editor is active. The existing background-library selector already wrote mobile fields correctly; its duplicate `forMobile` branch has been removed. Desktop background and widget geometry are unaffected by uploading in phone mode.

The canvas right-click menu retains separate phone background color and library/upload controls. Selecting a solid phone color now removes the previous phone image so the selected color is visible immediately. Removing a phone image does not clear a separately selected phone color. If no phone background is configured, the phone stage renders white, **never** the desktop image/color.

The RC144 Arial fix has been examined in the source and checked in a real local Chromium computed-style fixture. With both editor and projection elements configured for Arial 24px, computed family, size and measured text advance are identical; the phone canvas uses its explicitly configured color and `background-image: none`. The new RC145 CSS inheritance guard prevents global application heading styles (`Outfit`) from replacing authored widget typography on h1–h4 inside editor, participant, presenter or rehearsal. Explicit per-range text marks remain authoritative.

## Validation and limitations

- Node API + web suite: **825 passed / 0 failed** after updating one historic test that asserted a single unbranched upload success message.
- New RC145 Node contract cases (4) verify image upload/selection, solid-color replacement and Arial/inline-style contracts.
- Chromium headless CSS fixture: computed Arial 24px editor and preview glyph advances equal (152.07421875px for the same sample); separate smartphone background #e0f8ff / no image confirmed. This is a style fixture, not a live authenticated editor-browser acceptance run.
- Python RC145 focused contracts and full integrity inventory are required in CI. Full Vite/TypeScript build, real authenticated image-upload flow, iOS/Android/Firefox/WebKit checks and GitHub CI remain pending before formal acceptance.

**Certified completion stays 85.25%**, with 43 accepted and 17 partial external gates. No RC promotion: `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, tag, image publication or real-server changes.

**Suggested cumulative commit message since last user-confirmed RC140 commit:**

`Complete rating/results parity, formatting ribbon, independent mobile layouts and Arial/background fixes [full-ci]`
