# RC286 — `.quo` session format, faithful thumbnails, scroll-safe menus and illustrated manuals

## Application changes

- Portable session archives now use **`.quo`** across server endpoints (`/api/sessions/:id/export.quo`, `/api/sessions/import.quo`), filenames, inputs, tests, and documentation. The vendor MIME namespace `application/vnd.quorivio.session+zip` identifies the manufacturer, **not** the superseded archive extension. Hidden `.quorivio-*` working directories are unrelated to session archives.
- **Session attachments** in the dashboard are a keyboard/touch-accessible native `details/summary` section, **collapsed by default**, with an item count.
- Page thumbnails now represent actual question titles/options, text, timers, images/logos, shapes, lines, reaction/rating widgets and schematic charts. The active page preview includes unsaved draft changes. No synthetic vote counts are presented as live statistics.
- Widget context menus are fixed to the visual viewport, have their own bounded scroll area, and do not close on internal wheel or touch scroll. True/false indicators are short within menus, with full settings retained in properties.

## Documentation and evidence

- Six regenerated Italian/English PDF guides, 247 total pages in RC286. Expanded guided workflows for pages, schemes, all rehearsal modes, live sessions, mobile participation, portable `.quo`, backup/DR/scaling.
- Six original conceptual diagrams with arrows/shapes and two synthetic photographic-style inserts are clearly labelled. Authentic archived browser screenshots are attributed by **release**; commit strings are not printed in manuals.
- CI Chromium capture is expanded to record real PostgreSQL-backed UI of thumbnails, context menus, master editor, four rehearsal views, live presenter, collapsed/expanded attachments and 16:9 mobile view. The secure manifest still stores full source commit and image checksums privately for proof of freshness.
- Full end-to-end acceptance of the expanded capture requires the next CI; no mock UI is misrepresented as real.

## Validation and constraints

- Local web tests: 473 passed. API: 652 passed. New focused RC286 contracts passed. Full npm compilation, extended Chromium screenshots and RC286 full CI remain pending.
- Product completion baseline remains 85.25% pending newly accepted functional gates. No assistant commit, push or tag.
