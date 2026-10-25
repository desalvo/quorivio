# Sixth 30-case conversion batch — visual interoperability and honest fidelity

**Baseline:** maintainer-confirmed green Audience 20 Cycles workflow `40144692900`. Conversion batches 1–6 (180 acceptance/intervention items) remain **uncommitted**.

## Implemented changes

- New deterministic **12-slide editable PPTX visual corpus**, containing 12 distinct RGB slide backgrounds, three horizontal alignments, bold/normal runs, real editable shapes and colors. Each slide is imported into Quorivio portable JSON, exported back to native PPTX, independently rasterized via **LibreOffice Impress + Poppler**, and compared pixelwise with a bounded mean RGB difference (<18/255 per channel). This is genuine renderer-based acceptance, not just XML assertions. All 12 checks pass locally.
- Imported text boxes retain leading/trailing whitespace, Unicode and intentional newlines (up to the existing 500-character portable description limit). Presenter projection no longer duplicates a short label followed by its full description, preserves whitespace and applies native font family, size, weight, italic, color and decoration styles.
- PPTX fidelity audit explicitly reports mixed run styling, theme text colors, unsupported gradient/native shape fills, theme shape outlines, picture cropping and long text; previously these could be misclassified as lossless. The report never includes slide content or images.
- The original 16-widget-per-slide, 200-page, image-budget, archive-safety and atomic-publication controls remain unchanged.

## 30 independently executed acceptance checks

1–12. Real LibreOffice/Poppler pixel-difference comparisons of 12 individually styled slides after native PPTX→portable→PPTX roundtrip.
13. Native 12-page slide count after roundtrip.
14. All 12 editable solid background colors preserved.
15. Editable rectangle shape geometry across all 12 pages.
16. Three paragraph alignment variants across all 12 pages.
17. Bold/normal run styles across all 12 pages.
18. Native editable shape fill colors in the exported deck.
19. Native font color in the exported deck.
20. Supported visual corpus correctly reported non-lossy.
21. Leading whitespace in native text.
22. Trailing whitespace in native text.
23. Multi-line text.
24. Unicode/diacritics/CJK text.
25. Mixed run styling explicitly marked lossy.
26. Uniform run styling does not trigger a false alarm.
27. Native theme-based text colors marked lossy.
28. Native gradient shape fills marked lossy.
29. Native theme-based outlines marked lossy.
30. Text exceeding 500 portable characters explicitly reported as lossy.

Four additional source contracts check presenter typography and non-duplicated text.

## Local evidence and limitations

- `python3 -m unittest discover -s tools/tests -p 'test_*.py' -q`: **512/512 PASS** (including the 30 new real fidelity checks and 4 presenter/audience/rehearsal contracts).
- `npm test`: **221/221 PASS**; `npm run build`: **PASS** for backend TypeScript and frontend Vite.
- `python3 tools/rc_gate_audit.py`: PASS, **45.5% weighted RC score unchanged**.
- The 12-page visual corpus is **synthetic and deterministic**; it is not a representative third-party PowerPoint corpus. Mean RGB difference is a coarse regression metric and does not prove typography/pixel-perfect parity or Microsoft PowerPoint rendering. New GitHub CI and container build still pending.
- No commit, push, tag, release or deployment.
