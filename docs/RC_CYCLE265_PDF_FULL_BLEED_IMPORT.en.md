# Quorivio 0.1.0-dev RC265 — Full-canvas PDF/PPTX picture import

## Field changes
RC264 passed full CI: [GitHub Actions 42498365156](https://github.com/desalvo/quorivio/actions/runs/42498365156); manual application/converter image publication passed in runs 42500277043 and 42500299374. The operator confirmed successful PDF conversion on Kubernetes and fixed a RWO PVC Multi-Attach conflict through the `Recreate` Deployment strategy (operator change, not modified by RC265).

**RC265:** image-mode PDF/PPTX import now offers **Fill canvas** (`cover`, default: preserve aspect ratio, crop edges), **Fit entire image** (`contain`: no crop, blank white bands where needed), and **Force stretch** (`fill`: 100%×100%, may distort). A default-on checkbox suppresses inherited schemes, title, footer and page number for new imported pages. The API validates transport headers before conversion, stores a session-scoped private image as the page's `backgroundAssetId`, and persists `importedImageFit` and `suppressMaster` in `page_design`. No superimposed title/widget is created for imported raster pages.

This geometry and scheme policy is used across the editor, presenter, rehearsal and public desktop/phone views. Backgrounds from master schemes cannot leak beneath a full-bleed image. Page thumbnails render the actual imported background. Existing ordinary image widgets also show real thumbnails rather than placeholder text.

Only private session assets may be used. `validPageDesign` accepts `cover`, `contain`, `fill` and a valid asset UUID; no arbitrary image URLs for this mode. Pages imported before RC265 retain their existing page layout; **reimport those PDFs** to apply full-bleed placement. Their image widgets will nevertheless show real thumbnails.

## Validation and limitations
Behavioral tests cover background geometry, scheme suppression, API headers and thumbnails; API/web suites, TS/Vite builds and SHA inventories. Full RC265 GitHub CI and manual on-cluster validation are still pending. No SQL migration, converter image changes or Kubernetes wizard changes. Editable import is unchanged.

**Readiness:** 85.25% (43 accepted gates, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Do not commit, push or tag without authorization.
