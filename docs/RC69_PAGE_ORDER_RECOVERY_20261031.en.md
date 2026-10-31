# RC69 — Thumbnail JSON export reconciliation and authoritative reorder recovery

**Committed baseline:** `487c960f09b3c9adb996d489f44b52d059da12b2`, standard CI `41191213305`, full campaign `41191751069`. RC66–RC69 have **not** been declared committed. No assistant commit, push or image publication.

## Evidence-bound credit (+0.50 percentage points)

Successful full CI quality job `124509777927` executed `tools/ci_browser_editor.py` against a **compiled production React frontend in real Chromium**. The tested presenter opened a specific page's thumbnail menu, selected **Esporta layout JSON**, awaited an actual browser download, and checked that the generated file existed. This page-specific browser-download capability is **not** the previously credited A2-ORDER thumbnail ordering/layout and **not** the A3-AUTO page autosave or CAS. It does not establish the correctness of a full JSON import/export roundtrip.

The A2 partial residual weight is reduced 4 → 3 and the new `A2-PAGE-JSON` accepted gate has weight 1. Total remains 100, score becomes **84.75%** (42 accepted, 17 partial, 59 gates). This reconciliation uses **prior green GitHub evidence**, not the untested changes in this package.

## New software code (not certified by the old CI)

- A page reorder now always fetches the authoritative server snapshot, even when the PUT returns a transport error. It does **not** retry an ambiguous write (which could overwrite another collaborator's changes) or assert that the previous order survived.
- The UI distinguishes a confirmed write, server-recovered committed write, rejected write and concurrent reordering. A failed authoritative GET leaves an explicit **unknown** state requiring reload.
- New TypeScript unit tests cover committed-but-lost acknowledgements, rejection, concurrent updates, unavailable readback and changed page collections.
- A new Playwright proof runs the **compiled React editor** in native Chromium, Firefox and WebKit at 1440px / 390px. It exercises genuine HTML drag and drop, an acknowledged response lost **after commit**, HTTP 409 rejected reordering, and Alt+ArrowUp keyboard persistence. It uses isolated in-memory HTTP fixtures; it does not use production data.

**New browser proof is pending the next GitHub standard and extended campaigns.** npm package installation cannot complete locally due registry DNS being unavailable; the TypeScript/Vite build is consequently not claimed as locally verified. Do not promote native drag/drop, assistive-device, physical touch or independent visual fidelity gates until further evidence. Publishing and strict RC remain disabled.
