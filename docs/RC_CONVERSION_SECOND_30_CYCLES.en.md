# Second 30-intervention batch — native PPTX conversion and safe publication

**Confirmed committed baseline:** Audience 20 Cycles, workflow 40144692900 green. **Important:** the preceding `RC_CONVERSION_30_CYCLES` batch is still **uncommitted**; this package includes both batches (60 documented interventions).

## Inventory

1. Reject PNG payloads with a forged signature and undecodable structure.
2. Reject truncated PNGs and corrupt image chunks.
3. Validate complete JPEG decoding instead of only magic bytes.
4. Cross-check declared MIME type with decoded image format.
5. Enforce a 16-million-pixel image budget.
6. Validate decompressed image streams with Pillow before publishing.
7. Reject case-colliding duplicate OOXML ZIP members.
8. Reject Windows drive-prefixed OOXML paths.
9. Reject noncanonical OOXML paths with repeated separators.
10. Reject control characters and ./ prefixes in OOXML member names.
11. Expand forbidden executable OOXML member extensions.
12. Parse XML relationships including entity-encoded attributes.
13. Reject malformed OOXML relationship XML.
14. Reject symlinked or non-regular PPTX sources.
15. Reject symlinked imported-media directories.
16. Create imported assets exclusively without silent overwrite.
17. Enforce private 0600 permissions for extracted media.
18. Bound nested-group counting in fidelity reports.
19. Reject empty and oversized slide collections during inspection.
20. Validate explicit imported presentation titles.
21. Type-check exported format, version and page list.
22. Type-check page_design and widget collections.
23. Validate finite bounded widget geometry before export.
24. Validate widget rotation including NaN and boolean rejection.
25. Reject XML 1.0 incompatible text characters.
26. Validate style and formatting field types.
27. Validate quiz option structure and quotas.
28. Enforce aggregate unique-media quotas for PPTX export.
29. Publish PPTX and CLI JSON exclusively and atomically with private temporary files and cleanup.
30. Hash and recheck worker import/export sources and reject symlinked conversion roots.

## Verification

Python **375/375 PASS** (35 new behavioral regressions); Node.js **215/215 PASS**; API TypeScript and web TypeScript/Vite builds **PASS**. Previous batch locally passed a real 12-page PDF and LibreOffice PPTX conversion. No new GitHub CI or independent real-world visual-fidelity corpus has run.

**Still open:** full visual fidelity, representative PPTX corpus, cross-browser/device rendering, independent AV/pentest, operational acceptance and RC sign-off. Gate D4 remains partial; RC audit **45.5%**, with no unverified promotion.
