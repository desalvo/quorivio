# RC136 — Independent operator acceptance and verifiable evidence handoff

**Baseline:** RC135 GitHub Actions run 41437489546, commit `6c1118e93076c5d2eb8d60e96a43f8c663178053` (all executed full-campaign jobs passed; multiarch image published). RC136 introduces an **operator acceptance verification tool**; **it does not close or certify any of the 17 external gates.** Certified score: **85.25%** (43 accepted / 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No code release, commit, or operator approval is implied.

## Purpose and scope

`tools/rc_external_evidence.py` converts the existing 17-gate operator plan into a tangible, offline, SHA-256-verified review packet. It verifies the **presence, integrity, gate-specific completeness and stated independent approval** of evidence. It does **not** verify the truth of the review, certify accessibility/GDPR/ISO compliance, or update `RC_GATE_MATRIX.json`. Each of the 17 gates requires external proof (real hardware, providers, independent storage, operator or legal/security assessment). The specific mandatory evidence facets are frozen in `docs/validation/RC136_OPERATOR_EVIDENCE_REQUIREMENTS_20261102.json` and guarded by tests and CI.

## One-packet workflow, off Git

1. Install Python 3.10+; prepare a secure local directory that is **not** tracked by Git or publicly uploaded. Choose the **exact full commit SHA of the version being reviewed**, not a SHA from a previous release.
2. Create a blank, **unapproved** packet:

   ```bash
   python3 tools/rc_external_evidence.py --init ../quorivio-operator-evidence --commit <40-character-reviewed-commit-sha>
   ```

3. For each of the 17 entries in `../quorivio-operator-evidence/reviews.json`, collect real independent physical/provider/operator evidence. Redact participant names, email addresses, tokens, private screenshots, passwords and other personal information **before** import. Add a separate, substantive artefact for **each** listed facet:

   ```bash
   python3 tools/rc_external_evidence.py --attach ../quorivio-operator-evidence --gate A4 --facet nvda --file /secure/redacted-nvda-report.pdf
   ```

   Other allowed report types: TXT, Markdown, JSON, CSV, PNG, JPEG, WebP, MP4, WebM and LOG. Files must be regular, nonempty, at most 1 GiB. The importer refuses overwrite and stores the SHA-256 for each copy. **Review videos are not automatically anonymized.** Do not import `.env`, keys, or unredacted private material.
4. After actual external review, each gate's independent reviewer **must** edit its record: fill `operator`, `independent_reviewer`, timezone-aware `reviewed_at` (e.g. `2026-11-02T13:00:00+01:00`), `environment`, `review_scope`, substantive `notes`, and only on a genuine pass set `outcome` to `pass` and `independent_approval` to `true`. A rejected/incomplete review must remain pending. The operator and reviewer identities must differ; note that the tool cannot independently authenticate either identity.
5. Check against the exact reviewed commit:

   ```bash
   python3 tools/rc_external_evidence.py --report ../quorivio-operator-evidence
   python3 tools/rc_external_evidence.py --check ../quorivio-operator-evidence --expected-commit <40-character-reviewed-commit-sha>
   ```

   `--check` exits nonzero if any facet is absent, modified or unapproved; if any reviewer/commit/date is inconsistent; or if any path, symbolic link, duplicate or SHA-256 is unsafe. Only an independent owner can finally accept the **substance** of the evidence and explicitly approve gate promotions. A positive report is **not a release certificate** (`certifies_release=false`).
6. After independent verification, formally reconcile `RC_GATE_MATRIX.json` and release documents under maintainer control. A manual strict gate requires **both** all 60 ledger gates accepted and a matching complete off-repository evidence packet. Usage:

   ```bash
   python3 tools/rc_release_preflight.py --strict --evidence-dir ../quorivio-operator-evidence --commit <40-character-reviewed-commit-sha>
   ```

   In trusted CI, `QUORIVIO_RC_EVIDENCE_DIR` and `GITHUB_SHA` may supply these parameters. Do **not** commit private attachments, actual review identities, or provider secrets. Without external evidence, the strict gate intentionally stays red even if somebody edits all gate statuses to `accepted`.

## Release boundary

- **Technical build readiness:** RC135 full CI passed, including native OCI builds/runtimes, Kubernetes variants, ClamAV, browser engines and multiarch publication; future development changes require new CI.
- **Formal release-candidate acceptance:** remains **blocked** pending 17 independently witnessed/reviewed gates. Current completion 85.25%. Do not change `rc_strict`, `publish_image`, `publish_latest`, create release tags, or claim legal/AGID certification on the basis of this packet generator.
- **No automated signoff:** CI checks only the schema/facet mapping, failure modes and release strict refusal. Operator notes or generated templates never count as accepted evidence.
