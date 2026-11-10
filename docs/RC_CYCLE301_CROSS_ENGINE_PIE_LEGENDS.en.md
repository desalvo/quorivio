# RC301 — Cross-browser readable result legends

**Starting point:** Main release build `7c1046a16203`, based on the full-CI-green RC300 source `f27525c9b09e`.

## User-facing improvement

Long option names in mobile pie legends now wrap to multiple lines instead of being clipped with an ellipsis. Percentage values stay in their own clearly readable rows. This applies to the presenter rehearsal, editor Smartphone layout and public result variants that use the common chart component.

## New acceptance

- Uses **actual production TypeScript** `resultPieLayout` to generate a 12-option, highly skewed pie with tiny nonzero slices, as well as a separate configuration with percentages disabled.
- Runs that markup against the **shipped CSS** in native Chromium, Firefox and WebKit at desktop, 390px, 360px, and an editor Smartphone layout rendered on desktop.
- Checks physical browser-computed name wrapping, percent font size ≥14px, no overflow, correct SVG ratio, visible mobile legend with accessible count/percentage labels, hidden mobile SVG callouts, and complete absence of percentage labels when disabled.
- All PRs run the Chromium case; the extended cross-browser job requires native Firefox and WebKit. Browser failure screenshots contain only synthetic public fixture data, not credentials.
- CI static preflight checks the real module wiring and source syntax before npm.

## Release limits

This is a rendering/accessibility **automation subgate only**. It does not validate real votes in these browsers, accessibility with NVDA/VoiceOver/TalkBack, device-native mobile Safari, or production approvals. The RC ledger remains **85.25% (43 accepted, 17 partial)**; strict RC is still blocked pending independently reviewed A4/B3 and other external operator evidence. No release tag.

**Suggested merge title:** `fix: wrap long pie legends and validate Firefox WebKit accessibility`
