# Quorivio 0.1.0-dev — Editor, rehearsal and audience visual parity (2026-10-28)

**Baseline:** user commit `e2dc3a97bd15d82a50c23a98b1fb83c2bd1841c9`, earlier successful Full CI `40595463258`. Changes in this cumulative archive have **not** been committed or verified by a new GitHub run.

Implemented shared projection-backed widget sample bodies in the editor; editable title/options on double-click; contextual add-choice; font face, size, text color and alignment in the palette; bounded API-validated character-range `textMarks` (plain text, no arbitrary HTML); unsaved-draft participant rehearsal launched from the editor with native fullscreen; 16:9 saved coordinates across preview and final audience on desktop/mobile; rectangular tooltips for both widget palettes; and opt-in network-free real Chromium CSS geometry regression.

**Local validation:** TypeScript API/web compilation + Vite build PASS; backend 454/454 Node PASS; frontend 38/38 Node PASS; focused Python 26/26 PASS; Chromium visual geometry 1440px and 390px PASS. Full Python suite locally timed out and is **not** certified.

**Still open:** post-commit Full CI (Chromium with real PostgreSQL), Firefox/WebKit and real hardware, independent pixel-level widget parity checks, screen readers, phone usability, fully visual rich-text WYSIWYG inside the currently plain edit input, and distinct multi-question blocks inside one widget. No RC gate promoted on this evidence alone. Global RC remains **53.0%** (1 accepted, 17 partial); release candidate not ready. No assistant commit/push/tag/image publication.
