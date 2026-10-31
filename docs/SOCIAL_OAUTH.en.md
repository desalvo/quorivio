# GitHub and Facebook OAuth2 — Quorivio 0.1.0-dev

## RC61 update

Existing GitHub/Facebook associations can now be listed in the account SSO dashboard and unlinked after confirmation and a current-password challenge (5 attempts/minute per account across replicas). OAuth single-use state is persisted in PostgreSQL; it is not process-local any more. Real HTTP/DB unlink acceptance has been wired into CI but has not run yet; real provider consent and operator acceptance remain outstanding. The historical notes below describe the first OAuth implementation.


## Scope
GitHub and Facebook use dedicated OAuth2 flows rather than OIDC id_tokens. Linking requires an authenticated, approved local account; matching an email never triggers automatic linking.

## HTTPS-only settings
- `OAUTH_GITHUB_CLIENT_ID`, `OAUTH_GITHUB_CLIENT_SECRET`, `OAUTH_GITHUB_REDIRECT_URI` (callback: `/api/auth/social/github/callback`)
- `OAUTH_FACEBOOK_CLIENT_ID`, `OAUTH_FACEBOOK_CLIENT_SECRET`, `OAUTH_FACEBOOK_REDIRECT_URI` (callback: `/api/auth/social/facebook/callback`)

Register matching HTTPS callback addresses with each provider. After local sign-in, choose **Link GitHub** or **Link Facebook** under account identities. OAuth state and cookie are validated once, and an immutable subject is retrieved from the provider's HTTPS API. Linked subjects are stored in the existing `oidc_identities` table. Subsequent social sign-ins require an approved, active local account. Accounts using local TOTP must continue logging in locally with MFA, to prevent bypass.

## Limitations
Pending state is process-local and not suitable for multi-replica deployments. There have been no live provider, PostgreSQL or end-to-end browser tests, and a full build is unverified. This does not provision new accounts. Facebook requests include `appsecret_proof` and GitHub uses its official `/user` endpoint. Validate provider terms, secret handling, deployment security and account-revocation workflow before production.
