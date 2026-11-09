# Quorivio RC273 — API TypeScript hotfix

The RC272 full CI run [42547239843](https://github.com/desalvo/quorivio/actions/runs/42547239843) passed the historical preflight stages but stopped at the RC189 strict API TypeScript check, producing TS2352 in WebDAV, TS2769 in S3 and two TS2339 errors from audit request parameters.

Corrections: retain Node's streaming body and duplex half at the WebDAV fetch boundary with a narrowly scoped type conversion, convert S3 signed Buffer payloads into web-compatible `Uint8Array`, and type/validate the Express `id` parameter for audit records. Keep the RC272 inventory as historical and promote RC273 with a new complete SHA-256 source manifest.

The RC270 Node backup transports tests pass, and the three backup modules pass isolated TypeScript 5.8 typechecking against Node type definitions. A full dependency-enabled API build, GitHub full CI and real storage/restore/LDAP testing remain pending. The ledger-derived baseline remains 85.25% (43 accepted, 17 partial) with `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag.
