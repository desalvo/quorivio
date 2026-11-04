# Quorivio RC170 — Master-aware phone footer number parity

## Reproduced issue

The page number used desktop 1280px-relative `cqw` units even on the independent 390px phone document. It became unreadably small. Separate old CSS rules forced 5px in rehearsal and 10px in live participation, overriding saved user margins and manually positioned page numbers.

## Application fix

- `SlideCanvasNumber` retains `cqw` sizing on desktop/projection but exposes phone font size and independent insets in logical pixels.
- Shared CSS for phone editing, interactive rehearsal and the authenticated participant view. Explicit `footerNumberX/Y` anchors take precedence over automatic insets.
- The standard editor derives its numbering overlay from the inherited session master, while the editable page widgets remain local and unchanged.
- Desktop 16:9 scaling and presenter projection are unchanged.

## Validation

- RC170 Node checks cover master inheritance, page-level override and display sizing.
- RC170 Python checks include negative regression mutations and early CI wiring.
- Real Chromium fixture checks three surfaces in two viewports, two authored font sizes, two independent inset pairs, and manual anchors, without accessing a network or session credentials.
- The authenticated PostgreSQL/Chromium browser test also asserts real participant page-number sizing and offsets; this requires GitHub CI confirmation.

**Certified progress:** 85.25%, 43 accepted / 17 partial gates. Full TypeScript/Vite build and authenticated RC170 acceptance pending GitHub CI. No commit, push, tag or deployment.
