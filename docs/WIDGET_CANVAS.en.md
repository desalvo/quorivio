# Visual widget canvas — 0.1.0-dev

## Status
Implemented in source with layout-validation tests and TypeScript/TSX parse checks; live browser/PostgreSQL tests remain outstanding.

## Usage
Drag widgets on the visual page canvas, double-click their labels to edit them, adjust width with +/− and remove each widget separately. Select **Save layout** to persist. The legacy list retains per-widget settings, ordering and keyboard-operable buttons.

## Persistence
`position: {x,y,width}` contains percent-based coordinates with x/y >= 0, width 12–100, x+width <= 100 and y<=96. The backend rejects non-finite and unexpected values. The audience view uses saved positions.

## Limitations
Collision avoidance, custom responsive layouts, full spatial keyboard controls, browser/PostgreSQL E2E tests, conversion sandboxing, and multi-replica shared storage remain open.
