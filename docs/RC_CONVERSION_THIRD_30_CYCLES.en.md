# Third 30-intervention batch — converter security

Date: 2026-10-25. Last confirmed committed baseline: Audience 20 Cycles. Conversion batches 1, 2 and 3 remain **uncommitted**.

## Inventory of 30 interventions

1. Full PNG stream decoding.
2. IHDR header CRC validation.
3. IDAT image-data CRC validation.
4. IEND terminator CRC validation.
5. Reject missing PNG terminator.
6. Reject bytes after PNG terminator.
7. Reject unknown critical PNG chunks.
8. Reject duplicate PNG IHDR headers.
9. Enforce contiguous PNG image-data chunks.
10. Reject nonempty PNG IEND payload.
11. Reject truncated PNG chunks.
12. Reject undecodable PNG pixel data.
13. Validate PNG chunk type names.
14. Validate all ancillary PNG chunk CRCs.
15. Retain support for valid PNG metadata.
16. Validate raster color format and geometry.
17. Reject encrypted PDF files.
18. Reject PDF files declaring active JavaScript.
19. Retain ordinary nonencrypted PDF support.
20. Reject OOXML DTD/ENTITY declarations.
21. Scan complete XML parts including late DTD declarations.
22. Reject unsupported OOXML ZIP compression.
23. Reject embedded ActiveX components.
24. Reject binary OLE objects while preserving chart workbooks.
25. Reject macro-enabled PPTM content disguised as PPTX.
26. Validate absolute and URI OOXML relationship targets.
27. Validate nested percent-encoded OOXML relationship targets.
28. Reject active OOXML relationship types.
29. Protect worker root and health readiness against symlink ancestors.
30. Enforce strict Bearer authentication and unambiguous HTTP request framing.

## Evidence and limitations

- 43 new behavioral tests for PNG, PDF, OOXML parsing and worker HTTP framing; local totals: 418 Python, 215 Node.
- Backend TypeScript and Vite frontend builds PASS. Real PDF/PPTX conversions remain covered by the Python suite.
- Pillow is now an explicit converter image and CI prerequisite; no remote commit or publication.
- The new converter container and the new GitHub CI **have not been executed** in this batch.
- Real-world PPTX visual corpus, independent penetration testing and accessibility acceptance remain open.
- D4 remains `partial`; RC score unchanged at **45.5%**. Not a release candidate.
