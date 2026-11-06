# RC238 — Real participant Chromium phone-default reconciliation

## GitHub failure

[GitHub full CI run 42269302109](https://github.com/desalvo/quorivio/actions/runs/42269302109), committed RC237 `4c4b7ee0451e0a20abb791da2a0ea585eddc8f63`, completed with a failing `Production quality gate`, step **Chromium participant UI and PostgreSQL lifecycle (opt-in)**. The runner reached `tools/ci_browser_participant.py:132`: it expected the **Diapositiva 16:9** button to have `aria-pressed=true` on the mobile context. The actual value was `false` because RC227 automatically selects **Layout smartphone** for a narrow touch browser. ClamAV succeeded; dependent release jobs were skipped or failed closed.

## RC238 scope

- Keep product mode selection and layout logic unchanged: no runtime UI, API, database or CSS change.
- During participant join, verify faithful 16:9 default on the desktop viewport, verify smartphone default and rendered `.stage-phone` on the touch/narrow viewport, then explicitly switch the mobile browser to `.stage-fidelity` for authored 16:9 geometry checks.
- After mobile reload, verify that the automatic phone default is restored; explicitly switch back to 16:9 before comparing desktop/mobile normalized geometry. The later explicit phone and accessible-reading tests remain in place.
- Reconcile the historical RC176 source-order check to inspect `stage-phone` after the **explicit** switch, because `stage-phone` now correctly appears earlier as an automatic default.
- Add `tools/tests/test_rc238_auto_phone_participant_chromium.py` with negative mutations for missing defaults, missing explicit mode switches, changed mobile join, missing product mode guard and dropped end-to-end CI acceptance. Execute early before npm, retain real PostgreSQL + Chromium step as a mandatory full-CI gate.

## Validation and release state

Run from the repo root: `python3 -m unittest tools.tests.test_rc238_auto_phone_participant_chromium tools.tests.test_rc176_accessible_stage_modes -q`, then the relevant historical source tests and all Node tests. Validate all historical workflow receipts, current RC238 manifest, release headers, SHA-256 and the final ZIP.

**Important:** unit/source checks cannot replace the real browser lifecycle with PostgreSQL on GitHub. Full CI remains to be certified. Certified completion remains **85.25%** (43 accepted and 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag.
