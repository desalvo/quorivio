# RC302 — Joint authorized Docker Hub publication

**Baseline:** RC301 merged on `main` at `d18b14129afe8850b5df549213e5d56ba03a47b3`, full CI `42901855073` green. Earlier app-only publish `42897981990` succeeded; converter publication was separate until RC302.

## One approval, two verified images

The same explicit publication authorizes matching tags for two repositories:

- `desalvo/quorivio:sha-<12>` and `desalvo/quorivio:latest`
- `desalvo/quorivio-converter:sha-<12>` and `desalvo/quorivio-converter:latest`

The existing `[publish-docker]` marker on a `main` commit requires successful full automatic RC campaign acceptance; explicit manual `workflow_dispatch` with `publish_image=true` still requires quality and container gates. Unmarked pushes, pull requests, standalone RC acceptance runs and `[full-ci]` do not publish. The original converter-only manual workflow remains for exceptional recovery.

Native AMD64 and ARM64 runners each build both images and push by immutable digest with SBOM and provenance; no QEMU release build. Separate digest records are uploaded together. The publisher validates both native converter images, labels and authorization **before** moving either mutable tag. It then publishes and inspects the application and converter multiarch manifests. Existing quality gate builds and Trivy scans both images.

**Registry limitation:** Two separate Docker Hub repositories cannot be updated as one atomic transaction. A registry failure after the app manifest is written may leave the converter pending; the job fails and requires retry/verification. Failures in preflight never alter mutable labels.

**Release boundary:** This is a publishing infrastructure improvement, not a production security assessment or independent physical accessibility sign-off. The ledger stays **85.25% (43 accepted, 17 partial)**; strict RC cannot be declared ready without operator evidence. App version remains `0.1.0-dev`, no Git release tag created.

**Suggested merge commit:** `ci: publish app and converter together after verified full CI [publish-docker]`
