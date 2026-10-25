# Quorivio 0.1.0-dev — 30-intervention conversion and publication batch

**Committed baseline:** `quorivio-0.1.0-dev-audience-20-cycle-real-browser-cumulative.zip` (maintainer confirmed commit). GitHub Actions `40144692900` production quality and container build both **SUCCESS**, production publication SKIPPED. Browser editor and real PostgreSQL audience acceptance **PASS**. Earlier opt-in 500-participant acceptance **PASS** in `40141894130` (not rerun here).

## 30 functional/security interventions (one cumulative package)

### A. Import admission and OOXML boundary (1–6)
1. Apply the same native OOXML archive validator to **flattened PPTX imports** as to editable PPTX imports.
2. Reject external OOXML relationships before invoking LibreOffice.
3. Reject macro/executable archive members before invoking LibreOffice.
4. Reject path traversal, absolute paths and backslash-based unsafe OOXML members.
5. Reject duplicate, encrypted and symlinked OOXML members.
6. Enforce native OOXML entry count, expanded size, per-entry and compression-ratio limits for flattened conversion.

### B. Source and destination lifecycle (7–12)
7. Reject symlinked input files.
8. Require regular input files, rejecting directories and special files.
9. Apply a bounded source-file size and explicit supported extensions/signatures.
10. Compute input SHA-256 incrementally without loading the entire input into memory.
11. Detect input mutation between initial validation and final publication.
12. Refuse existing outputs and symlinked output-parent directories before conversion.

### C. PDF conversion and ordering (13–18)
13. Parse exactly one valid `pdfinfo` page-count field, rejecting ambiguity.
14. Reject empty or over-200-page documents before rasterization.
15. Bound subprocess execution time with safe timeout failures.
16. Avoid returning raw converter stderr containing potentially private file paths.
17. Sort Poppler-generated page numbers **numerically**, including decks with 10+ pages.
18. Reject missing, duplicate, out-of-range or unexpected raster output files.

### D. Rendered page integrity and privacy (19–24)
19. Require PNG signature and IHDR structure for each rendered page.
20. Verify IHDR CRC and supported PNG format metadata.
21. Bound PNG width, height and total pixel count.
22. Bound each rendered page's byte size.
23. Bound aggregate rendered-page bytes across a presentation.
24. Restrict page/manifest permissions and publish only after all hashes and the manifest are complete.

### E. Portable conversion worker atomicity (25–28)
25. Reject unsafe/symlinked job workspaces and existing portable import outputs.
26. Stage imported assets and portable JSON privately; publish only after successful conversion and fidelity inspection, cleaning failures.
27. Stage PPTX exports privately, enforce the output quota and publish with exclusive hard-link creation (no silent overwrite).
28. Reject duplicate JSON keys, non-finite numbers and symlinked media inputs in portable export.

### F. Private HTTP boundary and CI acceptance (29–30)
29. Enforce JSON Content-Type, bounded decimal Content-Length, exact `job` request shape, non-cacheable JSON and `nosniff` responses.
30. Add **58 new automated regressions** (including a real 12-page PDF render, a real LibreOffice PPTX render, HTTP and atomic-failure injections); make LibreOffice/Poppler dependencies explicit in CI.

## Verification

- **Local Python:** 340/340 PASS (282 prior + 58 new).
- **Local Node.js:** 215/215 PASS (unchanged application behavior).
- **API TypeScript + web TypeScript/Vite production builds:** PASS.
- **Real Poppler PDF 12-page conversion:** PASS with correct `page-0010.png` ordering and verified manifest hashes.
- **Real LibreOffice PPTX flattening:** PASS locally.
- **GitHub CI for this batch:** **NOT YET RUN**. The new LibreOffice dependency and regression suite must pass in the next workflow run.
- **Weighted RC score:** 45.5/100, unchanged. D4 remains partial; a converter safety improvement is not a complete PPTX fidelity or security sign-off.

## Remaining acceptance

Full representative PPTX/PDF visual fidelity corpus, editable object roundtrip, fonts/effects/transitions, production container execution, resource-exhaustion testing and independent accessibility/security review. No commits, pushes, tags or releases were performed by the assistant.
