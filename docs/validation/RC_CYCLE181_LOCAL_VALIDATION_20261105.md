# RC181 local validation — 2026-11-05

Scope: GitHub Actions run 41931287829, preflight `tools/ci_accessible_disclosure_chromium.py` at line 54. The stale requirement for a forced overlap was replaced with **no overlap** using the production CSS. The original hit target, native click/tap, checkbox, contextual toolbar dismissal, and layer action are still exercised.

Executed locally on the source before packaging:

- `QUORIVIO_CHROMIUM_PATH=/usr/bin/chromium python tools/ci_accessible_disclosure_chromium.py`: PASS (390x844 touch, 1440x1000 desktop; includes real button/checkbox interactions).
- `python -m unittest tools.tests.test_ci_mobile_disclosure_overlap tools.tests.test_rc181_disclosure_dock tools.tests.test_rc180_editor_rail_context_docking -q`: PASS (12 tests).
- `tools/ci_rc180_editor_palette_context_coexist_chromium.py`: PASS (1440x940, 960x800, 390x844; normal pointer hit testing).
- `tools/ci_editor_save_locator_chromium.py`: PASS.
- `tools/ci_editor_save_flow_chromium.py`: PASS.
- `tools/ci_editor_mock_layout_chromium.py`: PASS.
- `tools/ci_editor_floating_layout_chromium.py`: PASS at 1440x900 and 390x844.

No claim is made here for the complete React/PostgreSQL authenticated test or physical-device/accessibility acceptance. The release gate ledger is unchanged at 85.25%. No commit/push/tag/deploy.
