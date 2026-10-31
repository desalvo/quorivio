# Quorivio 0.1.0-dev — RC61: SSO identity self-service

**Date:** 31 October 2026. Maintainer-confirmed commit: `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`, standard CI `41152434205`, extended CI `41152939003` apply **only to that committed baseline**. Cycles **58–61 are cumulative, uncommitted**. Version remains `0.1.0-dev`.

## Implemented scope

The account SSO dashboard can now list linked Google, GitHub, Facebook and generic OIDC identities and unlink them. `GET /api/auth/identities` is account-scoped and returns only provider and link date, never the external subject or another user's associations, with `private, no-store` caching. `POST /api/auth/identities/unlink` requires a signed unrevoked session and the current local account password. A PostgreSQL transaction locks the user credential row, rechecks approval and session revocation after acquiring the lock, and deletes only the identity associated with the caller. Five account-scoped password attempts per minute are enforced in the shared PostgreSQL rate limiter before the main transaction, so failed attempts count even after rollback. Confirmation/cancel, password entry and refresh are present in the UI; linked providers are not offered as duplicate links. No schema migration is required. Unlink prevents **future** login using that provider; it does not by itself revoke unrelated active local sessions. Existing MFA restrictions are unchanged.

## Verification and acceptance

**Local PASS:** 546 API Node tests, 99 web Node tests, TypeScript syntax parsing of the modified sources and the RC campaign preflight. A new **GitHub CI-only** loopback PostgreSQL/HTTP suite covers authentication, private listing, user isolation, wrong password, successful unlink, replay and password-rotation revocation. The suite has **not run yet** on the new commit. Full npm build is blocked locally by missing `@types` in the archive's npm tree; actual provider consent, deployed PostgreSQL E2E, independent accessibility/hardware, and legal review remain unverified.

**Official RC score remains 81.75%**, 38 accepted + 17 partial (55 gates); C3 remains partial, and this work has no prematurely awarded score. Strict RC still blocked. After the maintainer commits: run standard CI, then one nonpublishing `rc_acceptance_suite=true`, `publish_image=false`, `rc_strict=false`, `publish_latest=false` campaign. Do not auto-commit or publish.
