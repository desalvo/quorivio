# Quorivio — extended CI and scanner hotfix


## 2026-10-28 — Extended GitHub CI 40709447219 and SHA-256 secret-scanner regression

**Verified upstream:** main commit `ac4b4e23c90afe44b3fa8d2deb0177222af8f16c`, GitHub Actions run `40709447219`, job `122891045579` (failed). The failed step labelled “Kubernetes wizard and worker integration tests” actually failed while executing `PYTHONPATH=tools python3 -m unittest discover -s tools/tests -v`: **965 tests, five `KeyError`** exceptions. Four tests read `pending_local_batch.new_feature_promoted`; one reads `pending_local_batch.new_ci_required`. The preceding TypeScript build and PostgreSQL integration completed far enough to reach the Python gate. The step label does NOT imply a proven Kubernetes provisioning defect.

**Fix:** restore both backward-compatible JSON keys with strict semantics (`new_feature_promoted=false`, `new_ci_required=true`) and retain all 32 weighted RC gates, with no new acceptance. Add regression tests for those keys, actual evidence score and fail-closed handling. This is a documentation/CI contract fix, not new evidence for any RC gate.

**GitGuardian:** all five reported incidents were shown under `docs/validation/RC_PUBLIC_STAGE_FILE_INVENTORY_20261028.json`. One incident's displayed `Password` prefix was confirmed as the stored SHA-256 checksum of `docs/validation/RC_PASSWORD_RECOVERY_AUTH_GATE_66_20261028.json`, not a password. The other four specific values were not individually shown. Convert all 746 historical file hashes and the baseline archive checksum losslessly into eight ordered groups of eight lower-case hex characters. Add a strict checksum validator with explicit source-baseline vs post-stage checks and CI regression tests; preserve GitLeaks action and existing security policy. Previously raised incidents may remain visible because the Git history remains unchanged; do not automatically dismiss unverified secrets.

**Verification:** real source ZIP (740 files) and original public-stage ZIP (746 recorded files) independently rechecked against the grouped checksums. TypeScript backend/frontend/Vite build PASS, Node backend 474/474 PASS, Node frontend 58/58 PASS, targeted RC Python 24/24 PASS. Fresh full Python suite **971/971 PASS**; prior interrupted local attempt is not counted. No fresh GitHub full CI or external security/browser acceptance occurred after this code correction.

**RC readiness:** 32 gates, 15 accepted, 17 partial, **67.0% → 67.0% (+0.0 pp)**. Strict RC release remains blocked. Report: `docs/validation/RC_CI_40709447219_AND_GITGUARDIAN_HOTFIX_20261028.json`. User must commit and rerun GitHub Actions with `browser_test=true`, `publish_image=false` when ready. Do not publish Docker or change the version `0.1.0-dev`.
