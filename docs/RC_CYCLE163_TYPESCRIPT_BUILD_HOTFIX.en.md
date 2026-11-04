# RC163 — TypeScript build regression hotfix

GitHub Actions run 41756050958 (commit `e926015e12952643ec08ea7d35e4fc9dee4ed7ee`) failed in **Compile frontend and backend** with 4 TypeScript errors in `apps/web/src/main.tsx`:

- TS2339 at line 2119: `showQrUrl` missing from the local history editor widget `Pick<>` type, although it is present in the canonical `PageDesign` type and validated by the API.
- TS2367 three times on line 2145: non-graphic widget rail branch tested `k==='shape'` / `k==='line'` after TypeScript had already narrowed out those kinds.

The hotfix includes `showQrUrl` in the local `EditorWidgetPermissionFields` and removes unreachable graphical-only conditions from the non-graphic insertion branch. It preserves the dedicated `GraphicInsertTool` for lines and shapes, desktop and mobile edits, QR title and URL preferences, all prior RC162 functions, and the previous inventory unmodified.

The new `test_rc163_frontend_typescript_build.py` is run *before* npm and contains negative-mutation regressions. TypeScript/Vite build and real browser acceptance require confirmation in the new GitHub CI run; no source gate was promoted from a failed run. **85.25% certified** (43 accepted / 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
