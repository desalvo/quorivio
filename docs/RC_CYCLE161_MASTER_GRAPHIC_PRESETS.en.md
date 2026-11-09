# RC161 — Slide master, Arial defaults and caption-free graphics

## Changes

- Arial is the effective default for titles, footers and other text widgets in both the standard and slide-master editors, including mobile; explicit user font choices remain intact.
- In **Edit masters**, upload an image or select one from the session library. **Save master** persists a shared background image for desktop slides without their own image. A page-level image takes precedence; independently authored phone backgrounds remain separate.
- Master images are accessible only while the page is live, protected against accidental deletion and included/remapped in portable `.quo` backups.
- Lines and shapes no longer render text labels or descriptions. Use a simple click for the default object, right-click, a 560-ms long touch, ContextMenu or Shift+F10 for a preset picker with arrows, dashes, shapes, stroke widths and optional fill. Presets are stored in the usual validated style fields and remain editable through the widget format inspector.

## Validation and remaining acceptance

Run `node --experimental-strip-types --test apps/web/test/*.test.ts apps/api/test/*.test.ts` and `python3 -m unittest tools.tests.test_rc161_master_background_graphics -q`. Live acceptance should compare participant/presenter and editor backgrounds for a slide with local image and one inheriting the master, including a separate mobile layout. **Full GitHub CI and authenticated end-to-end acceptance are still pending.**

**Certified status:** 85.25% (43 accepted, 17 partial). Keep `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
