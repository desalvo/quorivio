# RC gate score CI regression — 2026-10-27

## Incident

- Last maintainer-confirmed commit: `551396cdaafb8765140355557eae8f8ceb59c8d4`.
- GitHub Actions push run: `40522786396`, quality job `122254095095`: **FAILED** in `Kubernetes wizard and worker integration tests` (the step runs the whole Python test suite).
- Exactly one of 817 Python tests failed: `test_rc_gate_audit.RcGateAuditTests.test_weighted_ledger_is_normalized` compared the **actual 53.0** RC score against the obsolete hard-coded **48.0**. All other 816 tests passed. The downstream container build was skipped; routine publication was skipped.

## Correction

- The gate audit regression test now derives expected scores from the current ledger's gate weights and statuses, verifies the 100-point budget, per-area subtotals and exact unaccepted gate IDs, and uses synthetic mutable ledgers to test legitimate progress as well as invalid statuses and weights.
- The release preflight test likewise computes its expectation from the live ledger rather than freezing 53.0.
- The dated RC evidence milestone retains the already-proven minimum 53.0 and source traceability, but explicitly allows later independent review to raise an eligible partial gate to accepted and eventually reach 100.0. A milestone's historical evidence remains required.
- Production code, PostgreSQL schemas, Docker and manual publishing policies are unchanged.

## Verification and honesty

- Full local Python suite **819/819 PASS** (two additional independent audit tests).
- RC-focused suite **310/310 PASS**, before the extra milestone relaxation; the new milestone targeted tests then also passed.
- `python tools/rc_gate_audit.py`: **53.0**; `python tools/rc_release_preflight.py`: **release_candidate_ready=false** and no missing required files.
- New GitHub CI has **not yet been executed** for this hotfix. No promotion of gates or claims of full CI success.

## Next

Commit this test-only fix and run the ordinary push CI. Do not re-publish production images for a test-only correction.
