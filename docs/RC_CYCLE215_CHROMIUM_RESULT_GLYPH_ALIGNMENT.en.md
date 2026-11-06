# RC215 — Chromium result-count glyph alignment contract reconciliation

## GitHub failure
Run `42144060435` (production job `127651153649`) passed the early gates and failed at «Chromium editor UI acceptance», script `tools/ci_rc141_widget_parity_chromium.py`. `tailInline` was false on all editor, presenter, rehearsal and participant fixtures despite word and counter glyphs being exactly baseline-aligned. The historic RC141 test compared the last-word text `Range` top to the `output` **element box** top, whose bounding box is about 2.076 px higher than the painted glyphs. Downstream RC jobs were skipped, ClamAV passed and no Docker Hub image was published.

## Fix
Chromium now compares DOM text `Range`s on both sides and verifies that the bracketed count is on the same line after the final word, with bounded horizontal spacing. All original assertions for long-text wrapping, no clipping, hidden title, emoji reactions, native controls, four rendering surfaces and two viewports (1440 and 390 px) remain. No React runtime or visual stylesheet changes. Added pre-npm `tools/tests/test_rc215_chromium_result_text_alignment.py` with fail-closed mutations. A negative Chromium check that shifts the output down 8 px is rejected.

## Validation and release
Reproduced the RC214 Chromium failure locally; RC215 passes all surfaces at 1440 and 390 px and rejects deliberately offset text. Targeted Python regressions pass. GitHub full RC215 campaign remains pending. Version `0.1.0-dev`, certified **85.25%** (43 accepted / 17 partial gates); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Cumulative ZIP with grouped source SHA-256 inventory, preserving historical verifier receipts. No assistant commit, push or tag.
