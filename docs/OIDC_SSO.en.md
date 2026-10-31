# OIDC SSO — federated authentication (development)

## RC61 status update

The authenticated "SSO / Identities" dashboard now lists linked providers privately and supports confirmed unlink with a current local password. API endpoints: `GET /api/auth/identities` and `POST /api/auth/identities/unlink`. OAuth flow state is one-shot and shared in PostgreSQL across replicas; revocation is rechecked at linking callback. New PostgreSQL HTTP unlink acceptance is staged in CI, not yet executed. Real identity-provider and operator testing remain pending. Older notes below describe the first implementation, not the current RC61 acceptance status.


Quorivio includes a first OpenID Connect Authorization Code + PKCE S256 flow with one-time state/nonce, an HttpOnly SameSite=Lax callback cookie and RS256 verification using provider JWKS. Identities are anchored to `(provider, sub)` and must be explicitly linked by an already authenticated, approved local account. A verified email address alone never auto-links identities. Accounts with TOTP enabled must continue using local password + MFA; OIDC login is rejected for these accounts to avoid bypassing the second factor.

## Setup

Configure `OIDC_GOOGLE_ISSUER`, `OIDC_GOOGLE_CLIENT_ID`, `OIDC_GOOGLE_CLIENT_SECRET`, `OIDC_GOOGLE_REDIRECT_URI`, or the corresponding `OIDC_PROVIDERS_JSON*` or `OIDC_CUSTOM_*` variables. Register an exact HTTPS callback ending `/api/auth/oidc/<provider>/callback` with the identity provider and use the provider's documented exact issuer. Configured providers appear in the login UI and in the authenticated account-link UI. Public endpoint: `GET /api/auth/oidc/providers`. Additional endpoints: `/start`, `/start?link=true`, `/callback`.

## Outstanding safety and functionality work

- State/PKCE verifiers currently use a process-local cache: multi-replica operation requires a shared atomic cache.
- ID token claims and RS256 signatures are checked locally, but real IdP integrations and PostgreSQL migrations have **not** been run.
- No TOTP step-up for federated logins, unlink UI, production audit, dynamic provider administration, SAML or production browser tests.
- GitHub OAuth and Facebook Login require provider-specific OAuth implementations or an OIDC broker; neither is claimed implemented.
- generic OIDC requires a working registered OIDC client with its actual issuer and has not been validated on the live federation.
- Secure deployment requires public TLS, distributed throttling, secret rotation, auditing and penetration review.
