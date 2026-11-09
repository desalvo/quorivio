# RC278 — Live-evidence bilingual manual publication

**Base:** RC277 cumulative sources, with no application runtime changes. **Version:** Quorivio 0.1.0-dev. **Edition:** RC278 (9 November 2026). **Creator:** Alessandro De Salvo <braket71@gmail.com>. **Licence:** EUPL-1.2. **Repository:** https://github.com/desalvo/quorivio.

## Changes

- **One-source release metadata** (`tools/manual_release_metadata.py`): software version from `package.json`, author/email/SPDX from `LICENSE`, edition/build/date from the manual release; GitHub CI adds the actual source commit. All six covers display the official logo, repository, supported Linux amd64/arm64 Docker/Podman/Kubernetes server and desktop/mobile web clients, plus **indicative** test hardware estimates, explicitly not certified minima.
- **Expanded bilingual admin runbooks** for horizontal scaling, actual RWX/CSI storage, WebSocket continuity and failover, autoscaling limitations, backup validation, PostgreSQL 18 and asset recovery, RPO/RTO, DR cutover/failback. Presenter and participant tutorials cross-reference the genuine screenshots and sample quiz workflows.
- **Actual Chromium captures**: `tools/ci_manual_real_screenshots.py` exercises the **real production web app** against an ephemeral PostgreSQL 18 API, not a DOM reconstruction. It captures up to 14 views of login, workspace, server backup/audit/users, editor, rehearsals, live projection, participant mobile joining, question and submitted feedback. At least nine images and three per role are required.
- **Evidence and privacy**: strictly loopback HTTP with synthetic `example.com` administrator, masked credentials and join token controls. `capture.json` stores commit, source, image hashes and dimensions. The PDF generator rejects missing images, changed bytes or mismatched build provenance; it never promotes old illustrations into a real screenshot gallery.
- **Build-scoped CI artifact**: `quorivio-live-manuals-<sha>` contains all fresh images and six generated bilingual PDFs for successful screenshot stages; 14-day artifact retention. Generation into `/tmp` avoids changing the tracked release files after checkout and falsely failing source-inventory tests. Publication into the application awaits human review and a new committed release; CI does not push generated images or PDFs automatically.
- **Local RC278 PDFs**: expanded manuals built with clearly labelled illustrative images. **Real captures are not available in this local environment**: the npm registry could not be resolved (EAI_AGAIN) so no authenticated live app run was possible. Do not imply that CI screenshots have already been collected.

## Verification

```
python3 -m unittest tools.tests.test_rc277_manuals tools.tests.test_rc278_manual_screenshots -q
python3 tools/generate_manuals.py
# Only in disposable CI after actual API/PostgreSQL/Chromium startup:
python3 tools/ci_manual_real_screenshots.py
python3 tools/generate_manuals.py --require-real --output-dir /tmp/quorivio-manual-build
```

The next full CI must validate the new capture stage and browser rendering. CI fixture images do not constitute Kubernetes production, physical device, GDPR/AGID or security certification. Product baseline stays **85.25%**, 43 gates accepted/17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. The assistant did not commit, push or tag.
