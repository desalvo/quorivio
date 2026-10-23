# Kubernetes wizard-generated secrets

The wizard generates a PostgreSQL password **only for an internal database**, the initial administrator password and `AUTH_SECRET` for authentication and encrypted application settings. Supply `admin_email` for the initial administrator; replace the example default before deployment. The admin account is forced to change its initial password.

Generated values are saved in `quorivio-overrides.json` and reused on subsequent runs in the same output directory. The `05-app-secret.yaml` Kubernetes Opaque Secret contains base64-encoded values, **not encrypted values**. Both files are created with 0600 permissions; the manifest is listed in `kustomization.yaml`. Keep them out of Git and store secure backups. Regeneration in a different output directory generates new credentials. Rotating AUTH_SECRET can invalidate existing encrypted application settings; rotating an initialized PostgreSQL user's password requires a coordinated DB change.

For **external** PostgreSQL, provide its existing password using protected `--values` or the saved override. The wizard cannot invent credentials for an existing remote database. External database TLS/certificates remain operator responsibilities. Passing secret strings via `--set` risks exposing them in shell history or process listings; prefer a 0600 protected JSON `--values` file.

Example: `python3 tools/k8s_wizard.py --unattended --output ./k8s-generated --set admin_email=admin@example.com`. Ingress default TLS and node selectors are preserved.
