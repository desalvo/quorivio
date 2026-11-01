# RC104 — Editable rich text in native PowerPoint

**Scope:** PPTX export and import for Quorivio 0.1.0-dev, with no release-readiness credit before the next externally validated CI.

## Completed

- Preserve independently formatted text spans for **Text**, **Post-it**, **Title**, **Footer**, **Question** and top-level quiz options, including supported font family, font size, bold, italic, underline, strike-through and RGB color.
- Explicit span overrides take precedence over widget defaults, including removing bold from a selected title span while retaining bold elsewhere.
- Reuse the same `label`, `description`, and `option:<id>` fields as the React projection, including native paragraphs/newlines. On import, recover supported PowerPoint font runs into bounded `description` text marks so they remain editable in Quorivio.
- Respect JavaScript UTF-16 selection offsets without splitting non-BMP Unicode characters. Validate mark fields, ranges, allowed fonts, number/color/boolean types and a 64-mark bound independently inside the converter worker. Do not trust HTML or user-supplied OOXML.
- Retain RC103 native participant QR picture plus editable, clickable URL export.

## Acceptance

Run `python3 -m unittest tools.tests.test_rc104_pptx_inline_text_roundtrip -v` **after** installing `python-pptx`, as explicitly ordered by the standard GitHub workflow. Full Python discovery runs it again.

Human Office acceptance should include mixed-styled text, selected-bold toggle in titles, inherited footer formatting, independent quiz-option spans, and an import/edit/export roundtrip. The native regression tests verify OOXML runs and editable text, not independent pixel-perfect Office visual fidelity.

## Explicit limits

This does not preserve unsupported Office effects, arbitrary font faces, nested multi-question widget semantics, animations or live audience interactivity in static decks. Imported text remains a Text/Post-it widget, not automatically a semantic Title/Footer. External Office corpus, operator review and independent D4 acceptance remain open. No commit, deployment or Docker Hub publication is carried out.
