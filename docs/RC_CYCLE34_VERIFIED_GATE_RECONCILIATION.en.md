# Quorivio 0.1.0-dev — RC cycle 34 — Verified 80.25% (+1.00 pp)

Maintainer commit: `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`. Green GitHub Actions: https://github.com/desalvo/quorivio/actions/runs/41048187760 (quality, container build, real ClamAV, two-worker NGINX KIND). Image publication skipped.

Credited bounded evidence only: C4-AV-INSTREAM (1 weight) from C4, and B4-KIND-INGRESS-RECOVERY (1 weight) from B4. Both parents remain partial, weights sum to 100, score moves 79.25 to 80.25; 50 gates = 33 accepted, 17 partial. ClamAV runtime proof job 124037870523; KIND multiworker ingress/failover job 124038997005. The same capacities previously in B4-LOAD and D4-SCAN are not claimed again.

New, not-yet-GitHub-verified change: ClamAV scan uses O_NOFOLLOW/O_NONBLOCK pinned regular inode, scans through the same open file handle, and rejects concurrent file mutation by rechecking file metadata after scan. Locally tested; no score claimed.

Limits: KIND is on one Docker host using a shared bind, not production CSI/NFS RWX or multi-machine HA. ClamAV checked direct application INSTREAM client, not concurrent HTTP uploads through deployed managed scanner. Real HAProxy, public TLS, physical ARM64, human screen readers, devices and independent AGID/GDPR/security signoffs remain required. Strict RC blocked. No assistant commits or publication.

Local regression cycle 34: backend Node 492/492; frontend Node 65/65; Python 1,243 executed (1 skipped, zero failures) in eight non-overlapping groups; scanner-focused 12/12. Source/ZIP SHA-256 validated. Fresh TypeScript/Vite build not verified locally (missing npm dependencies). Re-run standard and opt-in CI after maintainer commit; do not assume that new scanner source has real ClamAV CI proof.
