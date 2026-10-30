# Quorivio 0.1.0-dev RC cycle 30 — operational Kubernetes preflight (30 October 2026)

This cycle introduces **non-destructive live-cluster inspection**. Unlike manifest generation and local KIND fixtures, `tools/k8s_operational_gate.py` reads real Kubernetes API objects and refuses to pass when actual pod readiness, placement and storage properties are missing.

## Scope

1. Deployment: at least two Ready/Available replicas on different nodes, latest generation observed, maxUnavailable=0, hard hostname spread and >=30 seconds termination grace.
2. PDB: matching selector, healthy replicas and at least one voluntary eviction allowed.
3. Storage: a Bound RWX PVC mounted by the app, consistent PV binding. Reject `hostPath`/`local` even if advertised as RWX; identify CSI/NFS/CephFS without implying durability or tested failover.
4. Ingress: expected Host, class, service and `/` route; require a TLS host entry when requested. EndpointSlices must show Ready endpoints on two nodes.
5. Optional external probe: HTTPS with normal certificate/hostname verification or HTTP, explicit 200 with nonempty response from `/api/health/ready`; redirects do not count.

**Wizard example:**

```sh
python3 tools/k8s_wizard.py --unattended --output ./k8s-private \
  --set replicas=2 --set asset_access_mode=ReadWriteMany \
  --set enforce_node_diversity=true --set asset_storage_class=YOUR_REAL_RWX_CLASS
# After an operator deploys to the intended cluster:
python3 tools/k8s_operational_gate.py \
  --context YOUR_KUBE_CONTEXT --namespace quorivio --app quorivio \
  --service quorivio --ingress quorivio \
  --pdb quorivio-availability --host quorivio.example.org \
  --ingress-class nginx --replicas 2 --require-tls --probe-external
```

**Helm:** for release `myrelease` use `--app myrelease-quorivio --service myrelease-quorivio --ingress myrelease-quorivio --pdb myrelease-quorivio-availability`. Use a real RWX provisioner and review the PostgreSQL HA strategy separately.

The tool only runs `kubectl get` (plus a read-only current-context query); it never applies or mutates resources, reads Secrets or collects pod logs. Omit `--probe-external` if external DNS is not reachable from the operator's environment. `--output /path/new-evidence.json` creates an immutable sanitized receipt without overwriting existing evidence. **`API_CONTRACT_PASS` does not certify actual HA or security.**

## Explicit remaining gaps

- The bundled PostgreSQL StatefulSet has **one replica**, a single point of failure; API high availability does not imply full-stack HA.
- Real CSI/NFS failover, network impairment, zone faults, RTO/RPO, prolonged load, independent ClamAV/HAProxy/AGID/GDPR/accessibility tests remain unverified.
- Cycle-29 live two-worker KIND smoke is still pending GitHub verification and uses a host bind, not production shared storage. Cycle 30 labels the disposable control plane `ingress-ready` so the pinned NGINX KIND controller can schedule, and fixes wizard CLI `--set enforce_node_diversity=true` parsing.
- Helm app pods no longer automatically mount a ServiceAccount token.

**Formal RC score unchanged: 79.25% (31 accepted, 17 partial).** Do not count unexecuted CI or external reviews, enable `rc_strict`, or publish images without full acceptance.
