# Real PostgreSQL Chromium editor — independent-field fixture correction (2026-10-25)

## GitHub evidence

- Full workflow run **40220288310**, quality job **121250301296**: failure in `tools/ci_browser_editor_postgres.py:101` expecting the message `Nessun conflitto sui singoli campi`.
- The ARIA snapshot instead showed a **legitimate** unresolved `/widgets/pg-first/position/x` conflict: local **12**, remote **10**. The preceding persisted coordinate was **11**.
- The fixture erroneously called `draft('Remote collaborator')`, resetting the remote widget coordinate to **10** while also changing its label. Thus both authors changed `x`; the merge engine correctly refused an automatic resolution.
- In the same run, the opt-in mock Chromium editor gate, PostgreSQL HTTP CAS smoke, and real PostgreSQL Chromium participant gate had progressed past their earlier failures; the production container and publication jobs were skipped after quality failed.

## Correction

- New pure helper `tools/ci_editor_collaboration_fixtures.py`: builds a label-only remote update from the **latest server activity snapshot**, deep-copying the existing page and result designs and using its actual `design_revision` for CAS.
- The real browser test fetches the current activity before the collaborator write, asserts revision 3 and the unchanged coordinates **[11, 41, 75]** after revision 4, then checks that the independent local x=12 and remote label edits rebase without a conflict.
- The subsequent deliberate same-label conflict and explicit resolution remain in the browser test; no conflict checks or safety controls are bypassed.
- Eleven Python behavioral regressions verify exact single-field mutation, immutable inputs, preserved geometry and result data, current CAS revision, other widget IDs, invalid fixtures, and that the browser test uses the helper rather than a reset-to-original payload.

## Acceptance / remaining

- Local validation: **644/644 Python tests PASS**, **314/314 Node tests PASS**, backend TypeScript and frontend TypeScript/Vite builds PASS, isolated Chromium desktop/mobile viewport checks PASS. ZIP integrity verified on packaging.
- Real PostgreSQL + full browser end-to-end **requires a new GitHub `browser_test=true` run**. Do not mark the editor gate accepted before it passes. Weighted RC score remains **45.5%**.
- No commit, push, tag, deployment or release was performed by the assistant.
