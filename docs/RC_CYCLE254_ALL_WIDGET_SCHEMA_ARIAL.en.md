# RC254 — Complete widget and slide-master font audit

## Baseline

RC253 full CI [42432817088](https://github.com/desalvo/quorivio/actions/runs/42432817088) (`93d029100ef09af4e3fe88119e83db38abc62960`) passed: 14 successful jobs, 3 conditional skips.

## Findings and changes

RC252's shared `RichWidgetText` already skips absent properties in imperative CSSStyleDeclaration. Other rendering paths still trusted font-family strings blindly: baseline widget text, answer fields/options, submit buttons, result text overrides and footer page numbering. Invalid legacy/imported strings could therefore become CSS font names in those paths.

RC254 centralizes the supported-family allowlist (Arial, Georgia, Verdana, Tahoma, Trebuchet MS, monospace) in `widget-typography-defaults.ts` and applies it at every rendering boundary. Unknown, empty, missing, literal `undefined` and `null` values never create CSS font names. All supported explicit author choices survive unchanged. This is a rendering safety layer; the API continues to reject invalid writes.

Both page authoring and slide-master authoring use `WidgetCanvas` and the same rich-text engine; no duplicated master-only implementation was necessary.

## Checks

- Node regression checks 20 widget kinds, all text fields, malformed values, and independent question/answer/footer overrides.
- Compiled React Chromium checks 14 text-bearing widget kinds in both regular and slide-master editors, 390×844 and 1440×940. Test-only WebSocket fixture is constrained; console/page errors remain hard failures.
- Media-only kinds are covered by unit defaults, not by an asset-upload integration fixture.
- A successful local suite does not imply a GitHub full CI pass or update running Docker deployments.

**Progress:** 85.25% (43 accepted / 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag.
