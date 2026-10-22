# PDF and PowerPoint presentation import — EN

Application version: 0.1.0-dev. Documentation build: dev-20261022.

## Implemented functionality

The **offline** `tools/import_presentation.py` command accepts PDF and PowerPoint `.pptx`, validates the signature and size (up to 100 MiB), caps the number of pages at 200, and creates one PNG per page, at most 1600 pixels on the longest edge. `manifest.json` records page count, source checksum and each PNG SHA-256 checksum. Requires `pdfinfo`, `pdftoppm`, and `libreoffice` for PPTX files.

```bash
python3 tools/import_presentation.py /secure/slides.pdf /secure/output-slides
python3 tools/import_presentation.py /secure/slides.pptx /secure/output-pptx
```

The destination must **not already exist** to avoid unintended overwrite. Production conversion must run in an isolated network-disabled worker/container with an unprivileged user, sandbox, CPU/memory quotas, a restricted filesystem and GDPR-aware cleanup. **These measures have not yet been integrated into the application runtime.** The CLI by itself is not a secure public upload service.

## Known limitations

No API or interface yet associates the rendered manifest with a session: output is staged for future import. Rendering flattens slides and does not preserve animations, transitions, embedded audio or video. Missing fonts and PPTX conversion may affect fidelity. Legacy `.ppt` is unsupported. Integrated PDF/PPTX session import, editable pages and browser previews remain pending.

## Verification

Local tests cover invalid signatures, unsupported content and rendering a sample PDF. Cluster, browser and database tests have not been run. Manifest hashes provide integrity evidence, not malware assurance.
