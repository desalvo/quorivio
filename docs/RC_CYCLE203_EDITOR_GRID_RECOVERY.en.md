# RC203 — Editor grid and wrapped widget catalog CI fix

Source: [GitHub Actions run 42107111552, job 127524721412](https://github.com/desalvo/quorivio/actions/runs/42107111552/job/127524721412).

- Python dependency staging and frontend/API Node suites passed. The real Chromium `ci_editor_mock_layout_chromium.py` failed at a wrapped widget palette 140 px tall in a 122.765625 px rail; its final geometry assertion was reached after all earlier editor browser checks passed.
- Root cause: RC200 compact header replaced the three explicit rows (header, palette, stage) with only header and stage; its desktop `grid-template-rows:minmax(88px,auto) minmax(0,1fr)` superseded RC178's bounded palette row.
- Restore `minmax(72px,auto)` as the middle row for desktop, tablet and phone; keep title/primary owner beneath action buttons. Expand desktop 16:9 canvas vertical clearance from 240 to 280 CSS pixels to avoid the small overflow visible after restoring the palette row.
- Extend the actual Chromium layout test to 1440×900, 1200×900, 960×760, 390×844. Add RC203 pre-dependency fast regression, including checks that restoring the old two-row CSS or 240px clearance fails.
- Preserve RC201 live QR refresh, RC200 portable import/export and RC202 Python staging unchanged. Do not enable strict RC or automatic publication.
- Completion stays **85.25%**, with 43 accepted and 17 partial gate results until validated evidence changes. Full CI on this new cumulative remains pending.
