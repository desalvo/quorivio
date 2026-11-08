# RC269 — LDAP/LDAPS, housekeeping, primary ownership and sidebar

## Features

- When an authenticated API call receives HTTP 401 with `authentication_required` or `session_revoked`, the browser immediately reloads the login page. Binary upload/import paths share the guard; public audience routes and login attempts are excluded.
- Every **12 hours** and once after startup, reclaim old idle conversion workspaces and persistent asset files **unregistered** in `session_assets`, only if older than 12 hours. Registered session media, background library, profile pictures and unknown paths are preserved. DB errors fail closed.
- Primary session owners may transfer ownership to another approved presenter in the same organization, with transactional update, audit record, and optional previous-owner collaborator retention.
- Opt-in LDAP/LDAPS with TLS verification, STARTTLS support, service-bind search, actual end-user bind, group→role mapping and existing Quorivio MFA. Never silently link an LDAP identity to a local account by email; an authenticated local user may explicitly link an identity from their Profile using the LDAP password. Automatic provisioning disabled by default.
- Blank thumbnail sidebar context menu only on right-click or mobile long-press (650 ms), never left click. Reordering remains unchanged.
- Phone editor response option labels have a readable 17px minimum; QR and page number remain unchanged.

## Kubernetes

Use the standalone wizard in offline mode for a NEW generated manifest set and set `ldap_enabled=true`, `ldap_url=ldaps://...`, `ldap_bind_dn`, `ldap_base_dn`; keep `ldap_bind_password` in a private 0600 override JSON, not in shell history. It emits `LDAP_BIND_PASSWORD` in the Kubernetes Secret, never the ConfigMap. `ldap_starttls=true` applies to `ldap://` only. The configurable user filter, directory ID and mail attributes, group DNs, provisioning organization, and optional CA file path are described in the Italian guide. **A CA path does not mount a file by itself.** Avoid regenerating and applying an existing cluster's Kustomize folder without reconciling converter and PostgreSQL overlays. New single-replica ReadWriteOnce deployments use strategy `Recreate`; :latest pulls use Always.

## Validation limitations

New negative/safety tests cover TLS/filter handling, orphan cleanup, primary-ownership endpoint contracts, UI and wizard output. Real LDAP directory end-to-end authentication and Kubernetes rollout require an environment to test; CI validation remains pending. Runtime dependency: `ldapts` 9.2.x, Node >=22. **Completion unchanged: 85.25%**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag.
