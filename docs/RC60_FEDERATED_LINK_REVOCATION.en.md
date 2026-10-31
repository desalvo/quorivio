# Quorivio 0.1.0-dev — RC60: federated identity link revocation

**Last maintainer-confirmed baseline:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`, standard CI `41152434205`, extended CI `41152939003`. **Cycles 58–60 are cumulative, uncommitted.** No release, publication or git mutation. Version remains `0.1.0-dev`.

## Security defect and fix

The one-time PostgreSQL OAuth/OIDC state previously allowed an account-linking callback to complete after its initiating local session had been revoked by a password change/reset or administrative MFA reset. The start endpoint also checked the cookie's HMAC but not always the account's current revocation timestamp.

Both OIDC and GitHub/Facebook `?link=true` starts now validate the signed session's issuance timestamp against current PostgreSQL approval, mandatory password-change and revocation status. A backwards-compatible `auth_flows.link_auth_issued_at_ms` migration stores that issuance proof with the single-use authorization state. Both callbacks retrieve the saved issuance time, reject missing or invalid legacy proofs and perform an atomic conditional `INSERT ... SELECT` into `oidc_identities` subject to *current* account revocation state. Duplicate provider identities or multiple identities for a provider/user pair are rejected without leaking SQL errors. Non-link federated sign-in behavior is unchanged. A cross-site callback is not expected to include the local `SameSite=Strict` login cookie.

The standard CI now includes disposable PostgreSQL 18 policy tests for valid links, one-shot state, uniqueness, revocation, password rotation, approval and forced password change, gated to a loopback database in a GitHub Actions run. These tests do **not** impersonate or communicate with external OAuth providers.

## Evidence limits

Locally, 541 API Node tests and 99 web Node tests passed, including new contract and policy cases. The RC campaign preflight passed. Full TypeScript/Vite production build was not established because npm dependencies were unavailable locally; the PostgreSQL integration and external Google/GitHub/Facebook redirect/consent workflows still require CI/operator testing.

**Verified readiness remains 81.75%** (55 gates: 38 accepted, 17 partial); strict RC remains blocked. Never recredit local tests. Next maintainer action: commit once, standard CI, then one nonpublishing `rc_acceptance_suite=true`, `rc_strict=false`, `publish_image=false`, `publish_latest=false` campaign.
