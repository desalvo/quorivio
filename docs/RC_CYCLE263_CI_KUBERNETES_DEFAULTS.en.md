# Quorivio RC263 — Poppler CI fixture and Kubernetes PostgreSQL probe defaults

- Full CI RC262 (`42495326713`) failed because two synthetic subprocess mock tests checked actual Poppler executable availability on the runner. Tests now mock binary discovery as well as subprocess rendering. Production conversion still rejects missing dependencies.
- Kubernetes defaults `terminationMessagePath: /dev/termination-log` and `terminationMessagePolicy: File` on persisted Container objects. RC262 compared the entire live object with the constructed probe and incorrectly rejected reconciliation after a successful rollout. RC263 strips ONLY these defaults, with exact value checks; image, command, env, secrets, volumes, resources, security and unknown properties are still strictly compared.
- If RC262 `--apply-disk-monitor` rolled out successfully but then refused manifest drift, **do not apply again**. Confirm the live `db-disk-probe` sidecar and a successful StatefulSet rollout. Then use RC263 `--sync-disk-monitor --generated-dir ./k8s-generated --set namespace=quorivio --set name=quorivio`. This does not patch the Kubernetes cluster or restart PostgreSQL.
- `--version` is offline. The standalone self-updating wizard uses official GitHub main, retaining its locally newer version until published. `--no-self-update` explicitly bypasses the update check.
- Validate reconciliation using `kubectl kustomize ./k8s-generated > /dev/null`.

No production application or database credentials have been changed.
