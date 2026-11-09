# Quorivio 0.1.0-dev — RC279 — OAuth HA manual contracts and CI repair

**RC279:** Fix GitHub Actions run [42599356568](https://github.com/desalvo/quorivio/actions/runs/42599356568): RC126/RC59 expected OAuth PostgreSQL one-use state text in an obsolete manual generator, even though the manuals are now sourced from bilingual Markdown. The test now checks published manual sources and the real PostgreSQL single-use OIDC/social callbacks. Also reconcile RC154 load-test/Gravatar manual checks with the Markdown sources, add authorized 500-participant CLI workflow and safety restrictions, update six bilingual PDFs, and retain RC278 as immutable historical inventory. No application runtime changes. The real-screenshot CI step was not reached and remains unverified; **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE279_MANUAL_CI_OAUTH_HA.en.md`.

## Acceptance / Collaudo

- New contract tests check both documentation languages and source-level PostgreSQL single-consume OAuth callbacks.
- The RC154 CLI/Gravatar contract checks editable manual sources, not incidental Python generator contents.
- Six role-specific manuals regenerated from authoritative Markdown; real screenshots must come from disposable Chromium/PostgreSQL CI and satisfy provenance SHA-256.
- Full GitHub CI, screenshot generation, actual browser/manual publication and DR tests remain pending.
