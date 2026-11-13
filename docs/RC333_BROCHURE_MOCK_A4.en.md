# Quorivio 0.1.0 — RC333 brochure redesign (13 November 2026)

## Baseline and intent

- Resume the working branch `main` at `4c2f9f709e54c11c28758cf82e236903a3ddd853` from `Quorivio 0.1.0 #29`.
- Source reference: user's six-panel promotional collage, registered as `docs/assets/brochure-editorial/mock-reference-6-pages-2026-11.jpg`.
- **Do not substitute the earlier generic brochure layout**. Maintain the editorial sequence and the visuals of this mock, while expanding each of six panels into an A4 portrait page to the page boundaries (210 × 297 mm).
- Two complete languages (IT and EN); editable/searchable vector typography and chart components, illustrations cropped without distortion.
- The visual reference contains **six separate promotional sections**, not six copies of the same one-page design:
  1. Present, interact, engage; live polls, audience feedback, quizzes and smartphone participation.
  2. Create > share QR > present live > see results; presenter, projection and phone.
  3. Ten widget types and eight result chart types.
  4. Owner-enabled response gauge, by default off; responders at least once / total connected, 0–100%, size 20–100%.
  5. In-person, remote and hybrid events; 500 participants **exercised in a CI benchmark**, not a certified product limit.
  6. Export PDF/PPTX, share .quo for support with consent, retention, notifications and Docker/Podman/Kubernetes.
- QR artwork displayed in brochure is **illustrative** and not a live session invite.

## Artifacts and paths

- `docs/brochures/quorivio-brochure-it.pdf`
- `docs/brochures/quorivio-brochure-en.pdf`
- Mirrored exactly at `apps/web/public/docs/brochures/quorivio-brochure-{it,en}.pdf` for download from the application.
- Generator `tools/generate_brochures.py`
- Reference image `docs/assets/brochure-editorial/mock-reference-6-pages-2026-11.jpg`
- Verification `tools/verify_portrait_brochures.py`

## Build and release

Use a Python environment with `reportlab`, `pillow`, `pymupdf`, and Lato fonts; run from repo root:

```bash
python tools/generate_brochures.py
python tools/verify_portrait_brochures.py docs/brochures
cmp docs/brochures/quorivio-brochure-it.pdf apps/web/public/docs/brochures/quorivio-brochure-it.pdf
cmp docs/brochures/quorivio-brochure-en.pdf apps/web/public/docs/brochures/quorivio-brochure-en.pdf
```

The generator supports `--output-dir`, `--reference`, `--no-web`; by default it copies output to the web app. The reference image is checked into GitHub for reproducible builds.

## Honesty/acceptance and other active Quorivio work

- User had confirmed full CI GREEN and multiarch images on RC333. This editorial update is **not** a claim of a new successfully tested Docker release; recheck GitHub Actions after push.
- The Quorivio GDPR requirement and last requested server-side temporary-data cleanup apply to the application independently; this task focuses on correcting brochure assets and publication.
- Do not publish personal audience information in examples. All shown poll responses are synthetic samples; distinguish CI benchmarks from production guarantees.
- Keep cumulative handoffs and last ten Quorivio packages, do not delete manual/service assets.
- Suggested commit: `docs: match Quorivio brochures to six-panel A4 mock and publish bilingual PDFs`
