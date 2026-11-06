# RC212 — Public projection and presenter numbering CI reconciliation

## Evidence
RC211 full CI [42140039942](https://github.com/desalvo/quorivio/actions/runs/42140039942) stopped at `test_rc185_cross_page_projection`: the historical contract rejected **even internal use** of `presenter_activity_id` inside the public snapshot producer. Since RC206, it is used internally to calculate the presenter-visible footer ordinal, shared with the participant screen without gaps for presenter-hidden pages.

## Fix
Application runtime remains unchanged. The historical RC185 source slice now ends at the real function boundary; the old newline-brace delimiter could include subsequent functions. The test allows internal ID use while ensuring the **public response excludes it**. The response retains `presenter_page_number` and only exposes the published audience page and authorized scoped statistics.

A new pre-npm RC212 Python guard adds negative mutations for leaking the private ID, expanding visible page scope or changing the published activity. Four Node tests execute the **actual projection function** extracted from `server.ts` with minimal stubs: synchronized numbering, no private IDs/secrets, audience-only content, no closed-page disclosure and suppression of disabled results.

## Status
Version `0.1.0-dev` unchanged; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No runtime, database or authorization changes. RC212 full CI pending; most recent full-green CI RC203 `42110429701`. Certified functional completion **85.25%** (43 accepted, 17 partial). No commit, push or tag.
