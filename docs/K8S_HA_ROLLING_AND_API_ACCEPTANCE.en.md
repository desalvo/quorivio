# Kubernetes HA and safe rollout — RC cycle 23

The generator now uses `maxUnavailable: 0` and `maxSurge: 1` for application deployments. With **2–20 replicas** and RWX storage, it creates a `policy/v1` PodDisruptionBudget with `minAvailable=replicas-1` and preferred (not hard) pod spreading by Kubernetes hostname. With a single replica the PDB is absent and an old generated PDB is removed on re-render. These choices limit voluntary disruptions; they cannot guarantee HA without real independent nodes and healthy storage.

## Safe secret handling

Generated `05-app-secret.yaml` and `quorivio-overrides.json` are atomically replaced at `0600`; symlink destinations and nonregular files are rejected. Existing generated credentials persist on repeated invocations. Do not place the output folder on an untrusted shared filesystem. Back up and protect the overrides file out-of-band. Never commit the generated credentials.

`--set replicas=3 --set asset_access_mode=ReadWriteMany --set max_upload_mb=150` now converts numeric fields to integers before validation. Replicas greater than one require an RWX-capable PVC and appropriate StorageClass.

## Graceful rolling drain

On `SIGTERM` the application reports readiness HTTP 503 (`status=draining`) and closes live WebSockets with code `1012` (`service_restart`), then stops accepting HTTP after a short grace interval. Kubernetes allows 45 seconds termination grace. The surviving replicas should accept fresh sockets without losing committed PostgreSQL votes. This is a code property pending real PostgreSQL E2E approval, not a production SLO.

## Verification

The standard CI now exercises an actual PostgreSQL two-replica SIGTERM/drain scenario after the 500-participant optional load test. A separate *manual* `kubernetes_manifest_test=true` KIND job runs `kubectl apply --dry-run=server` for four NGINX/HAProxy, TLS, internal/external PostgreSQL and RWX configurations. The KIND job validates Kubernetes API/schema only; it does **not** prove real ingress routing, RWX storage, ClamAV, multi-node scheduling or production HA. `runtime_arch_test=true` separately exercises OCI amd64/arm64 under QEMU. These new tests have not been run in GitHub for this cycle.

Run a real staging cluster with correct RWX, ingress controllers, TLS, and failure injection before accepting D3 or B1. Keep `publish_image=false` and `publish_latest=false` during experimental checks.
