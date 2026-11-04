# Quorivio RC180 — editor insertion rail and contextual toolbar pointer safety

## Failure observed on GitHub

Run `41913987787`, job `126868661600` (`Production quality gate`) completed with failure at the `Chromium editor UI acceptance` step. The RC179 browser test for selected-widget actions passed on desktop/tablet/phone. Immediately afterwards, `tools/ci_browser_editor.py` timed out attempting a native click on `button.editor-icon-tool[data-graphic-palette="line"]` because a `.canvas-editor-tools` descendant intercepted pointer events. The RC179 approach had fixed the reverse obstruction by elevating the entire `.editor-stage` stacking context over the responsive insertion rail.

## Functional correction

The canvas selection and alignment panels are docked in normal document flow at the top of the artboard content and below the adaptive widget insertion rail. Context panels remain independently scrollable and visible while selected, and the canvas remains scrollable inside the editor stage. There is no pointer-events bypass, forced Playwright click or synthetic DOM event. The stage's contextual z-index is reset to its ordinary level while tools are open. Header and contextual background-menu rules are preserved.

## Regression and acceptance

The new `tools/ci_rc180_editor_palette_context_coexist_chromium.py` uses the real app CSS and realistic wrapped icon wrappers. It alternates actual native Playwright clicks on **Duplica selezione → Linee → Sinistra → Linee** without dismissing selection tools, at 1440×940, 960×800 and 390×844. It asserts `document.elementFromPoint` resolves each active control before clicking. Against the RC179 source, it fails on the desktop Linee control (intercepted by context); against RC180 it passes on all widths. This guard is invoked before `tools/ci_browser_editor.py` in GitHub Actions, with an early unittest contract. Existing RC179/RC171/editor-header browser tests are rerun.

Local browser fixture tests do not replace the complete compiled React, PostgreSQL and physical-device acceptance. No release gates have been promoted based on this change; the certified score stays 85.25% (43 accepted, 17 partial). Release flags remain `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
