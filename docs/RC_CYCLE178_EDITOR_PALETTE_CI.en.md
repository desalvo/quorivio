# Quorivio 0.1.0-dev — RC178: fix Chromium CI and responsive editor widget catalog

**Analyzed run:** https://github.com/desalvo/quorivio/actions/runs/41871700136/job/126720219254 on 4 November 2026. `Production quality gate` failed in `Chromium editor UI acceptance (opt-in)` at the outdated `getComputedStyle(...).overflowX == "auto"` assertion in `tools/ci_editor_mock_layout_chromium.py`. npm install, unit tests and frontend/backend build had already succeeded in this GitHub run.

**Confirmed functional defect:** RC171 changed the widget catalog from horizontal scrolling to wrapped rows with bounded vertical scrolling, but the older RC101 CSS still fixed the desktop grid row to 80px. This clipped the second row. The expanded palette also exposed a few pixels of 16:9 canvas overflow at the bottom of the desktop editor.

**RC178 changes:** bounded automatic palette row across desktop/touch widths; desktop canvas width cap to keep the 16:9 stage visible; Chromium RC101 acceptance now checks vertical scrolling, wrapped icon layout, zero horizontal catalog overflow, bounded height, and that the last widget can actually be reached. A new Python source and negative regression preflight detects a reversion to the fixed-height palette. Existing immutable historical receipts are retained.

**Local evidence before generating the new receipt:** Chromium RC178 editor mock at 1440/390px; RC171 graphic palette at 1440/960/620px; RC105 floating handles, canvas hit target, header overlay, context portal, visual widget geometry, master editor and dual preview; focused RC101/RC178 Python tests. These browser fixture checks do not certify authenticated React/PostgreSQL or physical devices.

**Release safety:** formally certified completion remains 85.25% (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, tag or deployment.

**Final early-CI preflight regression:** 584 Python tests executed with zero failures (one skipped), plus six focused RC101/RC178 tests passing. The RC178 source receipt is verified; a post-commit GitHub CI run has not been observed yet.
