# Full Chromium mobile visual-viewport hotfix — 2026-10-25

## Confirmed failure

GitHub Actions run `40218596128`, quality job `121245025409`, fails inside `tools/ci_browser_editor.py` at the **mobile** `acknowledge_functional_cookie_notice` step. The desktop editor scenario already reached canvas operations; its `failure.png` is the desktop context captured by the outer handler, whereas `mobile-failure.png` identifies the actual failure context.

Playwright: `Locator.click: Timeout 10000ms exceeded`; the native `<dialog>` itself intercepts pointer events aimed at the child `Ho capito` button. The previous native `showModal()` top-layer fix was necessary to avoid dashboard stacking, but did not fix the mobile coordinate mismatch. `ws proxy error: ECONNREFUSED` is unrelated to this specific pointer failure.

## Reproduction and root cause

The CI artifact `chromium-editor-failure` was inspected. A Chromium local replay of the saved mobile DOM reproduces the same click timeout. With a 390×844 touch-capable browser viewport, the overflowing page can produce a **layout viewport 574×1243**, while the **visual viewport is 390×844**. Bottom-fixed modal placement puts the button near **y=1173**, below the touchable visual viewport; Playwright reports the dialog as intercepting the click. Merely increasing timeouts, raising z-index, or forcing the click does not address the defect.

## Correction

- `apps/web/src/style.css`: for screens <=740 CSS px, anchor `.functional-cookie-dialog` to `top:18px;bottom:auto`; retain desktop bottom anchoring and the native top-layer modal.
- `tools/ci_browser_editor.py` and `tools/ci_browser_editor_postgres.py`: before a real user click, assert that the button's center is inside `window.visualViewport`, including viewport offsets. Preserve real clicks, `:modal`, and acknowledgement persistence.
- `tools/ci_cookie_viewport.py`: **network-free Chromium regression**, desktop and 390×844 touch viewport with a deliberately wider layout. The pre-fix CSS reproduces Playwright's intercepted click; fixed CSS passes both modes.
- `tools/tests/test_chromium_cookie_visual_viewport.py`: three new regression contracts; existing cookie-notice contracts updated for the named button locator.

## Validation

Local: **314/314 Node tests PASS**, **633/633 Python tests PASS**, API TypeScript build PASS, web TypeScript + Vite production build PASS, independent Chromium desktop/mobile click PASS. The previously failing mobile fixture also passes when replayed from the saved DOM with the corrected CSS. The complete GitHub full browser suite is **pending**; do not claim the gate green until `browser_test=true` succeeds. RC audit remains **45.5%**; A1 remains partial. No commit, push, tag, release or deployment performed by the assistant.
