# RC253 — Deterministic offline Chromium validation for editor Arial

## Verified full CI failure

The maintainer committed RC252 at `6af6db7e6ad812e20548fba8ce9c0451c26df2fe` and full GitHub Actions run [42431610890](https://github.com/desalvo/quorivio/actions/runs/42431610890) failed in **Production quality gate**, step **Chromium editor UI acceptance (opt-in)**, specifically in `tools/ci_rc252_arial_rich_dom_chromium.py`. The compiled React harness passed its Arial checks but its strict console guard detected an incidental `ws://live/?session=...` connection. Because the harness mounts the Vite bundle with `page.set_content` on an offline `about:blank` document, there is no live server, and Chromium emitted `net::ERR_NAME_NOT_RESOLVED`.

## Narrow fix

- Keep the production React code, RichWidgetText DOM fix, real widget insertion and strict browser error checks **unchanged**.
- Before importing the compiled application into the offline fixture, replace `window.WebSocket` **in that test page only** with a deterministic WebSocket implementation. It accepts exclusively the synthetic `ws://live/?session=<fixture-id>` URL and throws for other endpoints.
- Simulate successful asynchronous open and clean close, so no fake network DNS error can mask or fail actual typography assertions. Verify open/close and rejection of unrelated URLs inside Chromium.
- Preserve `pageerror`, console error capture and `assert not errors` without filtering or swallowing application errors; test title/answer glyphs and authored Georgia/Trebuchet overrides at 390×844 and 1440×940.
- Fail closed on unrecognized transport URLs, so accidental navigation to a real endpoint cannot be hidden by the fixture.

## Release and verification

RC252's source-change and historical integrity catalog remain immutable. RC253 changes the offline browser test and CI annotation only, adds this two-language evidence and a fresh SHA-256 cumulative inventory. Frontend TypeScript/Vite build and both Chromium viewports pass locally. GitHub full CI for RC253 remains pending a maintainer commit. No container publishing or repository mutation was performed by the assistant.

**Progress: 85.25%** (43 accepted/17 partial). `rc_strict=false`; `publish_image=false`; `publish_latest=false`.
