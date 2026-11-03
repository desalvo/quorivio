# Quorivio 0.1.0-dev — RC143 — Formatting window, top results and smartphone visual fidelity

## Scope

- **Floating “Widget Format”**: close control stays in the visible header even at narrow viewports; toolbar groups wrap into multiple rows; vertical scrolling exposes every action. ResizeObserver repositions the floating panel if its height increases. Closing the window does not clear widget selection.
- **Results / animated word cloud**: the displayed top result count is configurable on the linked Results widget, default **5**, range 1–20. Ranking is stable by descending count and does not modify the source data. Long labels wrap at word boundaries; the final word stays attached to the numerical count. The result component shared by editor, presenter and rehearsals owns these rules. The normal auto-fit scales the whole set to available space; disabling auto-fit intentionally preserves manual crop/scroll behavior.
- **Smartphone rehearsal**: a fixed **1280 × 720 logical canvas** is scaled uniformly to the available device width via ResizeObserver. Widget coordinates, dimensions, rotation and text wrapping are no longer replaced with a stacked mobile layout. The page background photograph is omitted in the phone simulation. Desktop, presenter and normal participant preview modes remain unchanged.

## Verification

- `node --experimental-strip-types --test apps/web/test/rc143-preview-results.test.ts`
- `python3 -m unittest tools.tests.test_rc143_phone_result_ribbon -q`
- `python3 tools/ci_rc143_format_phone_chromium.py` (mock page geometry at 1225 and 390 px)
- `python3 tools/verify_rc_cycle143_inventory.py` plus historical catalog checks
- Full standalone local campaign: **816/816 Node tests passed**, **1,734 Python tests run, 0 failed, 1 skipped**, Chromium CSS acceptance 1225/390 px passed. Full frontend npm/Vite compile and real deployment browser acceptance: **pending GitHub CI**. This is not proof of parity on all devices. The smartphone editing workflow does **not** yet persist independent phone-only widget geometry; adjustments to the shared authored layout remain available from the desktop editor.

**Release flags:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Certified completion stays **85.25%** (43 accepted / 17 partial). Do not promote without external evidence.
