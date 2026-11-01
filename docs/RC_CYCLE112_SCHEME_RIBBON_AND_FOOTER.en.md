# Quorivio 0.1.0-dev — RC112 — PowerPoint-style master editor, Footer and rulers (1 November 2026)

**Certified baseline:** RC107 GitHub full CI `41309042012` SUCCESS, commit `99a801ab7623347ba776b8214d054aa872ddb5c6`, Docker Hub published. RC108–RC112 cumulative changes remain **uncertified on GitHub**. Version `0.1.0-dev`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Certified completion stays **85.25%** (43 accepted, 17 partial of 60); no local-only promotion.

**Slide scheme editor:** RC105 selected-only border-box resize handles are now shared with the master canvas; Exit remains above overlapping content and receives pointer hits. The top PowerPoint-like ribbon groups Insert, Align, Distribute, Save, and a horizontal widget rail enables adding non-media widgets. Masters support up to 16 valid widgets; a single Title and Footer each plus multiple generic kinds. Persisted master widgets are inherited by page views, with result/source links remapped to inherited IDs. Media widgets (Image, Video, Logo, PDF) are shown in the master rail and enabled only when the session library contains a compatible authorized asset; their asset selection is editable in master properties.

**Configurable footer:** central session title vs custom label, font/size/bold/italic/underline/color, geometry, independent page-number visibility and placement within the Footer (0–100% in both axes), separator visibility and color. Existing footers retain the 10px lower-right number when custom coordinates are absent. React and native PPTX use the same customizable numbering, with strict API validation; numbers remain dynamic by slide order.

**Page editor rulers:** the same horizontal and vertical rulers displayed in the master are now visible around the normal page editor canvas, responsive on desktop/mobile while retaining 16:9 ratio.

**Evidence and limits:** Node API 567/567 and frontend 159/159 passing. Native Chromium CSS checks on 1440px and 390px verify selected-only handle positions, Exit hit target and page ruler. Generated PPTX checks cover custom number placement and suppression plus separator. Full React/Vite production build and authenticated end-to-end master-editor gestures still require GitHub full CI. No commit/push/tag/image publication.

**Suggested cumulative commit since RC107:** `Export grouped-question PPTX, improve interactive widgets and backgrounds, fix previews, and complete draggable slide schemes and configurable footer [full-ci]`.
