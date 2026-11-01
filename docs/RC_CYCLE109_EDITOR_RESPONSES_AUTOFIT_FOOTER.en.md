# Quorivio 0.1.0-dev — RC109 — answer controls, auto-fit and single-row footer (1 November 2026)

**Baseline:** RC107 GitHub full CI `41309042012` SUCCESS; the maintained SHA `99a801ab7623347ba776b8214d054aa872ddb5c6` is published on Docker Hub. RC108 and RC109 are local cumulative changes **not yet GitHub-CI certified**.

**Editor and answer controls:** Questions, timed quizzes and audience-topic questions now show their real (disabled preview) Submit button on the edit canvas, including independent nested questions. Answer text boxes and options have independently configurable font family, font size, text color, bold and italic; the answer button font size (12–40 px) is configurable from the PowerPoint-like floating ribbon and the widget properties dialog. Shared style helpers apply in the authenticated participant surface, rehearsal and editor. Fields are validated strictly by the API and cannot smuggle arbitrary CSS or HTML.

**Auto-fit:** Eligible text/interactive widgets expand to fit their content by default after text, font, or answer-control changes. Growth is bounded to the 16:9 slide and uses the existing collision-rejection policy. A manual edge-resize or Shift+Arrow resize disables auto-fit only on that widget; a Properties checkbox reenables it. The algorithm never silently moves other widgets or writes outside the canvas. If the slide has no free space, content cannot be guaranteed to fit without manual rearrangement (deliberate fail-closed choice).

**Footer:** New footers use a 7%-height single-row strip starting at 93%, center the session title horizontally, add a subtle separator line above, keep transparent background, and preserve the independent 10 px lower-right page number. Previously saved custom geometries remain unchanged; legacy normalization still works.

**Previous cumulative RC108:** Native editable PowerPoint export of grouped questions and rich text with no answer-key disclosure remains included.

**Verification:** API Node 565/565; frontend Node 154/154; RC109 Python contracts and old footer/rehearsal contracts passed locally. Chromium real application and full CI remain to be verified via GitHub.

**Certified weighted completion:** 85.25% (43 accepted / 17 partial, 60 gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No additional gate credit without evidence. Suggested cumulative commit since RC107: `Export grouped questions to PPTX and improve editor answers, auto-fit and slide footers [full-ci]`. No assistant commit, push, tag or image publishing.
