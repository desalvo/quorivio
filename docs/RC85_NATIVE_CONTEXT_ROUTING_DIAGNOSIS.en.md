# RC85 — native context-button ownership

- Previous commit `2d081ae95594ab79a743822476dee77336f6ea9e`; extended failure `41237085040` job `124643010292`: background menu open and widget menu missing, despite passing Node tests/TypeScript and prior browser checks.
- The prior widget `onPointerDown` selected an unselected widget even for secondary-button presses. This may rerender/reflow the canvas before native `contextmenu` dispatch.
- RC85 limits selection to primary-button pointerdown. A same-gesture, 1.5-second, 8-pixel widget pointerdown receipt permits safe retargeted context recovery; blank background still opens the page menu. No synthetic/forced Playwright actions.
- Native event trace contains only event type, button and widget hit flags, no session content. Use it if the issue recurs. Node/Python/manifest verification and full build status are documented in handoff.
- No unverified acceptance credit, no publishing, `rc_strict=false`.
