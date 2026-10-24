# Page editor selection and lifecycle stabilization

- Duplicating a page refreshes the server snapshot and selects the newly created page by comparing activity identities; it does not assume the server returns pages in insertion order.
- Focused page thumbnails support Arrow Up/Down and Home/End to select adjacent, first and last pages. This does not replace drag-and-drop or the dedicated reorder buttons.
- Closed sessions disable creation, deletion, duplication and reordering in the editor. The backend remains responsible for enforcing access controls.
- No API or database migration is introduced. Existing save-layout behavior is retained.
- **Not yet accepted:** unsaved-change prompting, full browser regression, real PostgreSQL and Kubernetes validation. Build requires npm dependencies and was not completed in this environment.
