# 0.1.0-dev RC batch: publication safety, PostgreSQL/TLS email MFA acceptance, evidence diagnostics

**Committed baseline**: `dd806243e2dff0c8b608ff43d5ae9848d48361ad`, GitHub Actions 40335963980 quality/container/publisher SUCCESS. The prior run **actually published** `desalvo/quorivio:latest` on Docker Hub. Nothing in this ZIP was committed or published by the assistant. This batch is cumulative *on top of* the committed baseline.

## Macroarea 1 — Image publication: explicit opt-in only

- Every `push` to main or a version tag and every PR still validates/tests/builds/scans without pushing to Docker Hub.
- `publish` job only starts for `workflow_dispatch` with `publish_image=true` and an allowed source ref (main or a semver `vMAJOR.MINOR.PATCH[-prerelease]` tag). A standard `Run workflow` with defaults **never publishes**.
- `tools/resolve_image_tags.sh` independently revalidates invocation, exact repository, SHA, git ref, explicit consent and Docker tag syntax before login to Docker Hub.
- Default image label from main is `sha-<12 sha chars>`. Version git ref labels use the matching version tag. Optional `publish_tag` is validated; `latest` **cannot** be entered there.
- `publish_latest=true` adds `latest` only when explicitly selected on main. It is refused for version-tag dispatches. Production job retains validation+container dependencies, `production` environment, no repository write permission and multiarch/SBOM/provenance.
- **Operator prerequisite:** configure required reviewers on the GitHub `production` environment (not assumed); only dispatch an approved commit. Previously published tags are not automatically removed by this workflow change.

### Manual invocation

Actions → **Quorivio CI and Docker Hub** → Run workflow → branch `main` → `publish_image=true`; optionally `publish_tag=rc-0.1.0`. `publish_latest=false` by default. Enable `publish_latest=true` **only** to replace the live `latest` pointer. Leave all publish inputs at defaults for quality-only CI, even with `browser_test=true` or `capacity_test=true`.

## Macroarea 2 — Email MFA testable against real disposable PostgreSQL and SMTPS

- Strong TLS with ephemeral locally generated certificate, standard TLS hostname verification, AUTH PLAIN and an authenticated loopback-only SMTP capture endpoint. No real email provider, real mailbox or production database is contacted.
- SMTP auth secret generated per CI run, delivery capture file mode 0600, all ephemeral OTP/certificate/private-key files removed at end (also on failed CI). Tests do not echo credentials, cookies or OTPs.
- `tools/ci_email_mfa_postgres.py`: creates a dedicated throwaway account after provisioning, rotates the temporary password, enrols via email (10-minute code), checks wrong code/retry, proves stale cookies revoked, logs in with email factor (5-minute code), checks replay, verifies PostgreSQL row-lock single-use under concurrent clients, brute attempt lockout, forced expiry, disable/revocation and password-only login restored.
- The login-challenge SMTP delivery error handler now conditionally removes **only the digest that actually failed**, preventing a late failed send from deleting a newer reissued challenge. The enrollment email correctly says ten minutes, distinct from the five-minute login OTP.
- Fixtures are restricted to local HTTP and localhost TLS SMTP and refuse non-CI use; live PostgreSQL acceptance is **authored but not yet executed** by a new GitHub workflow.

## Macroarea 3 — RC evidence and diagnostics

- `rc_strict=true` (manual opt-in) requires all release gates accepted; it intentionally fails while release blockers remain. Default `rc_strict=false` preserves normal CI quality checks.
- The normal quality job produces a GitHub Actions RC score/gate summary; the summary does not imply CI acceptance of independent legal, mobile or external-provider checks.
- `docs/RC_GATE_MATRIX.json` re-evaluates D6 as **partial** based on already-completed 40335963980 PostgreSQL erasure and privacy evidence. This raises evidence-weighted progress from **45.5% to 48.0%**. D3 remains open and C2 remains partial: newly authored tests have not run on CI. D1 remains accepted only for the last committed baseline.

## Operational acceptance checklist

| Scope | Evidence in this batch | Still required |
|---|---|---|
| Publisher safety | Local policy tests exercise failure closed and valid manual tags | New GitHub push must show publish SKIPPED; separate authorized manual dispatch for publication proof |
| Email MFA | Local fake-SMTPS protocol/certificate tests; disposable real-DB fixture scripted | New GitHub CI on PostgreSQL 18 and real app; real provider and browser sign-off |
| Profile/photo | Previous committed PostgreSQL CI PASS | RWX multi-replica volume and independent Chromium/device sign-off |
| RC progress | Recalculated from 18 weighted gates | Further external/operator acceptance before RC |
| Packaging | Complete source + tests + RC documentation | User commit + CI replay |

**No commit, push, tag, release or publication performed.** Suggested next actions: standard CI after user commit; if green, manual `browser_test=true` with `publish_image=false`; separate publication only on request.

## Local validation / Verifiche locali (2026-10-26)
- Full Python suite: **726/726 PASS**, including manual-publisher policy and real TLS SMTPS protocol fixtures.
- Full Node suite: **433/433 PASS**.
- Generated Kubernetes credential stability check: **PASS**.
- Bash publisher and TypeScript source parse checks: **PASS**. GitHub Actions YAML/boolean defaults parsed: **PASS**.
- Full local TypeScript/Vite production build: **NOT VERIFIED** because pre-existing incomplete local `node_modules/@types` includes empty type packages (`TS2688`). Last committed CI build PASS, but it does not validate the new patch. Mandatory new GitHub CI is required.
- Real PostgreSQL+SMTPS application fixture: **AUTHORED, NOT YET RUN**; green local SMTP protocol tests alone do not certify the endpoint.
