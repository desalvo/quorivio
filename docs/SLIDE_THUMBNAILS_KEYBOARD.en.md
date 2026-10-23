# Slide filmstrip: geometry thumbnails and keyboard ordering (2026-10-23)

The presenter filmstrip now renders each page's own title and up to 24 saved widgets at their saved x/y/width/height percentages and rotation. Existing background imagery is used when available; image/video widgets are represented by small media symbols, **not** decoded media previews. The preview is DOM/CSS-based, not a screenshot or a full participant rendering. Widget-specific styles and all overflow clipping are therefore approximate. The legacy title-only tile is no longer used for pages with widgets.

Drag a filmstrip page onto another to reorder it. For keyboard use, focus a page and press **Alt+Left** or **Alt+Right**. This calls the existing server-side page-order endpoint; ordering is disabled for closed sessions. The separate page list and its reordering buttons remain available. No response data is modified by rendering thumbnails.

Verified: 85 Node tests and 88 Python tests locally, including two static regression checks for this feature. Not verified: Vite/TypeScript full build (offline npm dependencies missing), cross-browser drag and keyboard use, screenreader behavior, real database/session integration, and accurate rendering of individual uploaded assets. No claim of full RC readiness.
