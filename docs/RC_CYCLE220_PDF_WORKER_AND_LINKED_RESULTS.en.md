# RC220 — PDF/PPTX import and independently formatted linked results

**Baseline:** RC219 green full GitHub acceptance, run 42197607753 (14 successful jobs; three publication/final-image jobs skipped). App version remains 0.1.0-dev, certified 85.25% unchanged.

## Administration

Platform admin → **Server configuration → Isolated PDF/PowerPoint converter**. The page reports deployment enablement, private worker configuration and a bounded health check. Use Enable/Disable/Check worker; administrator choices persist as `platform_settings.converter_enabled`. API endpoints remain fail-closed and are restricted to platform administrators. Server-side `QUORIVIO_ENABLE_CONVERTER=true`, trusted URL and 32+ character secret are prerequisites; the web UI never provisions or exposes worker secrets. Compose includes the converter; set a strong random token in `.env` and start the entire stack. Kubernetes requires the converter sidecar, the shared scratch mount, a Secret and service health. The admin switch cannot deploy a missing worker. PDF and PPTX presentation imports produce full-canvas image slides.

## Linked results

Two independent options control source title and source answers, preserving legacy combined values. Source title begins on a new line, larger and bold. Answers are bullet-prefixed, bold, wrapping. A separate question bullet and distinct colour defaults to `#2563eb`; edit it via **Widget format → Questions → Question text colour**. Cross-page links and presenter-only statistic privacy remain unchanged.

Safety: `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full RC220 CI pending; no assistant commit/push/tag.
