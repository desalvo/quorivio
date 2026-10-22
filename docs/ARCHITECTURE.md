# Architecture decision log · ADR-0001

**Status:** prototype. Single modular Node service and React/Vite frontend avoid premature microservices. PostgreSQL is authoritative for users, sessions, activities and responses. WebSocket is an ephemeral notification plane, not the durable results store. Per-user permissions are rechecked during the WebSocket handshake; participant subscriptions must only contain redacted current-activity data. All submitted answers are checked on the server, inside DB transactions. Unique `(activity_id, participant_id)` makes retries idempotent.

## Planned scale-out

Use Redis pub/sub or PostgreSQL LISTEN/NOTIFY for broadcasts across replicas, shared rate limits, replay-safe session events and session-presence metrics. Exports and presentation conversion move to isolated workers. S3-compatible storage and Keycloak are options, not requirements for current runtime.

## Identity federation

OIDC/SAML 2.0 with Keycloak is the preferred integration path; Google, Facebook, GitHub and generic OIDC are future tasks contingent on actual provider configuration, compatibility and authorized tests. No provider endpoint, credentials or verified generic OIDC claim is asserted. Accounts must never auto-link on unverified email alone.

## Licenses

Project license is to be determined. Relevant dependency families commonly have MIT/ISC/BSD/Apache licenses but **specific versions and complete transitive licenses have not been independently audited**. Before distribution or commercial operation generate an SBOM, inspect installed package notices and confirm all versions/registries and container image licenses. Google Fonts are an optional external cosmetic load; for fully offline operation bundle verified open-licensed fonts or rely on system fallback. PostgreSQL is open-source PostgreSQL License.
