# RC230 — Correct active CI inventory after RC229

## Failure

GitHub Actions run `42230115609` on SHA `41a0339e9cc0ac6f52c7f7d28d322e2c9229fa66` failed at the step "Validate active RC release headers against the current inventory". The guard resolved the workflow’s last nonhistorical verification command as RC227, while the current documentation was RC229. Therefore `verify_rc_release_status.py` rejected the first active release heading. The acceptance-summary failure and skipped jobs were downstream effects, not independently proven runtime failures.

## Correction

- Retain the original RC227, RC228 and RC229 manifests unchanged and reference their verification scripts with `--historical`.
- Make exactly one last nonhistorical inventory command in the CI workflow: `verify_rc_cycle230_inventory.py`.
- Change four active release headings to RC230 while preserving archived historical sections and release safety flags.
- Include a new current SHA-256 catalog and a pre-npm regression asserting that the chosen current verifier agrees with all active headers and that deliberately stale RC227 headers are rejected.
- Preserve the unmodified application source and the certified completion score (85.25%, 43 accepted, 17 partial).

## Acceptance

Run `PYTHONPATH=tools python3 tools/verify_rc_release_status.py`, `python3 tools/ci_inventory_reference_guard.py`, `PYTHONPATH=tools python3 tools/verify_rc_cycle230_inventory.py`, `python3 -m unittest tools.tests.test_rc230_inventory_promotion tools.tests.test_rc199_release_headers -q` in a clean tracked checkout. After a user commit, confirm the full GitHub Actions campaign independently; do not declare it green on local checks alone.

The release remains `0.1.0-dev`, with `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push, tag or Docker publication by the assistant.
