# Quorivio 0.1.0-dev — RC68 — Verified private presenter background ownership (31 ottobre 2026)

**Maintainer-committed baseline:** `487c960f09b3c9adb996d489f44b52d059da12b2`. Standard CI `41191213305` and extended RC campaign `41191751069` succeeded on the same code; publication skipped. User has not declared a new commit for RC66–RC68. No assistant commit, push or tag.

**Evidence-scoped reconciliation:** production-quality job `124509777927` ran `tools/ci_background_library_postgres.py` using authenticated HTTP and disposable PostgreSQL 18. It proved presenter PNG upload, reuse among owned sessions, non-collaborator denial, offered access to a collaborator, independent ownership on copy and original access revocation. Gate `C4-PRIVATE-BACKGROUNDS` is distinct from already-accepted `C4-PROFILE` profile photos and `C4-AV-INSTREAM` raw ClamAV scanning. Parent C4 weight shrinks 2 to 1 while new accepted gate is weight 1, adding 0.50 percentage points.

**Verified RC progress: 84.25%** (41 accepted, 17 partial of 58 gates; +0.50 over RC67). Total weight 100. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. **No claim of real multi-node CSI/NFS RWX storage, managed HTTP-upload ClamAV, assistive-device testing, independent GDPR/AGID/security approval.** New package still needs the next GitHub CI.

## Next acceptance

Run standard and extended CI after a manual commit. No publication; independent physical RWX/ClamAV and operational approval remain outstanding.
