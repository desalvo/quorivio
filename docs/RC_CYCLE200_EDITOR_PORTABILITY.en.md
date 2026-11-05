# RC200 — Editor session portability, PDF/PPTX and privacy exports

## Baseline
RC199 full GitHub Actions CI green: https://github.com/desalvo/quorivio/actions/runs/42096705867 (14 successful jobs, optional Docker Hub publication skipped). Version remains `0.1.0-dev`; release/publish flags remain disabled.

## Editor
- Editor action buttons remain in the primary row; presentation title and primary owner are compact labels underneath.
- Removed duplicated "Edit schemes" control from the page-thumbnail sidebar; horizontal ribbon navigation remains.
- Thumbnail contextual "Import PDF/PPTX" uses existing authenticated isolated converter, inserts converted pages after the selected thumbnail and persists the order. Converter activation is required.

## Portable session
- Standalone `.quorivio` is a versioned private bundle with checksummed binary assets and slide raster snapshots. Import into a different account creates fresh session, page, and asset identifiers, new join secret and ownership; excludes participants, individual responses and aggregates. Inherited live QR bearer data is not preserved.
- PDF/PPTX exports use the isolated LibreOffice/PowerPoint worker and private stage; export of imported media slides embeds verified snapshot pixels as a background before overlaid native widgets. PowerPoint widget fidelity remains subject to the worker's documented native feature limits.

## GDPR statistics
- Explicit anonymization checkbox defaults on. Anonymous CSV/XLSX aggregates choices/ratings/reactions, omits individual identity, timestamp, free-text content and uploaded file identifiers. This is *data minimization*, not a mathematical guarantee against re-identification from tiny counts or sensitive question wording; review before distribution.
- Primary owner alone may disable anonymization. CSV escapes spreadsheet-formula prefixes; XLSX text cells are encoded as data, not formula cells; max 50,000 records.

## Verification and limitations
- Full local Node suites: 609 API and 348 frontend passed; focused Python tests and real LibreOffice PDF smoke passed. The broad 2,039-case Python run exposed two historical check incompatibilities (qualified `a.id` after a joined portable export and incomplete ambient TypeScript cache in an isolated fixture); both contracts were reconciled and 10/10 targeted tests subsequently passed. The complete Python suite was not rerun after those changes. API/frontend full build, Chromium, PostgreSQL integration and RC200 GitHub full CI must be confirmed on a committed RC200.
- `rc_strict=false`; `publish_image=false`; `publish_latest=false`. Certified completion stays **85.25%** (43 accepted, 17 partial). Do not commit/push/tag without maintainer request.
