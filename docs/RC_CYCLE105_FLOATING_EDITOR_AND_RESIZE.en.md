# RC105 — floating editor windows and canvas resize controls

Baseline RC104 cumulative not yet committed. RC102 full CI 41265300884 confirmed; application version stays 0.1.0-dev.

## Fixes

- Eight resize handles and the rotation handle are absolutely anchored to the selected widget **border box**. The legacy art-theme direct-child CSS was unintentionally switching these controls to `position:relative`.
- Unselected widgets hide resize and remove controls. Pointer and touch interactions retain access to selected handles.
- Office-like typography ribbon is rendered in a fixed React portal, outside the editor grid and without slide reflow. The ribbon scrolls internally on narrow screens.
- Widget properties and page settings are fixed draggable windows; dragging starts from the header, not from a button or field; positions are viewport-bounded and respond to browser resize.
- Ribbon buttons continue preserving the text selection.

## Evidence and remaining checks

- `tools/ci_editor_floating_layout_chromium.py` tests actual editor CSS in desktop Chromium 1440×900 and mobile 390×844, confirming eight handle centers, selection-only visibility, themed widgets and zero canvas geometry shift on ribbon opening.
- `tools/tests/test_rc105_editor_floating.py` guards source contracts for the portal, drag rules and active-widget controls.
- Full production React build, end-to-end moving windows in the loaded app and GitHub full CI still require execution by the maintainer.
- Physical-device audits remain open; certified readiness remains 85.25%, 43 accepted / 17 partial.
