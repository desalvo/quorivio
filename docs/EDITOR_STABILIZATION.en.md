# Editor gesture stabilization — 2026-10-23

This cycle hardens existing slide manipulation without changing the saved page schema or project version.

- Rotation now applies the pointer angle delta to the widget's previously stored rotation. Dragging the rotation handle no longer resets orientation on first movement.
- A cancelled pointer gesture restores the widget's initial geometry, including its previous rotation. Pointer-capture loss clears gesture state.
- Touch interactions on canvas items disable browser gesture interception; editable title inputs still permit text selection.

Validation: production TypeScript/backend and Vite/frontend builds passed; Node suite passed; Python tools suite 102/102 passed including three new static regression checks. Real touch, pointer cancellation, browser persistence and PostgreSQL integration remain unverified. These checks are not browser E2E tests. The A-editor acceptance gate and overall RC remain open.
