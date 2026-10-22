# Operations and release checklist
- Configure public TLS endpoint and set `PUBLIC_BASE_URL` to its actual HTTPS URL; keep secret credentials outside Git.
- Check PostgreSQL migrations/schema creation and restore strategy; test restoring backups periodically.
- Require CI test, compilation, vulnerability scan and container build gates; verify published digest and labels.
- Test with smartphone audience, reconnects, simultaneous votes, multi-tenant authorization and reverse-proxy WebSockets.
- Kubernetes wizard emits manifests only, does not apply them; review generated Secrets references, TLS, ingress and resources.
- Do **not** classify this development package production-validated before real integration, load, backup and restore exercises.
