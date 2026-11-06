# RC213 — Page-order React hook TypeScript recovery

## CI failure
GitHub Actions run `42140973603`, quality job `127640902633`, failed at `RC196 strict frontend TypeScript typecheck before extended CI` with `TS2448` and `TS2454` on `apps/web/src/main.tsx`, line 2132: the shortcut `useEffect` dependency array referenced `pageOrderPending` before its `useState` initialization. API TypeScript and earlier preflight contracts had passed; remaining jobs were skipped. This is a genuine frontend compilation failure, not an obsolete historical assertion.

## Corrective changes
Moved the `pageOrderPending` state initialization into the unconditional top-level `App()` state declarations alongside `pageBatchBusy`, before the thumbnail keyboard effect reads its value. Preserved the Ctrl/Cmd multi-selection, D/R/Backspace, drag/reorder blocking, page-change confirmations, and all RC204–RC212 features. Introduced a fail-closed RC213 Python test with three negative mutations, registered in the pre-npm quality gate. The existing strict frontend TypeScript compiler gate remains mandatory.

## Validation and release policy
Version **0.1.0-dev** unchanged; **85.25%** certified (43 accepted, 17 partial gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Current release source and ZIP are checked against the grouped SHA-256 inventory; all historical CI verifiers retained. Targeted Python regressions run locally; the full frontend typecheck requires the npm dependency tree and GitHub full CI. No commit/push/tag made by the assistant. Last full-green CI remains RC203 `42110429701` until a later full run succeeds.
