# Fifth 30-case conversion fidelity batch — 2026-10-25

**Committed baseline:** Audience 20 Cycles, GitHub CI 40144692900 green. The five conversion batches (150 cases/interventions in aggregate) remain **uncommitted**.

## Implemented functionality

- Native editable PPTX import/export now retains explicitly solid slide RGB backgrounds, paragraph-level uniform horizontal alignment, and text-box vertical anchoring. Inherited/default and gradient backgrounds are not falsely claimed as lossless.
- `PageDesign.backgroundColor` and widget `textAlign`/`verticalAlign` are strictly validated by the API. Presenter projection and rehearsal render slide backgrounds; the editor exposes background-color and widget-alignment controls. Unsupported or invalid values are rejected before atomic publication.
- Fidelity reports count retained backgrounds and alignment, and explicitly mark gradient backgrounds or mixed paragraph alignment as lossy. Existing OOXML security, media quotas and atomic publication remain intact.

## 30 independently executed acceptance scenarios

1. Import a black slide background as an editable RGB page color.
2. Import a white slide background without converting it to an image.
3. Import an arbitrary brand-color solid background.
4. Import a red slide background.
5. Import a blue slide background.
6. Export an arbitrary RGB page background to native PPTX.
7. Roundtrip a black exported background.
8. Roundtrip a white exported background.
9. Normalize lowercase RGB export colors through OOXML.
10. Report retained solid backgrounds in the fidelity audit.
11. Do not fabricate a background for an inherited/default fill.
12. Report unsupported gradient backgrounds as lossy.
13. Import left-aligned text as editable widget style.
14. Import centered text as editable widget style.
15. Import right-aligned text as editable widget style.
16. Import top-anchored text boxes.
17. Import middle-anchored text boxes.
18. Import bottom-anchored text boxes.
19. Export left text alignment into PPTX paragraph formatting.
20. Export centered text alignment into PPTX paragraph formatting.
21. Export right text alignment into PPTX paragraph formatting.
22. Export top vertical anchor into PPTX text frame.
23. Export middle vertical anchor into PPTX text frame.
24. Export bottom vertical anchor into PPTX text frame.
25. Flag mixed paragraph alignment rather than claiming a lossless import.
26. Reject invalid named background colors before publication.
27. Reject unsupported alpha backgrounds before publication.
28. Reject nonstring backgrounds before publication.
29. Reject unsupported horizontal alignment values before publication.
30. Reject unsupported vertical alignment values before publication.

## Evidence and limits

- New tests: `tools/tests/test_rc_conversion_fifth_30_cycle.py` (30 behavior checks) and `apps/api/test/pptx-visual-fidelity.test.ts` (6 API validation tests).
- Tests cover real python-pptx serialization/import, export and rejection, not visual pixel comparison.
- **Outstanding:** real-world PPTX corpus, pixel/typography fidelity, LibreOffice/PowerPoint interoperability on complex themes, independent Chromium/browser/device checks and new GitHub CI. RC gate score remains **45.5%**; no new gate accepted.
- No commit, push, tag or release performed.
