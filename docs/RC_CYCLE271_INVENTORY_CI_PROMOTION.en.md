# RC271 — CI repair: inventory promotion and RC270 coverage

## Verified root cause

The committed RC270 full CI [42535872914](https://github.com/desalvo/quorivio/actions/runs/42535872914) stopped in `RC230 inventory promotion guard before npm`: the current four status/handoff files were headed RC270 while the workflow still treated RC269 as the current inventory. The exact failure was `COMPLETION_HANDOFF.it.md: ... does not identify RC269`. The final campaign summary consequently failed; ClamAV passed and dependent jobs were skipped.

## Fix

* Keep RC269 checksum receipt byte-for-byte immutable and invoke its verifier with `--historical`; add a SHA-256 source/ZIP/Git-index inventory verifier for RC271 as the sole current verifier.
* Promote all four status/handoff active headings to RC271; preserve ledger-derived **85.25%** without a fictional advancement.
* Add early RC270 backup/audit and Kubernetes wizard tests and a dedicated RC271 inventory/metadata promotion regression to GitHub Actions.
* No changes to application runtime, storage backends, login, audit or result rendering. Fail-closed integrity guards remain in force.

Pending: full CI after committing RC271, production backup/restore acceptance for PostgreSQL/NFS/S3/WebDAV, LDAP/SMTP and browser matrix. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag.
