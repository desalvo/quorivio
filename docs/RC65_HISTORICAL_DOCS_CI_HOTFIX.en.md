# Quorivio 0.1.0-dev — RC65 — Historical CI documentation regression (31 October 2026)

**Latest maintainer commit:** `0786ef2f4b064080dd49b42f41d2f04b3d5f4c8a` (includes RC64). Standard CI run `41189697040` (job `124503743950`) passed 546 API and 99 web Node tests, build, PostgreSQL integrations, Kubernetes, and integrity checks. The Python suite failed 2 of 1399 tests: historic RC57/58 tests required RC58 markers to appear within the first 1700/2000 characters of mutable status documents, which grow by prepending current-cycle sections.

**RC65 fix:** historical regression tests now validate complete documents and the dedicated RC58 evidence receipt, without fixed document prefixes. RC35's similar 4000-character cap has been removed proactively; RC63's latest-inventory test no longer hardcodes cycle 64. RC64 checksums are historical and immutable, RC65 is the current checksum inventory. No security gates or tests disabled; prior manifests remain frozen. The new package needs a new maintainer commit and green CI for acceptance.

**Certified RC:** 81.75% (55 gates: 38 accepted and 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. External provider verification, physical RWX, cross-device accessibility and independently signed privacy/security review remain pending. No assistant commit/push/tag.

