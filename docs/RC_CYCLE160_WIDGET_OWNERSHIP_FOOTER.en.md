# RC160 — Widget-only audience participation and accessible footer

The real participant page now shows only content expressly placed by the presenter. Removed the unconditional mount of the old “Word cloud and questions from the audience” panel and the automatic reactions bar outside the slide. Interactive authored `question`, `topic-question` and `reactions` widgets remain fully available, and historical quiz/poll activity input is preserved only when the activity has no authored page widgets. Historical API endpoints remain for backward compatibility; this change governs participant rendering.

**Footer:** accessible reading order places the footer and slide number after all other widgets. The default smartphone footer is positioned at the bottom of the mobile document even when it was inserted first; explicit authored mobile overrides remain respected. Default smartphone rating height now accommodates optional comments and the 0–9 vote controls.

**Rating:** `RatingCommentField` is shared between editor, previews and live participation; stronger theme-independent CSS ensures its text area is visible, white and readable. Chromium computed-layout tests for 1440/390 px, Node tests and Python mutation guards protect these contracts. Authenticated real-server screenshot comparison is still required.

**Release safety:** no changes to authentication, authorization, database, billing or the 500-participant load-test pipeline. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Certified completion remains **85.25%** (43 accepted, 17 partial) pending new CI evidence.
