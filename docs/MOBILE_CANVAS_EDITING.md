# Mobile canvas editing — geometry and accessibility

The editor retains the same 16:9 coordinate system used for storage and PPTX
round-trips even below a 480px viewport. Previously the mobile rule changed
widgets to relative full-width blocks and removed their rotation while pointer
gestures still wrote absolute canvas coordinates.

The editor now keeps a horizontally scrollable artboard at least 600px wide.
Widget positions, dimensions and rotations are not rewritten by CSS.
The accessible controls list remains available as a touch/keyboard alternative
for moving, duplicating and layering elements. This is a source-level fix,
**not** a physical-device acceptance test. Participant answer views may still
reflow vertically for readability.

## Outstanding verification

- On iOS/Android, test canvas panning, dragging, resizing and rotation and
  compare persisted geometry before/after editing.
- Test virtual keyboard, browser zoom and screen readers.
- Run a clean TypeScript/Vite build; offline dependency resolution currently
  lacks `@types/bcryptjs` and no verified lockfile was generated here.
