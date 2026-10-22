# Integrated slide pages — Quorivio 0.1.0-dev

Presenters can now promote uploaded PNG, JPEG and WebP assets into individual session pages. The web workspace supports batch image upload (up to 100 files). Name files `page-0001.png`, `page-0002.png`, etc., to ensure alphabetical order.

## PDF/PPTX workflow

Convert documents offline using `python3 tools/import_presentation.py slides.pdf /tmp/pages`, then batch-upload the generated PNGs in the presenter workspace. Direct in-browser PDF/PPTX conversion is still pending; conversion should eventually run in an isolated worker.

## Access control

Only authorized session presenters may create slides, using a session-owned image uploaded by a presenter. The public image endpoint responds only while the corresponding slide is current in an active, unexpired session. No privileged tokens are embedded.

## Limitations

Database and browser end-to-end testing remain pending. Slide pages do not accept answers or modify quiz history. Animations, transitions, and embedded video are not preserved. The offline conversion tool is not sandboxed: run it on trusted input or in an isolated container.
