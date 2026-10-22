# Graphical page sequence — drag and drop

In the presenter page list, drag one page row onto another to reorder. Changes are saved with the existing authorized and transactional `PUT /api/sessions/:id/pages/order` endpoint. Stable page IDs preserve historical responses and the currently active page. Accessible Up/Down buttons remain available for keyboard users and clients without HTML5 drag and drop support. Closed sessions cannot be reordered.

A new pure ordering module has four regression tests for forward and backward moves, no-op operations and invalid IDs. This **is not yet** a freeform visual canvas, a page preview storyboard, drag-to-create from the widget palette, or a substitute for multi-browser/PostgreSQL testing.
