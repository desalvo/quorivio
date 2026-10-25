# Conversion batch 8 — native editable PowerPoint shape paints (30 acceptance cases)

**Baseline:** last maintainer-confirmed commit = Audience 20 Cycles, GitHub workflow `40144692900` green. Eight conversion batches, **240 cumulative intervention/acceptance items**, are uncommitted. This is **not 240 distinct new product features**.

## Functional delivery

- Native PowerPoint editable rectangles, rounded rectangles, ovals and triangles now import and export **explicit outline widths (0.25–12 pt)**, **solid/dashed/dotted line patterns**, **no-fill**, and **no-outline** flags. Supported native paint stays an editable shape rather than a rasterized image.
- The canvas editor provides keyboard-accessible controls for fill color, transparent/no fill, outline color, outline visibility, point width and dash pattern. These persist through the existing page-design save flow.
- Presenter projection, participant rehearsal, canvas editor and slide thumbnails apply the paint metadata. Unsupported theme-based line colors, widths outside the supported interval and uncommon dash patterns remain fidelity limitations, not falsely claimed as exact.
- The PostgreSQL API page-design validator and Python export preflight reject nonfinite, boolean, out-of-range or malformed outline widths, invalid dash values and nonboolean transparency flags. Existing media, crop, conversion security and atomic publication logic is retained.

## 30 distinct acceptance scenarios

1. Raster comparison: 0.25 pt stroke.
2. Raster comparison: 1 pt stroke.
3. Raster comparison: 2 pt stroke.
4. Raster comparison: 4 pt stroke.
5. Raster comparison: 8 pt stroke.
6. Raster comparison: dashed stroke.
7. Raster comparison: wide dashed stroke.
8. Raster comparison: dotted stroke.
9. Raster comparison: dotted stroke with transparent fill.
10. Raster comparison: solid fill with no outline.
11. Raster comparison: no fill and no outline.
12. Raster comparison: transparent fill with solid outline.
13. All 12 shapes remain editable postit widgets.
14. Native line widths survive import.
15. Native line widths survive export.
16. Native dash patterns survive import.
17. Native dash patterns survive export.
18. Explicit transparent fills survive import.
19. Explicit absent outlines survive import.
20. No-fill serializes to native PowerPoint background fill.
21. No-outline serializes to native PowerPoint background line fill.
22. Rectangle, rounded rectangle, oval and triangle geometries survive roundtrip.
23. Supported paint-only decks do not trigger a false lossy report.
24. Negative outline width rejected.
25. Zero outline width rejected.
26. Oversized outline width rejected.
27. NaN outline width rejected.
28. Boolean outline width rejected.
29. Unknown dash enum rejected.
30. String instead of boolean no-fill flag rejected.

Additional: **7 Node.js domain regressions** and **5 frontend/source integration contracts**. Visual comparisons render 12 synthetic PPTX slides through actual LibreOffice Impress and Poppler. This is **not** a Microsoft PowerPoint or real third-party slide corpus certification.

## Evidence and open gates

New 30-case visual/behavioral suite PASS, 232 Node.js tests PASS, backend TypeScript and frontend Vite production builds PASS. Full Python suite **583/583 PASS** locally; new GitHub CI pending. The official weighted RC score remains **45.5%**; A3/D4 remain partial. Still required: Chromium editor interaction with the new paint controls, independent Microsoft Office rendering, real-world complex presentation corpus, device accessibility and production-like deployment gates. No commit/push/tag/release.
