# RC164 — Chromium graphic-palette acceptance repair

The GitHub run [41760453415](https://github.com/desalvo/quorivio/actions/runs/41760453415), commit `81ff882`, passed the 588 API + 272 web Node tests and the TypeScript/Vite build, then stopped in `tools/ci_browser_editor.py` because the palette acceptance only read `data-widget-kind`. Since RC161, the Linee and Forme insert triggers retain the normal `.editor-icon-tool` class but expose `data-graphic-palette` to open their independent context menus. The previous test therefore reported them missing, although both were present.

RC164 accepts either attribute, checks required kinds and distinct accessible icons/names, preserves the native tooltip exception for graphic presets, and exercises each graphic menu using an actual right-click in the existing compiled-Chromium acceptance. The test closes the menu without changing the document. A new early negative-mutation suite rejects omission of graphic metadata or removal of right-click coverage.

Runtime and source data remain unchanged. RC163 is frozen as historical. Full authenticated GitHub CI and image publication are not certified by the local source checks. Certified readiness remains 85.25% (43 accepted, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
