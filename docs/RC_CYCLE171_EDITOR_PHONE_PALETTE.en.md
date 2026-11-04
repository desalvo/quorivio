# RC171 — Visible smartphone editor, automatic packing and graphic palette

Cumulative RC170 base. The page editor's **Desktop 16:9 / Smartphone 390 px** switch now lives in the top toolbar and remains available on narrow windows. The automatic smartphone planner uses smaller gaps and content-aware heights while protecting questions, the 0–9 rating controls and interactive text. The stage grows for longer content. Users can explicitly **Recompact automatically** to clear any stale saved placements; otherwise existing mobile position and style overrides are respected.

**Line/Shape:** graphic triggers now share the same width-limited wrapper as ordinary widget icons and the palette wraps to multiple lines rather than stretching a single giant button or requiring horizontal scrolling. Presets can be opened by right click, long press, Shift+F10 or the visible ellipsis button, with shape/line type, arrows, stroke, color and fill choices. Regular format editing remains available after insertion.

**Evidence:** Node and Python regression checks, actual Chromium CSS viewports 1440/960/620, cumulative source/inventory integrity. Full Vite compilation and authenticated React/real-device acceptance remain for GitHub CI. **85.25% certified (43/17), `rc_strict=false`, `publish_image=false`, `publish_latest=false`**. No commits, pushes or deployments.

**Canvas context / Menu contestuale dei widget inseriti:** nel widget Linee/Forme già presente è possibile selezionare direttamente preset, spessore, colore e (per le forme) riempimento tramite menu contestuale, mantenendo anche le proprietà complete nel pannello di formato. / Already inserted graphic widgets expose preset, stroke, color and shape fill directly in their right-click menu; full formatting remains available.
