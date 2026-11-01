# RC108 — grouped quiz PowerPoint visual export

## Scope and output

The production conversion worker uses `tools/pptx_portable.py`. Its native PPTX export now preserves all visible text from a question/timed-quiz widget: the top-level label, description and options, followed by up to five independent nested question labels, descriptions and option sets. Each line is editable PowerPoint text. Per-field `textMarks` are preserved with their saved font, size, color and toggle attributes; surrogate-pair/UTF-16 boundaries are respected. Large widgets are set to wrap and shrink text where PowerPoint supports it; operator review of readability remains necessary.

## Security and fidelity boundary

- Public slide decks carry NO correctness flags, private votes, answers, or answer-key metadata. Only visible option labels are exported.
- Strict validation rejects invalid nested question IDs, duplicated options, invalid answer references, orphaned text span fields and missing/overlong text.
- Exceeding the 6,000-character widget text ceiling fails with a clear error rather than silently removing questions.
- PowerPoint cannot reproduce the participant submission lifecycle. Reimport reconstructs only editable **plain-text** content, never a working Quorivio question group. Keep a separately secured session definition for genuine interactive roundtrip.
- The conversion worker still cannot guarantee pixel-perfect output, correct printing of all themes, or review in the commercial Microsoft Office client. Those are external RC gate requirements.

## Verification

`python3 -m unittest tools.tests.test_rc108_pptx_grouped_questions -v` is added to the native PPTX stage **after** python-pptx installation. Do not promote the parent Office-fidelity gate based solely on synthetic PPTX tests. RC107 full GitHub campaign `41309042012` was previously green; RC108 GitHub CI remains unverified until the maintainer's next push.
