# Quorivio 0.1.0-dev — RC181: accessible disclosure dock Chromium CI reconciliation

## GitHub evidence

Run [41931287829](https://github.com/desalvo/quorivio/actions/runs/41931287829), commit `8eccbfb48a214e584c3e685c2877bede0bbbcf94`, reached the Chromium editor UI acceptance after dependency installation, unit tests and frontend/backend build. The RC180 insertion rail checks passed. `tools/ci_accessible_disclosure_chromium.py` then failed at line 54 because it still required an *overlap* between the selected-widget toolbar and accessible disclosure in a 390px mobile fixture (`assert overlap`). That overlap had been intentionally removed by the RC180 non-overlapping dock. The run summary failed as a consequence; ClamAV acceptance passed.

## Correction

Updated the real Chromium CSS/DOM acceptance to assert **no overlap**, using the same application's production stylesheet. Preserved native (non-forced) mouse/touch clicks on the accessible `<summary>`, its checkbox, the contextual toolbar and the layer action, including automatic dismissal when the disclosure opens. Checked 390px touch and 1440px desktop. The earlier contract test `tools/tests/test_ci_mobile_disclosure_overlap.py` now asserts the new behavior instead of requiring the removed defect. A separate early `test_rc181_disclosure_dock.py` gate catches a reintroduction of the stale assertion, missing hit-test or disabled real-pointer controls before npm is installed.

No runtime application code or business logic changed in this cycle. No regression of the original accessible hit-target protections is permitted. Historical checksum catalogs remain immutable; the new RC181 catalog is generated from the previous RC180 catalog, and the CI runs the RC180 verifier in historical mode.

## Acceptance state

Local Chromium run (390px touch and 1440px desktop) and targeted Python regression are green. The full GitHub CI, authenticated React/PostgreSQL browser acceptance and physical-device accessibility review are not yet claimed. **Certified score: 85.25% (43 accepted, 17 partial).** Release flags remain `rc_strict=false`, `publish_image=false`, `publish_latest=false`. The assistant has not committed, pushed, tagged or deployed.
