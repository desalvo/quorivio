# RC189 — Typed portable page remapping and early strict TypeScript CI

## GitHub failure

Workflow run `42021367453`, job `127224676741` (commit `d1540d215638ee893e480fdad152dd116135be8a`) passed the historical RC92 preflight and unit tests, then failed during the backend `tsc -p tsconfig.json` build with two `TS2345` errors at `apps/api/src/server.ts:982`. The inferred `Map<unknown,unknown>` could not be passed to `remapPortablePageRouting`, whose contract is `ReadonlyMap<string,string>`.

## Fix

`createFromPortable()` constructs an explicit `Map<string,string>` and adds only imported page IDs narrowed to strings. Missing IDs in older portable archives remain optional and cannot accidentally become an `undefined` map key. Remapping for both public-page assignments and cross-page results remains unchanged. No URL, permission, or revision bypass is introduced.

## CI regression guard

`tools/tests/test_rc189_portable_map_types.py` exercises the exact server snippet using Node 22 and, where standalone `tsc` is available, checks a strict TypeScript compile and a negative mutation that reconstructs the original `TS2345`. CI executes the quick contract before npm and **the actual strict API compiler** immediately after npm, before lengthy browser/PostgreSQL tests. The normal full frontend/backend build remains mandatory later.

## Verification and limits

Local checks: Python contracts, isolated strict TypeScript, 599/599 API Node tests and 321/321 frontend Node tests. The full project build and the CI campaign on RC189 are **not yet verified**; only GitHub can confirm them on the new commit. Certified gate score stays 85.25% (43 accepted, 17 partial). CI is non-publishing; no assistant commit, push or tag.
