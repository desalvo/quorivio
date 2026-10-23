# Editor composition — grouped cycle (2026-10-23)

The 16:9 slide canvas now offers an optional 5%-grid snap while dragging/resizing (off by default), a duplicate control on each widget that assigns a new widget ID, and front/back stacking controls. The controls appear on hover or focus and are always visible on touch-oriented devices. They use the existing page widget array and save pathway; no schema migration is required.

**Scope and limitations:** stacking is controlled by widget array order. Duplicates inherit widget settings and shift by five percentage points when space allows. The grid is an editor aid rather than a persisted presentation setting and does not alter keyboard movement precision. Rotated box boundaries and overlap are not collision-solved. Browser pointer/touch and assistive-technology acceptance is still open. These tests include static contracts, not interaction E2E.

The overall RC matrix is unchanged pending live browser/DB verification. See `RC_GATE_MATRIX.json` and `DEVELOPMENT_STATUS.md`.
