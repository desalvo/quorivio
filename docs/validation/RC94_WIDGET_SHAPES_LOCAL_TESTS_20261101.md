# RC94 — borderless and vector shapes local evidence

- `node --experimental-strip-types --test apps/api/test/*.test.ts` — **565/565 PASS**.
- `node --experimental-strip-types --test apps/web/test/*.test.ts` — **143/143 PASS**.
- `python -m unittest tools.tests.test_rc94_widget_shapes_and_menu tools.tests.test_rc93_participant_qr_contract tools.tests.test_pptx_shape_paint_ui -q` — **15/15 PASS** (4 new native shape/border regression cases).
- `python -m py_compile tools/pptx_portable.py` — PASS.
- Global TypeScript source parser for main.tsx, widget-shape-outline.tsx, widget-appearance.ts, editor-context-menu.ts and api domain.ts — zero syntax errors.
- Consistent CSS clip geometry and SVG vectors tested at source level; real Chromium/mobile visual rendering remains pending.
- PowerPoint post-it exports use native editable auto-shapes; actual pixel-perfect cloud and speech conversion and other widget kinds remain pending advanced acceptance.
- No full TypeScript/Vite dependency build, authenticated PostgreSQL, GitHub CI or publication is claimed.
- RC acceptance holds at 84.75%, strict/publish flags remain disabled.
