# RC126 — Historical CI contracts adapted to native Docker publication

## Observed failure (GitHub Actions run 41371521619)

`Production quality gate` completed its TypeScript, Vite, PostgreSQL, Chromium and vulnerability checks, but the late Python `Kubernetes wizard and worker integration tests` ended `FAILED (failures=8)` after `Ran 1656 tests`. Failure IDs: `test_ci_browser_bootstrap.BrowserBootstrapTests.test_hosted_ubuntu_runner_uses_preinstalled_browser_without_apt`, `test_ci_integration.CiIntegrationTests.test_converter_build_and_scan_are_gated`, `test_ci_rootless_podman_smoke.RootlessPodmanSmoke.test_ci_is_explicitly_opt_in_and_cannot_publish`, `test_image_defaults.ImageDefaults.test_ci_publish`, `test_manual_docker_publish.ManualPublishPolicy.test_publish_runner_has_no_write_permission`, `test_manual_docker_publish.ManualPublishPolicy.test_workflow_is_never_push_based`, `test_rc76_editor_contracts_preflight.RC76EarlyContracts.test_release_remains_opt_in`, `test_rc_cycle59_campaign.CampaignContracts.test_workflow_is_explicit_and_does_not_publish`. Their prior static string expectations belonged to the retired single-job Docker workflow. A downstream required campaign summary failed and native OCI/publish jobs were skipped; neither QEMU nor Docker Hub was reached.

## Fix scope and safety

Seven historical Python test files are reconciled with RC125's two native images and separate manifest publishers. Parsed YAML job checks avoid leaking subsequent publisher contents into rootless Podman smoke boundaries. All critical controls remain mandatory: manual `workflow_dispatch` opt-in and no RC campaign publishing; optional commit mode only with literal `[publish-docker]` plus successful complete campaign; `validate` and scanned `image-build` before native digests; native architecture matrix, production environment and read-only GitHub permissions; two digests prior to tagging; no QEMU build for publication. Tests retain substantive policy and failure checks rather than accepting arbitrary renamed jobs.

An early pre-npm step re-runs all impacted legacy suites together with RC125 digest checks. The full late integration suite is still required, rather than bypassed. Real ARM64 runners, Docker Hub remote push and multiarch index remain unverified by this local patch. Do not attribute new production readiness or gate progress to CI test maintenance.

**Certified completion:** 85.25% (43 accepted, 17 partial gates of 60), provisional local 85.75% pending substantive acceptance. **Suggested commit:** `Align legacy CI contracts with native multiarch publication and gate both digest builds [full-ci]`.

Local regression evidence: 57 targeted Python tests run: 56 passed and one environment-dependent skip; the complete local discovery attempt timed out and must be verified on GitHub.
