# Quorivio 0.1.0-dev — RC149 — Device-aware background contract CI regression

RC149 after committed RC148: GitHub Actions run `41690976927` stopped in the historical RC110 background upload contract. That contract matched only the older unconditional desktop `backgroundAssetId` binding and two-argument upload call, while current editor intentionally routes phone background selection and upload independently. RC110 checks now require the desktop fallback and isolated phone branch, with negative regression mutations. Runtime editor code is unchanged. RC148 historical manifest remains immutable. Local CI validation does not substitute for npm, browser or external acceptance. **Certified 85.25%** (43 accepted / 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/release.

## Validation

- RC110 existing API, upload feedback, cloud and answer field contracts remain checked.
- Independent desktop/phone background props and upload routing are asserted.
- Negative-mutation checks reject reverting to unconditional desktop background.
- Historical receipts remain checksummed; CI source/ZIP inventory is closure-checked.
