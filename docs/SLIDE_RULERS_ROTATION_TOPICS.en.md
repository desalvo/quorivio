# Slide editor, preview and topic questions — 0.1.0-dev

The session dashboard opens the slide editor. Each page has a white 16:9 canvas with horizontal and vertical percentage rulers. Drag widget interiors to move, borders to resize, and the circular handle above each widget to rotate it by any angle between -360 and +360 degrees. Layout data persists position, size and rotation. Fullscreen editing and drag-and-drop slide ordering are available.

At mobile widths of 700px or less, the live page reflows widgets into readable vertical blocks instead of clipping the desktop geometry; saved desktop rotation is suppressed only for mobile presentation. Real-device testing remains mandatory.

The dashboard provides an embedded presenter-screen preview and an external link to the live projection/results page. Unlike the local participant rehearsal, this preview reflects the actual session state.

Use the `topic-question` widget for subject-scoped audience questions; multiple topic widgets may coexist. Each participant may submit up to ten questions per widget, between 5 and 2000 characters. Presenter lists are separated by widget, have ten questions per page, and refresh periodically. The presenter may optionally enable showing participant pseudonyms (off by default). Email addresses are never exposed.

Open: CI/frontend build, real PostgreSQL migrations and end-to-end browser tests, assistive-technology review, topic-specific moderation and historical preview independent of the active activity.
