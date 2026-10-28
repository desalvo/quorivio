# RC acceptance cycle — timed rehearsals and bounded security/documentation checks

**Date:** 2026-10-28. **Version:** 0.1.0-dev. **Last maintainer-confirmed commit:** `a32ef78902a656262d346a0fa622604a4deda405`.

## Implementation (uncommitted; new CI pending)

* Timed-quiz rehearsal now renders a shared countdown, with time beginning on entry to the preview page. Switching presenter/participant/dual modes does not reset the deadline. Page navigation and **Ricomincia prova** begin a new trial.
* One-shot answer submission checks the actual wall-clock deadline in its handler, independently of button disabled state; late answers cannot enter presenter statistics. Already submitted answers remain counted after expiry.
* The standalone Timer widget uses the rehearsal clock. The participant's quiz options and simulated submit button disable at the deadline with an announced expiry status. Independent question blocks share the widget deadline.
* Added TypeScript regression cases, a real offline Chromium acceptance (1440/390 px) on the actual TypeScript timer policy, and opt-in GitHub browser CI wiring. This is **not** an authenticated full-app browser test or hardware/screen-reader acceptance.

## Proven 63% → 65% RC reconciliation, based on earlier green CI only

`D4-SCAN` is **accepted, weight 2**, separated from partial `D4` (weight 5→3): Green full CI [40638652838](https://github.com/desalvo/quorivio/actions/runs/40638652838) on SHA `a32ef78902a656262d346a0fa622604a4deda405` passed npm high/critical vulnerability scanning, credential-leak checks, image build and security scanning. **Not** external pentest, AGID review or threat-model signoff.

`D5-TECHDOC` is **accepted, weight 2**, separated from partial `D5` (weight 5→3): the same green CI passed required nonempty EUPL license, README EN/IT, GDPR EN/IT and generated admin/user PDF manuals EN/IT. **Not** a bilingual editorial review, accuracy of screenshots or documentation usability signoff.

Weights still sum to 100; formula unchanged (accepted 1, partial 0.5, others 0). **30 gates: 13 accepted, 17 partial; score 65.0%; strict RC NOT READY.** The newly changed timed rehearsal contributes **zero points** until CI checks the new commit. The overall program still requires Firefox/WebKit, independent visual parity, real screen readers, physical devices, OAuth providers, RWX/ClamAV/Kubernetes/Podman, operational DR, and external legal/security approvals.

## Local evidence

Web/API production builds and Node/Python tests must pass; the Chromium fixture exercises exact boundary time, no late submit, reset, and preservation of presenter results. Manual workflow: `browser_test=true`, `publish_image=false`. Never infer publication from a successful container-build job.
