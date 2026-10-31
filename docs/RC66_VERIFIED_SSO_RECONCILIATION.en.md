# Quorivio 0.1.0-dev — RC66 — GitHub-verified SSO reconciliation (31 October 2026)

**Latest maintainer commit:** `487c960f09b3c9adb996d489f44b52d059da12b2`. Standard CI `41191213305` and full opt-in campaign `41191751069` PASS (11/11 required checks on the same source); no image publishing. Scoped PostgreSQL SSO link/revocation and account-scoped identity-management HTTP acceptance were both verified in job `124509777927`; this is distinct from the previously accepted protocol-only `C3-AUTO` gate. Split partial C3 weight 4→2 and accepted new `C3-PG-IDENTITY` weight 2; total gate weight remains 100.

**New verified progress: 82.75%** (39 accepted, 17 partial / 56 gates; +1.00 point from 81.75%). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. RC strict is NOT ready: real Google/GitHub/Facebook consent and redirects, public TLS, physical RWX multi-machine storage, human accessibility and independent security/GDPR/AGID sign-offs remain open. All original dated receipts are immutable. No assistant commit, tag or push. Next package uses this commit as base.

---
