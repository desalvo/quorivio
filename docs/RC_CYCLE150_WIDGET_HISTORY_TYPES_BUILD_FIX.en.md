# Quorivio RC150 — TypeScript widget history build fix

**RC150 cumulative after committed RC149:** fix two TypeScript TS2339 errors in GitHub Actions run `41700222536` by adding `position` and `resultTopCount` to editor history through a typed `Pick` from the canonical `PageDesign.widgets`. This preserves all saved widget state and operations. Added regression checks, synchronized status headers and generated a new inventory, while keeping RC149 history immutable. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full npm build and integration CI still require the next GitHub run. No assistant commit/push/release.

## Verification

- Run `PYTHONPATH=tools python3 -m unittest tools.tests.test_rc150_widget_history_types -q`.
- Run `npm ci --ignore-scripts` and `npm run build` in CI; no local npm dependency certification.
- Verify `PYTHONPATH=tools python3 tools/verify_rc_release_status.py` and new inventory/ZIP integrity.
