# RC51 — Kubernetes HTTPS acceptance protocol

Quorivio **0.1.0-dev**. Locally verified: keyword-only callsite checks, simulated complete KIND controller flows for NGINX and HAProxy Technologies, real Node TLS client vs disposable loopback server. **No actual new KIND HTTPS execution has been verified in GitHub CI**: official RC remains **81.25%**.

After maintainer commits cumulative cycles 49–51, run standard CI then manually dispatch extended with `kubernetes_tls_test=true`, `publish_image=false`, `rc_strict=false`. Require both controller jobs to pass strict TLS/SNI trust, wrong Host 404, untrusted-chain refusal, both pod clients, pod replacement and post-recovery live probe. Source: `tools/ci_k8s_multinode_ingress_smoke.py`; regressions: `tools/tests/test_rc_cycle50_https_tls.py`, `tools/tests/test_rc_cycle51_https_route_contract.py`.

Only a disposable KIND host bind is used. Not evidence of public PKI, independent machines with CSI/NFS RWX, network partition tolerance, sustained 500-user SLO, actual hardware devices, independent penetration testing or regulatory compliance. Bounded B4 TLS credit is conditional on two successful CI jobs; no additional points from local-only tests.
