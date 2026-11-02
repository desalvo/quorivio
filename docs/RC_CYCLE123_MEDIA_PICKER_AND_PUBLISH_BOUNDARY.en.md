# RC123 — Presenter media picker lifecycle and bounded Docker publication

Date: 2 November 2026. Scope: Quorivio `0.1.0-dev`; successor to committed RC122.

## Verified baseline

GitHub Actions run `41350047731` at commit `a97b80b8d09ebd1a6054111bf88326581e2cc80f` completed the **11/11 required automatic RC jobs successfully**; the overall run was ultimately force-cancelled because the authorized `publish-on-commit` Docker build/push job remained in progress. This is successful automated CI evidence **but not a successful end-to-end publication**. Docker Hub tag and digest from this run are not certified. The independent GDPR, AGID, Office fidelity and physical-device approvals remain unaccepted.

## Editor media lifecycle

A single `mediaUploadMime` policy now validates MIME and recognized file extension fallback across five presenter entry points: session asset uploads, widget Logo/Image/PDF/Video uploads, widget fill-image uploads, per-page background library uploads, and converted-slide image imports. A macOS or desktop picker may produce a JPEG `File` whose `type` is empty or `application/octet-stream`; in this case only a recognized extension is used to select the request `Content-Type`. The API independently checks allowed MIME, raw file signature, actual size, authorization, malware scanning and attachment persistence: the extension is *not* a trust boundary. SVG and executable formats remain rejected.

The existing `tools/ci_background_library_postgres.py` validates private library ownership, authorized collaboration and image fetch. A **new** native Chromium + disposable PostgreSQL browser acceptance, `tools/ci_browser_media_picker_postgres.py`, checks actual file chooser events for page background and Logo, the presenter library, independent stored image attachments, autosave and readback after reopening the editor; it is now required by the production quality gate after the server starts. It does not mock network API calls. The native browser acceptance is **not yet confirmed on GitHub for RC123**.

## Bound multiarch publication

The explicit `[publish-docker]` path remains conditional on all three success dependencies (`validate`, `image-build`, `rc-campaign-conclusion`) and successful Docker authentication. Add `timeout-minutes: 45` to `publish-on-commit` so a Docker push cannot leave the same workflow running indefinitely. Full CI-only commits using `[full-ci]` continue to have **no publication**. Timeout causes a failed/timed-out publication, never a success claim; a later controlled retry remains an operator action. There is no automatic Docker publish on any unrelated push.

## Status and acceptance

Local Node API and frontend suites, targeted source contracts and inventory validations must pass on the final extracted ZIP. GitHub strict compilation, authenticated media browser acceptance and multiarch publisher timeout behaviour are future acceptance evidence. No offsite devices, external legal certification, live user data, release tags, or external infrastructure were modified. No assistant commit or push. Certified progress remains **85.25%** (43 accepted / 17 partial of 60; `rc_strict=false`, `publish_image=false`, `publish_latest=false`).
