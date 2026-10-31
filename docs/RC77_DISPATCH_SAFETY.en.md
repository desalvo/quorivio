# RC77 — Deterministic non-publishing one-click acceptance

The maintainer confirmed standard CI run `41209516202` green on `e4f24a9fb8a36ef0b96ddb20b755a5a2f9335343`. Extended runs `41210085593` and `41210395340` both stopped in the admission step: the runner environment exposed `RC_CAMPAIGN_PUBLISH=true` even when only `rc_acceptance_suite` was reportedly selected. The public run API did not expose the original input values; therefore the origin of this value is unknown, and the application did not cause this failure. The 1/11 summary was a correct cascading failure.

## Fixed safety invariant

When `rc_acceptance_suite` is true:
1. Its validation step passes the effective values `RC_CAMPAIGN_PUBLISH=false` and `RC_CAMPAIGN_STRICT=false`, regardless of other workflow_dispatch inputs.
2. The `publish` job condition includes `!inputs.rc_acceptance_suite`, so even an accidental or persisted `publish_image=true` cannot publish within a campaign.
3. The strict release-candidate gate includes `!inputs.rc_acceptance_suite`, ensuring the campaign does not act as operator sign-off.
4. `tools/resolve_image_tags.sh` independently denies `QUORIVIO_RC_ACCEPTANCE_SUITE=true`, even if directly invoked with publication consent.
5. Early CI tests validate the gates and script before any npm installation, and the existing campaign preflight checks all guarantees.

Manual publication remains an opt-in separate workflow_dispatch outside the RC campaign, with original repository/tag, image and permission checks preserved. The strict RC is still blocked by outstanding external evidence. Run a **new** workflow_dispatch from the new maintainer commit with `rc_acceptance_suite=true`, not Re-run jobs on an old run. Do not claim green extended CI until verified.
