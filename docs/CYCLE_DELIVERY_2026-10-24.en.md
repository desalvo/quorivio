# Quorivio 0.1.0-dev — cumulative delivery (24 October 2026)

## Scope and baseline
This package is a complete source distribution based on the user's CI-green `ci-jsx-build-hotfix-cumulative` baseline. It is **not** an approved Release Candidate. No repository or server was modified and no version bump was made.

## Implemented since last confirmed commit
- Portable `.quorivio` import assigns fresh global asset identifiers and rewrites theme/page/result references; prevents cross-session primary-key collisions on re-import.
- Session duplication copies the underlying asset records and blobs, retaining independently usable shared media references.
- Media bundle validation checks embedded bytes against declared MIME signatures and cryptographic digests and rejects malformed archives.
- Email MFA enablement requires a delivered one-time code confirmation; authenticator MFA remains independent of SMTP. Settings, profile photo lifecycle and transactional admin changes hardened.
- Six regenerated English/Italian PDF guides and additional regression/HTTP integration coverage.
- CI pipeline adds disposable real-PostgreSQL HTTP smoke for import twice, duplication, media retrieval, photo lifecycle, and invalid bundle rejection.

## Verification in this workspace
- `npm run build`: PASS, backend TypeScript and frontend TypeScript/Vite.
- `npm run test -w @quorivio/api`: 126/126 PASS.
- `PYTHONPATH=tools python3 -m unittest discover -s tools/tests`: 224/224 PASS.
- `python3 tools/rc_gate_audit.py`: RC score 40.0/100. This is a weighted *acceptance evidence* score, not implementation coverage.
- Disposable PostgreSQL HTTP smoke is configured in CI but **not executed in this workspace**. Accordingly no claim is made that it passed.

## Outstanding acceptance blockers
1. Complete browser/device usability, pointer/touch, accessibility and presenter/participant cross-browser sessions.
2. Native PowerPoint advanced chart series, SmartArt and OOXML round-trip fidelity; document supported loss precisely on representative user corpora.
3. Real SMTP, OAuth/OIDC providers (including AAI INFN), and multi-replica session/MFA acceptance.
4. Cross-instance portable import on *two independent databases and object stores* and malformed bundle fuzzing under runtime resource quotas.
5. PostgreSQL 18 CI HTTP run, 500 simultaneous participants with p95 latency and correctness evidence, Podman rootless, Docker multi-architecture and Helm NGINX/HAProxy acceptance.
6. Security review, threat model, GDPR processing and deletion exercises, dependency licensing audit and operator/manual validation.

## Release decision
RC **NOT READY**. Keep `0.1.0-dev`; the unaccepted gates listed by `docs/RC_GATE_MATRIX.json` remain authoritative. Passing the local suites must not be confused with completion of external acceptance.
