## 2026-10-24 — Native PPTX table-cell recovery (current behavior)
PowerPoint native table text is flattened into **editable, independently positioned text widgets**, one per nonempty cell, up to the existing **16-widget/page** capacity. Original native table formatting, borders, merged-cell semantics, and underlying OOXML table objects are **NOT preserved**. The fidelity report exposes `editable_table_cells`, `table_cells_over_page_limit`, and `unsupported_tables`; a PPTX containing tables is always marked lossy. The browser/worker path uses this same converter; physical browser and Kubernetes tests remain pending.

**IT:** il testo delle celle delle tabelle PPTX diventa modificabile come widget singoli; la struttura tabellare originale non è conservata. La diagnostica segnala le perdite e il limite massimo di widget.

**Important:** Historical sections below document prior limitations when written; consult this section and source/tests for the current table behavior.


## October 23: embedded-image PPTX export
Browser export now stages referenced PNG/JPEG session media through the authenticated API into a private converter workspace. SHA-256 and size are checked before isolation; images are exported as PowerPoint picture elements with editable geometry and rotation. A session with missing image files, unsupported image formats or excessive media size fails explicitly instead of silently dropping them. The export does not preserve live quiz interactivity. Browser and Kubernetes acceptance remain pending.

# PowerPoint portability / Portabilità PowerPoint — 0.1.0-dev

## Current implementation / Implementazione attuale

The browser already imports PPTX/PDF through a configured conversion worker, preserving the visual appearance as raster slide pages. Those backgrounds are **not** independently editable PowerPoint shapes. The browser already exports/imports `quorivio-session` JSON, without private votes. This cycle fixes JSON import of `slide` activity pages and adds a **separate opt-in command line converter** for PPTX editable text boxes:

```bash
python -m pip install python-pptx
python tools/pptx_portable.py import deck.pptx quorivio-session.json
# Import the JSON in the browser: Session portability -> Import definition JSON
# Export session JSON in the browser, then:
python tools/pptx_portable.py export quorivio-session.json exported.pptx
```

La conversione testuale preserva **contenuti e geometria approssimativa delle caselle di testo**, modificabili come widget Quorivio; i widget nativi di quiz/sondaggi sono esportati in PPTX come **testo statico**, perché PPTX non supporta la logica server per la partecipazione live. La geometria dei widget è adattata ai vincoli dell'editor Quorivio. Il limite per pagina è 16 widget, 200 pagine per file.

### Explicit limitations / Limiti espliciti

- Fonts, paragraph/run-level styling, themes, masters, charts, tables, shapes, embedded images and animations are not reconstructed as editable elements by the CLI converter.
- Do **not** claim pixel-perfect fidelity or a complete browser-based PPTX export. The CLI converter requires `python-pptx` and is not bundled in the production API/converter container.
- For visual preservation, retain the existing raster-based browser import; for editable text, use the new JSON route. Combining both tracks into one editable overlay, plus a browser PPTX export, is future work.
- Local PPTX creation and loading are offline; **do not run untrusted macros** (the converter does not execute VBA).
- Imported Quorivio JSON excludes assets and user response data; export/import round trips do not embed uploaded images. SSO secrets, passwords, credentials and answers must not be serialized.

### Mobile

The browser includes responsive layouts for participant-facing interactive widgets. This cycle adds mobile hit targets, non-overflowing activity actions and an editor widget stack at <=480px. Stored canvas percentages are unchanged; mobile reflow is a presentation-layer layout, not a rewrite of saved slide geometry. Manual touch-device acceptance tests are pending.

## Acceptance gates outstanding

A complete solution requires shape-by-shape import with faithful font/layout semantics, secure asset embedding or remapping, integration in browser UI, browser download of full PPTX, graphical editing on physical phones/tablets and real browser/Kubernetes roundtrip tests. These gates remain OPEN.

## Incremental text style round-trip / Stili testuali conservati

