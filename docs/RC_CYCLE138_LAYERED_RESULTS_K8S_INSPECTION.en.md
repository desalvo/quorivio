# RC138 — Intentional widget layers, result widget fidelity and Kubernetes inspection

Baseline: **RC137**, GitHub CI `41475936282` green, commit `4b33e67ec2ee22973b557ab3ec6759bad356dedc`.

- All widgets can overlap intentionally via mouse, touch, keyboard, copy/paste, and eight-edge resizing. The canvas bounds still apply and Undo/Redo remains functional.
- Results live in their authored slide widget on the presenter screen, showing aggregates only; participant projections never render results or mirror participants' inputs into the presenter answer fields.
- Results now offer an auto-resize/scale toggle. Manual resizing disables scaling, maintaining chosen text/chart size and allowing scrolling within the widget, without a misleading downscale indicator.
- Presenter/participant rehearsal uses intrinsic submit-button width, matching the authored editor layout.
- Short free-text answer frequency data are aggregated into anonymous 1–2 word labels (max 48 characters); long responses contribute only to counts.
- The wizard accepts `--inspect-cluster` with `--output` and `--set namespace=... --set name=...`, writing a nonsecret read-only cluster inventory to `quorivio-cluster-discovery.json`. It does not read Secret values, mutate Kubernetes, or regenerate credentials in inspection mode. It is a discovery foundation **not** an auto-apply or complete reconciliation feature; never apply full generated installation manifests to an existing cluster without manual approval and Secret/PVC preservation.

CLI example: `python3 tools/k8s_wizard.py --inspect-cluster --output ./quorivio-inspection --set namespace=quorivio --set name=quorivio`.

**Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. RC138 remains uncommitted with new GitHub CI and independent acceptance pending. No assistant commit/push/release.
