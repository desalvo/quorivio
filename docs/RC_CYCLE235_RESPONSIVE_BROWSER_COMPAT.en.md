# RC235 — responsive browser compatibility and RC226 test repair

**Evidence:** GitHub Actions run 42249042835 on commit `774c8431972fdff1a73ad780352c1cf6550e17ad` failed Production quality gate at `tools/ci_rc226_responsive_studio_chromium.py`, width 320. Measured `paletteScrollable=False`, while the prior RC234 design removed horizontal scrolling. This is an obsolete browser acceptance condition, not a signal to undo the functional CSS fix.

**Correction:** In addition to reconciling the stale RC143 formatter fixture with the real tabpanel role and adapting the historical RC178 editor fixture to the vertical mobile filmstrip, the RC226 fixture now uses production-like `.editor-icon-wrapper` wrappers (rather than bare buttons, which become 302 px high at 320 px). It verifies one-column layout, horizontal scrolling of page thumbnails, widget palette wrapping, absence of horizontal overflow, vertical scrolling capability, and scrolling the final widget into view. No runtime CSS or TSX change. Browser RC171, RC226, RC234 acceptance all required in CI. `test_rc235_responsive_browser_compat` runs before npm and mutation-checks the new acceptance contract.

**Evidence gates (local):** RC226 Chromium 4/4 widths (320/390/760/1440); RC171 Chromium 3/3 widths; RC234 Chromium 9/9 widths (320–1440); RC143 formatting Chromium 2/2 widths; RC178 editor Chromium 4/4 widths; RC235 compatibility Python tests 5/5. Full integrated CI and independently audited release gates remain unverified for RC235. Current release source inventory is RC235; RC234 and previous manifests are historical.

**Publishing:** Keep Quorivio 0.1.0-dev, no assistant commit/push/tag. Full CI must be confirmed before any release promotion. Completion ledger remains 85.25%, 43 accepted / 17 partial.
