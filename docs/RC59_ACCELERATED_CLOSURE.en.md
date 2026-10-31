# Quorivio 0.1.0-dev — RC59 macroarea closure campaign

**Committed baseline:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`. **Verified CI:** standard `41152434205`, extended `41152939003`. **Certified RC:** **81.75%**, 55 gates (38 accepted, 17 partial). **Strict RC is NOT ready.** Cycle 58 and 59 changes await a new maintainer commit and CI.

## Execute full macroareas, not micro-cycles

Deliver one cumulative tested package only after a full functional macroarea is complete, then run normal CI and a single automated RC campaign. Collect any CI failures and address them as a batch. Preserve all previous source checksum inventories and update handoffs. The maintainer alone commits, pushes, tags and publishes.

## One-click, no skipped-job false green

After the maintainer commits, use **Actions → Quorivio CI and Docker Hub → Run workflow** with `rc_acceptance_suite=true`, `publish_image=false`, `rc_strict=false`, `publish_latest=false`. The full campaign enables 13 opt-in families: Chromium, Firefox/WebKit, 500-client capacity, global p95 SLO, 70-second idle live, Kubernetes manifest/boot, NGINX/HAProxy ingress and TLS on both, OCI amd64/arm64, rootless Podman and real ClamAV. All test infrastructure is disposable and isolated; **no real user Kubernetes cluster and no publishing**. Run standard CI first and avoid dispatching another workflow on the same git ref while the first is active (workflow concurrency cancels in-progress runs).

The new `rc-campaign-conclusion` job requires **all 11 dependent jobs** to have `success`; skipped, failed or cancelled jobs fail the overall campaign. The summary reports results in GitHub Actions. `python3 tools/rc_campaign_preflight.py --check-workflow` validates the workflow's input coverage, non-publishing guards and conclusion prerequisites. **A green automated campaign does not imply independent RC sign-off**; the scored ledger is updated only with individually reviewed proof.

## Parallel ownership tracks for all 17 partial gates

1. **Infrastructure and resilience:** B1, B4, C4, D2, D3 — verify KIND TLS; then independently provision CSI/NFS/CephFS RWX on distinct machines, two-way actual asset writes, storage/network failure, real restore RTO/RPO and degraded SLO. Single-host KIND and runner bind mounts do not certify these conditions.
2. **Federated identity, SMTP and administration:** C1, C2, C3 — real Google/GitHub/Facebook consent/callback, replay and cross-replica flows, independent SMTP deliverability and MFA/recovery. PostgreSQL already single-consumes OAuth state; cycle 59 adds bounded streamed JSON responses from providers. Mocks are not external provider approval.
3. **UX, collaboration and accessibility:** A1, A2, A3, A4, B2, B3 — real mobile/desktop devices, screen readers and keyboard operators, visual PPTX parity, editor/preview/presenter sessions, moderation and statistics with independent review.
4. **Independent governance and documentation:** D4, D5, D6 — third-party security and accessibility review, GDPR/AGID review, IT/EN manual acceptance and external Office corpus.

## Acceptance rule

Each gate needs bounded scope, working behavior, regression, actual relevant CI or operator evidence, and a reviewed JSON ledger update. Preserve weighted total 100 and never double-credit earlier acceptance. All 17 residual gates remain partial until their required independent evidence exists; do not label RC ready early.
