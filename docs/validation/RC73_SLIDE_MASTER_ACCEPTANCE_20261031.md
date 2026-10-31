# RC73: editable Title slide master and contextual Footer

- New `POST /api/sessions/:id/pages` and new poll/quiz activity insert a visible `title` widget stored in `page_design.widgets`.
- Titolo follows activity title until deliberately unlinked. Default style is bold/centered/large/transparent. Session master stored in `session.theme.master.titleStyle`; `PATCH /api/sessions/:id/design` validates and stores it.
- Footer is insertable via drag/touch from palette, defaults to bottom full width / one line, session title center and current page number right. Custom text and both visibility switches are in widget properties.
- Page number is calculated against current ordered activities, never frozen to a widget value. The thumbnail sidebar also displays the number below the thumbnail.
- Projection, rehearsal and participant views use the same semantic labels; OOXML export creates editable title/footer textboxes.
- Positive/negative API contract: `apps/api/test/slide-master.test.ts`; pure layout: `apps/web/test/slide-master.test.ts`; editable PPTX acceptance: `tools/tests/test_rc73_slide_master.py`.
- Do not promote the RC acceptance percentage on this uncommitted local package. Browser/TypeScript/API PostgreSQL acceptance and real GitHub workflows are still required.
