# RC119 — Content-only auto-fit measurement and Chromium group duplication

The failed GitHub run `41336263788` reported 3 rather than 5 widgets after duplication, and a saved failure screenshot confirmed short-text widgets stretched to the canvas edge. The auto-fit effect measured `.widget-canvas-item.scrollHeight`, which includes intentionally protruding resize handles. Repeated content-independent growth exhausted space required to duplicate a group.

RC119 reads `.widget-fit-content.scrollHeight` relative to `.widget-fit-frame.clientHeight` instead. The fix retains overflow growth for actual text, options and response controls, the existing collision safety, manual sizing, and one-step Undo. Chromium rejects oversized short fixtures *before* duplication and reports native rejection dialogs ahead of count assertions. Full GitHub CI remains required; no coverage or gate-score increase is claimed.
