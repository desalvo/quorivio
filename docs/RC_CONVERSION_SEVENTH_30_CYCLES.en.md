# Conversion batch 7 — editable PowerPoint picture cropping (30 acceptance cases)

**Baseline:** last maintainer-confirmed commit = Audience 20 Cycles (GitHub workflow 40144692900 green). Six preceding conversion batches and this seventh batch are uncommitted; **210 cumulative intervention/acceptance items**. Do not imply 210 distinct product features.

## New capability

PowerPoint pictures with representable native crops are imported as **editable image widgets** with four fractional crop coordinates. The original image remains private, byte-verified and deduplicated by digest across slides even when its visible crop differs. The native PowerPoint export reconstitutes the same crop properties; it does not bake cropped pixels into a noneditable raster. The presenter projection and rehearsal preview apply the same crop in the browser using bounded, clipped image geometry. The editor exposes four keyboard-accessible numeric crop controls and a reset action. Backend page-design validation and converter export preflight reject malformed crop data, nonfinite numbers, extra keys, negative fractions, overcrop and crop metadata on nonimage widgets.

PowerPoint negative crop/overscan and geometries removing almost the entire image are **not** supported: fidelity report distinguishes editable picture crops from unsupported crops. The existing `cropped_pictures` counter remains for backward-compatible informational reporting, but a supported crop alone no longer marks a slide lossy.

## 30-case inventory (new native PPTX acceptance)

1. Left-only crop raster fidelity.
2. Right-only crop raster fidelity.
3. Top-only crop raster fidelity.
4. Bottom-only crop raster fidelity.
5. Two-sided horizontal crop fidelity.
6. Two-sided vertical crop fidelity.
7. Left/top crop fidelity.
8. Right/bottom crop fidelity.
9. Four-sided crop fidelity.
10. Large four-sided crop fidelity.
11. Asymmetric crop fidelity.
12. Centered four-sided crop fidelity.
13. All imported cropped pictures remain editable widgets.
14. Four crop coordinates preserved on import.
15. Four crop coordinates preserved on export.
16. Embedded image deduplication across different crops.
17. Supported crops correctly excluded from lossy classification.
18. Exported pictures remain native PowerPoint picture shapes.
19. Empty/zero crop validation.
20. Maximum individual fraction boundary validation.
21. Horizontal overcrop rejection.
22. Vertical overcrop rejection.
23. Negative fraction rejection.
24. Nonfinite fraction rejection.
25. Boolean-as-number rejection.
26. Unknown key rejection.
27. Missing key rejection.
28. Export preflight rejection before publication.
29. Crop metadata rejected on text widgets.
30. Unsupported native negative crop reported as lossy.

Plus four Node domain tests and six frontend source-contract checks. The first 12 scenarios use **real LibreOffice and Poppler raster comparisons** (synthetic image corpus, not third-party Office corpus).

## Evidence and remaining work

Local: **225 Node tests PASS; 548 Python tests PASS; backend TypeScript and frontend Vite builds PASS; 12 real crop raster comparisons PASS**. New GitHub CI/container gates not yet run; independent Microsoft Office rendering, complex real-world decks and Chromium crop editor/browser acceptance still open. A3/D4 remain partial and the official RC score stays **45.5%**. No commit/push/tag/release.
