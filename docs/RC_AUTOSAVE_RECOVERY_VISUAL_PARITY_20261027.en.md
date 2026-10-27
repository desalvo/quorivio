# Quorivio 0.1.0-dev — Resilient autosave and shared widget geometry (27 October 2026)

## Baseline and evidence

- User-confirmed GitHub baseline: `67a7be939a5930e2f9a49ce3932a4b7f29a682ac`.
- Workflow `40553571012`: quality, Chromium with PostgreSQL, containers and publishing passed **for the baseline**. This new batch has not yet passed CI.
- Formal weighted RC score: **53.0%**; no unearned gate promotions. Independent acceptance is still required for A1–A4 and other gates.

## New changes after commit

1. Autosave identifies transient transport failures separately from application errors and checks the authoritative server revision before any retry.
2. A lost response after a committed PostgreSQL PATCH is recovered by read-back, without duplicate writes or spurious conflict indicators.
3. At most three automatic retries with bounded exponential backoff, only if the server still has the expected prior revision.
4. Diverging concurrent writes trigger the existing reconciliation workflow without discarding local drafts.
5. Retry identity includes the page and draft signature; it cannot leak across pages.
6. The editor, presenter projection and participant canvas use a single CSS percentage geometry helper. Independent pixel-accurate visual parity remains pending.
7. The Chromium mocked-API fixture now simulates request loss before and after commit. The real PostgreSQL/Chromium fixture remains completely unmocked and mandatory.
8. Frontend Node tests were added to the mandatory production quality gate.

## Local verification

- Complete Python suite: **842/842 PASS** (with `PYTHONPATH=tools`).
- Backend Node: **447/447 PASS**.
- Frontend Node: **12/12 PASS**.
- TypeScript/TSX parse: **PASS**.
- Browser Python syntax: **PASS**.
- Full React/Vite build and new GitHub Chromium/PostgreSQL acceptance: **pending**.

## Outstanding RC work

A1/A3 still require the integrated browser acceptance, independently validated pixel-accurate editor/projection comparison, cross-browser and physical device checks, and independent accessibility review. No premature RC sign-off or score inflation.

**Git rule:** do not commit, push, tag or publish automatically. Provide a one-line English commit suggestion cumulative since the baseline.