The optional converter now reads a representative text run for each editable text box and preserves explicit font family, size (10–96 pt), bold, italic and fixed RGB text color. Export applies these values to PowerPoint text boxes. Text containing multiple styles in the same shape is **flattened to the first non-empty run**, while theme colors, paragraph alignment and line spacing are not guaranteed. The visual-raster import path remains appropriate where visual fidelity is more important than editability. A local PPTX → JSON → PPTX font/color regression was executed. Browser export and complete fidelity remain open.

Il convertitore facoltativo conserva ora, per ogni casella di testo, lo stile del primo segmento non vuoto (font, dimensione, grassetto, corsivo e colore RGB esplicito); il testo con stili misti viene appiattito. L'importazione grafica rimane la scelta corretta per mantenere l'aspetto originale, mentre la conversione testuale consente la modifica nel canvas.

## Import safety and supported fonts (current cycle)

The optional editable-text converter now rejects malformed/non-OOXML ZIP input, presentations exceeding 50 MiB compressed or 250 MiB expanded, archives with more than 3,000 entries, and packages carrying VBA binaries or executable file payloads. This check precedes python-pptx parsing. It is not an antivirus or a substitute for an isolated conversion worker.

Quorivio's page-design validator currently accepts only Arial, Georgia, Verdana, Tahoma, Trebuchet MS, and monospace. To keep converted JSON importable, an unsupported PowerPoint font is omitted from the editable widget style (the app default takes over). **This loses font fidelity intentionally**; it does not substitute a visually identical font. Other PPTX formatting limitations in this document remain open. Import/export directly in the browser is not yet implemented for the editable path.

Il convertitore opzionale ora applica limiti alla dimensione compressa/decompressa dei PPTX, al numero di file interni e rifiuta macro/binari. I caratteri non ammessi dal validatore di Quorivio non vengono serializzati: la pagina resta importabile, ma la fedeltà tipografica non è garantita. L'importazione e l'esportazione modificabili direttamente dal browser rimangono da implementare.

## Slide headings and text rotation (incremental)

The optional editable converter now derives each slide's Quorivio page title from the
first nonempty text line (maximum 160 characters) and preserves the rotation of
editable text boxes on import and export. The headings are an authoring convenience,
not a reconstruction of PowerPoint title placeholders. The existing 16-widget/page
cap, text truncation, raster fallback, and unsupported OOXML features remain unchanged.

Il convertitore CLI ricava il titolo della pagina dalla prima riga testuale non vuota
e conserva la rotazione delle caselle di testo durante il round-trip. Non preserva
ancora l'intera formattazione PowerPoint; l'integrazione nel browser resta aperta.

On narrow screens, participant input labels wrap, radio/checkbox controls receive
larger touch targets, and text responses use the available viewport width. Stored
slide geometry is not rewritten. Physical mobile-device tests remain required.

## Browser integration (2026-10-23)

The session dashboard now offers **Import editable PowerPoint** (creates a **new** session) and **Export PowerPoint**. Both require `QUORIVIO_ENABLE_CONVERTER=true`, a correctly configured private converter worker, a shared conversion volume and `QUORIVIO_WORKER_TOKEN`. Build/deploy the matching updated `Dockerfile.converter` image; its `python-pptx` dependency is pinned to `1.0.2`. The API never executes document conversion inside its own process. Import is limited to 50 MiB compressed PPTX, and portable JSON is limited to 2 MiB. The existing raster import remains separate.

**Important limits:** Editable PPTX currently covers supported text boxes, approximate geometry, rotation and simple uniform styles; images, tables, themes, SmartArt, charts, animations and mixed inline styling are not preserved as editable objects. PPTX export is static: interactive Quorivio controls cannot function inside PowerPoint. The Quorivio JSON remains the format for full widget definitions (not embedded media binaries). Mobile layout changes have not been physically device-tested. Integration and fidelity remain pending browser/cluster acceptance.

## Fidelity diagnostic / Diagnostica fedeltà
The isolated converter now returns a metadata-only `fidelity` object in editable-import API responses with counts of pictures, tables, charts, other unsupported shapes, excess text boxes, and a non-16:9 warning. These elements are **not imported as editable assets** yet. The report contains neither extracted text nor binary data. Explicit text underline also round-trips. The mobile experience and PPTX object fidelity are still not accepted end-to-end.

