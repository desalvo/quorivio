# RC239 — Contextual widget formatting in the real editor Chromium acceptance

## Observed GitHub failure

Quorivio 0.1.0-dev RC238 committed as `e1f7d2f234a712a112f98b23e3774905825a28d8` failed full workflow run [42274460486](https://github.com/desalvo/quorivio/actions/runs/42274460486) during **Chromium editor PostgreSQL persistence and conflict acceptance**. The previous, independent real editor/PostgreSQL autosave, conflict-resolution and JSON-export fixture **passed**. The next real browser fixture `tools/ci_rc193_editor_focus_chromium.py` timed out attempting to select a missing `Ambito della formattazione` combobox immediately after opening the separate **Proprietà widget** inspector. Since RC223, the widget-format window is only shown by explicitly choosing **Formato widget** from the widget's context menu. The browser test incorrectly assumed that opening the inspector also opened the formatter.

## Implemented

- Preserve the RC193 checks for focus remaining in the active inline option, continuous typing and inspector text inputs.
- Close **Proprietà widget**, reopen the question widget's own context menu, select **Formato widget** and verify the `Formattazione rapida widget selezionato` toolbar exists.
- Select the whole-widget formatting scope within that toolbar; scope font-size, increment and font-family controls to that real toolbar and preserve Georgia/Arial answer inheritance assertions.
- Add RC239 mandatory pre-npm regression with negative mutations for wrong menu action, wrong ordering, missing close, unscoped controls, absent format action and removed CI gate. Keep the real authenticated compiled Chromium/PostgreSQL fixture mandatory after build.
- Promote the sole current source checksum catalog to RC239; retain and verify RC238 and earlier inventories with `--historical`, without editing their bytes.

## Verification and release constraints

The source is derived from the RC238 cumulative ZIP, with the main React, workflow and Chromium RC193 script blob SHA-1 hashes checked against the GitHub commit. The correction changes only acceptance scripts, CI, tests, and handoff metadata; no production React, CSS, API or DB behavior. Real compiled Chromium/PostgreSQL full CI must be rerun on GitHub after a user-controlled commit, and no result is claimed in advance. Last certified full-green workflow remains RC219 (`42197607753`); overall certified **85.25%** (43 accepted, 17 partial), with `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, tag or publication.
