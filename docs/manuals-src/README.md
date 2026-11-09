# Quorivio RC278 — bilingual release-controlled manuals

The six editable Markdown files (`user`, `presenter`, `admin` × Italian/English) are the editorial sources. The official logo, name, author **Alessandro De Salvo**, contact **braket71@gmail.com**, **EUPL-1.2**, GitHub URL, software version, build and publication date come from `LICENSE`, `package.json` and `tools/manual_release_metadata.py` — not separately typed in each PDF. The cover also states supported environments and *indicative* evaluation resources; these are **not production-certified minima**.

## Local authoring (no authentic server captures)

```
python3 tools/generate_manuals.py
python3 -m unittest tools.tests.test_rc277_manuals tools.tests.test_rc278_manual_screenshots -q
```

The local PDFs contain clearly labelled explanatory reconstruction artwork and diagrams. They **must not** claim these are genuine screenshots. `docs/assets/manual-illustrations` contains reconstructions. Update IT and EN sources together and regenerate the two publication trees, `docs/manuals` and `apps/web/public/docs/manuals`. Copies must be byte-identical.

## Authentic screenshot lifecycle in CI

The full GitHub Actions CI already boots a real Quorivio API, PostgreSQL 18 and a real production frontend on `http://127.0.0.1:8080`. The `Capture real app screenshots for the manuals` step runs `tools/ci_manual_real_screenshots.py` **after that runtime is ready** and uses Playwright Chromium to capture live UI for admin, presenter and participant workflows. The script refuses production/external URLs and non-synthetic admin identities. It masks join links, passwords, QR and email entry fields. The disposable demonstration data is never a real user's session.

The CI job creates `docs/assets/manual-screenshots/*.png` and `capture.json` with precise Git source commit, screenshot SHA-256 and image dimensions. The next step executes:

```
python3 tools/generate_manuals.py --require-real --output-dir /tmp/quorivio-manual-build
```

This fail-closed build checks provenance, exact screenshot checksum, matching commit and sufficient coverage for every role. The GitHub Actions artifact `quorivio-live-manuals-<commit>` contains the screenshots and all six generated PDFs. **CI must not overwrite committed PDFs at build time**, otherwise the source SHA-256 inventory would change after checkout. The CI artifacts are retained for 14 days; download and review them before expiry. To publish new real screenshots to the repository, a maintainer must review them for correctness, privacy and accessibility and explicitly incorporate them with a new release-manifest update. Never commit unreviewed test artifacts or screenshot evidence from production.

**Screenshot freshness policy:** a new commit yields a distinct captured revision and a fresh six-PDF bundle when the capture job passes. An absent screenshot manifest, wrong source commit, removed file or changed image bytes causes a `--require-real` failure; the pipeline must not silently reuse a reconstruction or older screenshot as authentic. PDF artifacts are supplementary to the normal app quality gate. A full staging/production browser acceptance review is still required to certify that the screenshots and manuals match the deployment.

## Restore, scaling and other infrastructure procedures

The admin manual includes stepwise backup/restore exercises, POSIX/NFS/S3/WebDAV configuration, LDAP review, audit retention, PostgreSQL 18, ingress, multi-replica RWX requirements, DR drills, RPO/RTO and failure handling. Use actual release Helm values as the authoritative configuration reference. The presenter and participant manuals include sample workflows and annotated real captures once the CI screenshot artifact has been produced. Hardware estimates are planning suggestions, not vendor-certified benchmarks.