Il convertitore restituisce un rapporto `fidelity` con il numero di elementi omessi, senza testo o media. Le immagini e le forme non diventano ancora elementi modificabili; non attribuire una fedeltà completa a questo import.

### Embedded image extraction (2026-10-23)
Editable browser PPTX import extracts PNG/JPEG pictures as individual image widgets and registers their bytes in the new session asset library. Bounds: 10 MiB per picture, 50 MiB total, max 200 imported pictures, and max 16 widgets per slide. IDs, sizes and SHA-256 are checked by the API before registering assets; failure removes the new session's staged assets. This does not implement the inverse image export to PPTX or portable media-inclusive Quorivio bundles. Fidelity is not guaranteed for crop effects, grouped shapes or theme assets. Requires browser + real PostgreSQL acceptance.

## Native OOXML geometry fidelity (2026-10-23)

Editable native PPTX import now preserves small text boxes and logos as percentage positions with four-decimal precision rather than enlarging objects to the former 12% width / 8% height minimum. The API validator accepts positive geometry down to 0.01% while rejecting off-page widgets. This also applies to editor-created widgets; the UI may impose separate interaction-size constraints, so verify touch editing. The fidelity report explicitly flags off-canvas shapes as lossy. PPTX uses native OOXML parsing/writing through python-pptx in the isolated worker; no Microsoft Office or LibreOffice installation is required for the editable route. Native support is **not** equivalent to exact visual round-trip: themes, complex geometry, charts, SmartArt, grouping, animation and font substitution remain unsupported.

## Native PPTX media deduplication and package safety (2026-10-23)

Repeated identical PNG/JPEG pictures across multiple PowerPoint slides are now stored once during editable import (keyed by SHA-256 and MIME type), while each occurrence remains an independent canvas image widget with its own geometry. The 200-asset and 50 MiB media limits apply to distinct stored image assets. PPTX OOXML members containing traversal paths, absolute paths, backslashes, encrypted members, or duplicate archive names are rejected before conversion. This is defense-in-depth; it does not certify fidelity of complex PowerPoint objects.

Import/export remains lossy for shapes, charts, SmartArt, grouped objects, animations, and complex theme formatting. Native PPTX means OOXML parsing and writing without Office installed, not pixel-perfect fidelity. Browser, PostgreSQL and Kubernetes acceptance remain pending.

## Native image MIME guard (2026-10-23)

Editable PowerPoint picture extraction now requires **both** an explicitly supported
PNG/JPEG MIME type and an image within the per-file limit before checking the
remaining asset quota or the deduplication cache. This closes a boolean-precedence
bug that could otherwise place unsupported embedded image bytes in the private
asset staging directory. Unsupported image types are skipped and remain visible
in the fidelity report. A dedicated mocked MIME regression test accompanies the
existing image round-trip and archive-hardening tests. **Native editable vector
shapes, tables, charts and full OOXML visual fidelity remain open.**

### Native rectangular shapes
Rectangular and rounded rectangular auto-shapes containing text now import as editable `postit` widgets; exporting a postit uses a native editable PowerPoint rectangle. Original fills, outlines, corner radius and group structure are not preserved.


### Native shapes: fills and strokes
Rectangular and rounded rectangle text shapes preserve explicit RGB fill, stroke, and rounded geometry in the editable widget style; theme-driven colors, gradients, complex paths, group transforms, and shape adjustments remain unsupported.

### Native editable ellipses and triangles (2026-10-23)

PPTX oval and isosceles-triangle autoshapes containing text now import as editable `postit` widgets with a validated `shapeType` (`ellipse` or `triangle`). Both re-export as native, editable OOXML shapes. Explicit RGB fills and outlines use the existing `fillColor` / `strokeColor` widget styling. The presenter displays ellipses using elliptical corners and triangles using a CSS clip-path; this is an approximation of PowerPoint's precise text layout and outline. Shape adjustments, gradients, theme-driven colors, grouping, non-text autoshapes and animation remain unsupported. Existing rectangular widget data is unchanged. End-to-end browser fidelity acceptance remains pending.
