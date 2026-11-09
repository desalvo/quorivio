# RC284 — Docker runtime build and authentic screenshot follow-up

## GitHub Actions evidence

Run [42624246307](https://github.com/desalvo/quorivio/actions/runs/42624246307), 9 November 2026, passed Production quality gate, ClamAV, Firefox/WebKit, and Kubernetes manifest schema validation. Docker, rootless Podman, OCI, and KIND test jobs all failed while installing system packages inside the Alpine Node production image.

## Root cause and repair

The production Dockerfile `RUN apk add --no-cache postgresql18-client tar` line included literal backslash and `n` characters instead of a Dockerfile line-continuation backslash followed by an actual newline. Shell tokenization passed `n` to `apk`, yielding `n (no such package)`. RC284 fixes that one continuation and preserves the npm runtime cleanup and `USER node` security posture.

Four tests in `tools/tests/test_rc284_container_runtime_build.py` execute before npm and check actual shell tokens, `sh -n`, runtime stage structure, nonroot hardening, and an intentionally malformed escaped-newline regression.

## Real screenshots and manuals

The same CI run published `quorivio-live-manuals-0bb89e6ac79ed57493130f06fc5042182a166ed6`: 13 actual Chromium/PostgreSQL screenshots with SHA-256 manifest and six IT/EN generated PDF manuals. The capture records source commit `0bb89e6ac79ed57493130f06fc5042182a166ed6` and synthetic-only fixtures. The RC284 local PDFs are regenerated without mislabeling earlier-commit evidence as current. The next CI run will capture fresh screenshots for the new commit.

## Pending validation

RC284 Docker/KIND/Podman/OCI runtime is not certified until a fresh full CI passes. Do not tag or release while these jobs fail.

## PDF rendering repair, verified pictures and provenance

The RC283 CI artifact included 13 genuine PNGs and six PDFs, but rendering inspection showed the PDF gallery contained printed HTML figure source instead of images. The renderer now processes vetted Markdown HTML, bounds illustrations to the A4 page (including tall smartphone screenshots), and verifies that each real screenshot caption shares a PDF page with a physically embedded large image. Source PNGs and SHA-256 manifest are preserved in `docs/assets/manual-evidence-rc283/`; six RC284 manuals (214 pages total) visibly label these images as **RC283 ARCHIVE** and display their original commit. The `--require-real` mode is strictly separate: it requires new screenshots from the exact `GITHUB_SHA` and refuses archived pictures as current. Regression checks in `tools/tests/test_rc284_manual_pdf_gallery.py` run in CI after PDF generation.
