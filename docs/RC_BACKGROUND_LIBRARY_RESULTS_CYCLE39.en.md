# RC cycle 39 — background library and result presentation

Backgrounds are uploaded into a presenter's personal library. Presenters who collaborate in at least one shared session can select each other's backgrounds across their own presentations; when used, the backend creates an independently owned copy in the receiving presenter's library before applying it to the session. Page backgrounds remain separate session-scoped assets, preserving portability and avoiding reliance on a former collaborator.

The blank-canvas context menu and page settings use the same library flow. CSS no longer forces white over a page image. The linked source question/quiz/poll controls the Result widget's view; the word cloud animates with a reduced-motion fallback.

**Verification limits:** local unit/static tests only; real PostgreSQL 18, browser and multi-presenter E2E remain pending after commit. Formal RC score remains 80.75%; no final GDPR/AGID acceptance claimed.
