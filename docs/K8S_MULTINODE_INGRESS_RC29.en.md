# Quorivio RC cycle 29 — multiworker and real NGINX ingress (30 October 2026)

**Local regression:** 1,193 Python tests executed, one skipped, no failures. npm production build and live KIND were not run locally.

## Verified results

After the cycle-28 maintainer commit (`016beea25d5e2d2fab21b0730aa15baf0b573e12`), GitHub Actions confirmed **SUCCESS** for OCI AMD64+QEMU ARM64 actual startup (`40980312270`, job `123820527902`) and **rootless Podman with PostgreSQL 18** (`40982728705`, job `123827805762`). This does not certify physical ARM64 hardware.

These independently verified scopes justify separating 0.5 weight from the still-partial D3 gate into a narrowly accepted automated runtime subgate. Formerly 0.25 of those points was credited as partial; now 0.5 is credited as accepted. Thus **RC 79.00% → 79.25% (+0.25 percentage points)**. Matrix: 48 gates, 31 accepted, 17 partial. No unexecuted test was promoted.

## Cycle 29 development

- **Kubernetes wizard:** opt-in `enforce_node_diversity=true` requires two replicas and `ReadWriteMany`, adds hostname `DoNotSchedule` spread with `minDomains: 2`. Default remains compatible with single-node KIND.
- **Public origin:** HTTP ingress with TLS disabled generates `PUBLIC_BASE_URL=http://...`; TLS ingress keeps HTTPS. Production should use TLS.
- **Helm:** optional `enforceNodeDiversity`, rejects replicas >1 without RWX, adds maxUnavailable=0 rolling strategy and a PodDisruptionBudget. Does not provision shared storage; scheduling can intentionally remain Pending without two eligible nodes.
- **New opt-in CI:** `kubernetes_multinode_test=true` creates a disposable KIND cluster with two workers, real PostgreSQL 18, non-published Quorivio image, strict separate worker placement, cross-worker file visibility, actual NGINX controller, HTTP ingress Host routing/rejection and pod replacement recovery. Script `tools/ci_k8s_multinode_ingress_smoke.py`.

**Critical limits:** KIND uses one Docker host and a shared bind mount, NOT independent physical machines or real NFS/CSI RWX. Not HAProxy, public TLS, multizone/control-plane HA, real storage failover, physical ARM64, AGID/GDPR assessment or SLA. The new Kubernetes multi-worker job has NOT been executed on GitHub yet. Local source contracts do not count as live cluster acceptance.

## Workflow after commit

Dispatch `kubernetes_multinode_test=true`, optionally plus `kubernetes_manifest_test=true` and `kubernetes_runtime_test=true`; keep `publish_image=false` and `rc_strict=false`. For a quicker diagnosis run the new multi-node job only. Publishing requires explicit maintainer opt-in.

**Strict RC remains blocked** by 17 partial gates and independent reviews. No assistant commit/push/tag/publication.
