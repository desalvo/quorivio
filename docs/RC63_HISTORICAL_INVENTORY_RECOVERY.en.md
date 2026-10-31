# RC63 — Historical CI manifest recovery (31 October 2026)

**Last maintainer-confirmed commit:** `8e7d2df0f3badb39136f9901cd91acf2897ca453` (includes RC62). Standard GitHub CI run `41187779633`, job `124498103225`, passed the previous HTTP 429 issue, Node unit tests, full build, real PostgreSQL integrations, and npm vulnerability check. It failed in `tools/ci_inventory_reference_guard.py` because the cycle 59 source checksum receipt was absent from the committed tree. This prevented the Python/Kubernetes test step from running.

**Root cause:** the cumulative RC61 archive accidentally dropped original cycle 59 and 60 inventory receipts while retaining the workflow references and historical verifiers. RC62 did not restore them.

**Resolution:** recover the original RC59 and RC60 JSON inventory receipts byte-for-byte from their original cumulative archives, pin SHA-256 in the CI reference guard, add automatic presence/absence regression tests, and add a current RC63 inventory verification in the standard workflow. No historical manifest is rewritten.

**Limits:** Local source/ZIP verification does not substitute for the next post-commit GitHub CI. Strict RC remains blocked; certified RC score stays at 81.75% (38 accepted / 17 partial of 55). No assistant commits, pushes, tags, or publishing.
