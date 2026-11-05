# RC199 — Early release header CI guard and package closure

## Failure reproduced

User-committed RC198 (`0375877`) failed on GitHub Actions run [42094437419](https://github.com/desalvo/quorivio/actions/runs/42094437419), Production quality gate job `127480690817`, at **Validate active RC release headers against the current inventory**. The actual locally reproduced exception was:

```text
ValueError: DEVELOPMENT_STATUS.md: missing one or more explicit release flags
```

Both `docs/DEVELOPMENT_STATUS.md` and `.it.md` introduced RC198 current summaries before the first `---` but did not explicitly repeat all three required release flags. The handoff files already contained them. The historical sections cannot satisfy this guard, by design. CI stopped before TypeScript/browser/PostgreSQL acceptance; this run does not establish a runtime or formatting regression.

## Change set

- RC199 is the current cycle in all four bilingual status/handoff headings, with the explicit and unchanged safety controls `rc_strict=false`, `publish_image=false`, `publish_latest=false` and ledger-derived **85.25%** / **85,25%**.
- Preserve previous RC198/RC197 status entries verbatim as historical evidence. Preserve the historical RC198 receipt and verifier; only move its workflow command to `--historical` and activate RC199.
- Add a negative regression fixture that reproduces an RC198-style status summary with missing flags while the other three headers are valid. The shared guard must fail before slow CI jobs.
- The RC199 checksum verifier also checks **the four headers embedded in the final ZIP**, not just the unpacked working tree; this prevents a stale, otherwise hash-consistent archive from being distributed.

## Acceptance and release policy

Run the shared early preflight, its focused tests, and the current source plus packaged SHA-256 checks before proposing the cumulative ZIP. Confirm GitHub Actions full CI separately. No strict release or publishing policy changes; no commit/push/tag by assistant. Certified completion **85.25%** (43 accepted, 17 partial), no gate promotion.

Suggested post-RC198 single-line commit: `Fix RC199 active release headers and validate packaged CI metadata`.
