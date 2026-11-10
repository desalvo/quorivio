# RC293 — Compact visual manuals and bilingual product brochures

Editorial date: **10 November 2026**. **Documentation-only** change; application runtime is unchanged. Certified functional baseline remains **85.25%**.

## Manual overhaul

- Removed compulsory page breaks before every chapter; sections now flow with visible separators and space-efficient pagination.
- Added a bilingual atlas of **20 actual widget-toolbar icons** cut from SHA-verified RC291 real captures, with practical usage and formatting guidance.
- Expanded administrator (server settings, users, audit, backup) and participant (join, response, feedback) illustrated walkthroughs.
- Every reading page has a small photographic inset; large remaining gaps carry an authentic archived screenshot and/or a **clearly labelled synthetic editorial photograph**.
- Archived images retain their originating RC attribution, but **no Git commit strings appear in the manuals**. CI still requires distinct current-commit screenshot evidence and a matching six-PDF output folder.
- All six PDFs are byte-identical between published file trees.

## Two product brochures

`docs/brochures/quorivio-brochure-it.pdf` and `docs/brochures/quorivio-brochure-en.pdf` are **two-page A4** marketing documents combining editorial imagery, verified archived screens and searchable text about widgets, sessions, previews, results, deployment, `.quo` portability and operating features. They carry the official logo, creator, email, EUPL-1.2, repository, build, publication date and indicative evaluation resources. Photography is attributed as synthetic, not software screenshots.

## Reproducible build

```bash
python3 tools/manual_icon_atlas.py
python3 tools/generate_manuals.py
python3 tools/generate_brochures.py
python3 -m unittest tools.tests.test_rc293_visual_manuals_brochures -q
```

Editorial dependencies: Mistune 3, WeasyPrint, Pillow, PyMuPDF, ReportLab and CairoSVG. They are required only in the controlled documentation authoring environment; ordinary application startup must never regenerate PDF files. Inspect rendered pages and validate actual behaviour before public distribution.
