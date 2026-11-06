# RC232 — Native PDF/PPTX conversion acceptance only after CI dependencies

## GitHub failure and root cause

GitHub Actions run `42237834439`, commit `86721afdd9ebed4ee9158d5770d7e4535c3b77a8`, failed in the Production quality gate at `RC229 consolidated legacy UI and converter preflight before npm`. The failing module `tools.tests.test_rc_conversion_30_cycle` performs real PDF/PPTX conversion and needs `pdfinfo`, `pdftoppm`, ReportLab and LibreOffice. The initial dependency-free section runs before the existing `Install Python conversion and load-test dependencies` step. Six errors and three additional failures occurred because these dependencies did not yet exist, not because the converter's security/quotas were defective.

## Resolution and acceptance

- Preserve the original RC229 source-only regression preflight before npm; remove only the native conversion module from that early command.
- Keep the same full `tools.tests.test_rc_conversion_30_cycle` suite mandatory in a new post-install step, immediately after `poppler-utils`, `libreoffice-impress` and `reportlab` installation. The regular global Python discovery still exercises it independently later.
- Explicitly verify presence of `pdfinfo`, `pdftoppm` and `libreoffice` in CI before launching real conversion tests.
- Add an independent no-dependency RC232 preflight asserting the ordering and negative mutation cases, so later releases cannot accidentally move the conversion suite back before installation.
- Preserve RC231 historical inventory unchanged. Promote RC232 to sole current inventory. Do not weaken fail-closed ZIP, git-index, safety or publish guards.

No application runtime logic, authentication, GDPR, database or Docker Hub publication changes. Full GitHub CI remains to be re-run. Certified 85.25% (43 accepted, 17 partial), unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
