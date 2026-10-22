# Graphical page sequence and page duplication

Version: 0.1.0-dev. Approved presenters (including authorized administrators) open a session and use **up/down** on an activity to reorder it, or **Duplicate page** to create an independent copy appended to the sequence.

The backend requires a complete permutation of the session's page identifiers, updates every position in a PostgreSQL transaction, and broadcasts a fresh WebSocket snapshot after committing. A live session may be reordered without changing the active page or historic answers. Closed sessions cannot be edited.

Duplication copies only definitions, quiz settings, styles and widgets, **not** votes, reactions or participant identifiers. The copy is appended at the end. Freeform drag-and-drop page canvas is still pending, as are PostgreSQL/browser integration and concurrency tests.
