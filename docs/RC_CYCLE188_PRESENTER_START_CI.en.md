# RC188 — Presenter/audience startup routing CI reconciliation

## Failure
GitHub Actions run `42011405908`, job `127191083032`, fails before npm: historical RC92 test requires the obsolete SQL `ORDER BY position,id LIMIT 1`. RC185 introduced presenter-hidden pages and explicit audience page routing.

## Required semantics
- First presenter page is the first page *visible to the presenter*, in stored order.
- Audience can be assigned a different, presenter-hidden page.
- Start is atomic under a session row lock, closes previous audience pages and opens exactly one answer-collecting audience page.
- Both presenter and audience pointers are set together; subsequent starts do not rewind timers.
- Missing audience targets fail closed; legacy SQL `LIMIT 1` cannot be reintroduced.

## Tests
Historical RC92 contract updated. Added an early RC188 Python guard with negative mutations and a real TypeScript routing behavior assertion, before RC92/npm in CI.

## Status
No runtime behavior modified. Local results in `docs/validation/RC_CYCLE188_LOCAL_ACCEPTANCE_20261105.json`; full compiled build and subsequent GitHub CI remain pending. Certified **85.25%**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
