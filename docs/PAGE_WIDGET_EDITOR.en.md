# Page and widget editor (0.1.0-dev)

- Pages can include multiple widgets. Drag to reorder or use the accessible up/down buttons.
- Each widget exposes controls for title, optional description, answer mode and text styling (family, size, color, bold, italic, underline, strikethrough and animation).
- Ratings require a nonempty title. Participants can submit an optional comment up to 1,000 characters alongside the rating; comments are stored in PostgreSQL and are not included in public aggregates.
- Double-click a title input to select its text, edit and save.
- Question widgets are supplementary visual blocks; independent submissions per widget still require an additional data model.
- Reduced-motion accessibility is required. Full browser/database tests remain pending.
