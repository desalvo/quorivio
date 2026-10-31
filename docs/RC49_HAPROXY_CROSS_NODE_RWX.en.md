# Quorivio 0.1.0-dev — cycle 49: verified HAProxy and cross-node RWX acceptance tool

## Verified GitHub evidence

- **Maintainer-confirmed baseline:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (cycle 48).
- **Standard CI:** run `41120048115`, quality job `124284164769` and container build `124285663501` succeeded.
- **Extended CI:** run `41123318359` completed with all 11 jobs succeeding. Real HAProxy Technologies job `124297991439`, NGINX multiworker `124297991261`, real Kubernetes API dry-run `124297991263`, OCI AMD64/emulated ARM64 `124297991308`, Firefox/WebKit `124297991462`, rootless Podman `124297991557`, single-node KIND `124297991520`, real ClamAV `124295253787`, quality `124295253885`, container `124297991450`, opt-in publication `124298997000`.
- **Formal RC adjustment:** accept distinct `B4-HAProxyTECH-KIND` (weight 1) by splitting the B4 parent (weight 2 → 1 partial). **81.25%**; **36 accepted and 17 partial gates** of 53. NGINX, OCI, browser and other already accepted gates are not credited again.

### HAProxy proven scope

Disposable two-worker KIND, strict separate worker scheduling, PostgreSQL 18 and CI-host shared bind mounts, actual HAProxy Technologies controller, matching HTTP host routing, rejection of unrelated host, both API origins, single pod replacement and restored availability. **Not proof** of independently hosted CSI/NFS RWX, geographically/physically separate machines, public TLS, long-term capacity, or production SLOs.

## New RWX operational data-path probe (not executed against a real user cluster)

`tools/k8s_rwx_cross_node_probe.py` reads Deployment/pods/PVC/PV through explicitly selected `kubectl` context, refusing hostPath/local storage, unbound/RWO claims, read-only/subPath mounts, unready replicas or replicas on the same node. It never requests Secret objects or application data.

Read-only API validation:

```sh
python3 tools/k8s_rwx_cross_node_probe.py --context YOUR_CONTEXT \
  --namespace quorivio --deployment quorivio --mount-path /app/assets
```

Only after authorized operator approval, enable the two-way A→B and B→A small temporary file write/read/fsync exchange, with best-effort cleanup on both pods:

```sh
python3 tools/k8s_rwx_cross_node_probe.py --context YOUR_CONTEXT \
  --namespace quorivio --deployment quorivio --mount-path /app/assets --confirm-write
```

`API_CONTRACT_ONLY_NO_IO` is **not** proof of data exchange; `CROSS_NODE_RW_EXCHANGE_PASS` is bounded two-way I/O evidence, not durability or HA. If both pods disappear during cleanup, a private `.quorivio-rwx-probe-*` directory might remain. Investigate that scoped directory manually before retrying.

**Still open:** real independent physical nodes with CSI/NFS RWX, storage disruption and recovery, trusted public TLS, representative sustained 500-person load and SLOs, actual devices, external WCAG/AGID, GDPR and security review. The new probe gets no additional RC credit until real authorized validation is performed and reviewed. No commit/push/tag/release is performed by the assistant.
