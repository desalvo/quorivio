# Quorivio 0.1.0-dev — RC255: strict TypeScript / native Node ESM contract

## Incident and root cause

- RC254 full CI: https://github.com/desalvo/quorivio/actions/runs/42476782314 (commit `45bf2bea9ed09c82684012ffcaa0925dbaf48dd2`).
- Failure: `Production quality gate` / `RC197 reconcile Kubernetes Python integration contracts before npm` / `tools.tests.test_rc75_typescript_ci.RC75TypescriptRegression.test_strict_typescript_compilation_of_affected_independent_modules`.
- TypeScript TS5097 at `apps/web/src/slide-master.ts:2`: the RC75 standalone `tsc --noEmit --strict --moduleResolution bundler` invocation did not enable `--allowImportingTsExtensions`. RC254 introduced an explicit `.ts` import to the shared widget-font sanitizer; this import is valid for the actual project build and required by native Node TypeScript tests.

## Correction

- Enable `--allowImportingTsExtensions` only for the standalone no-output TypeScript check (`tools/tests/test_rc75_typescript_ci.py`), preserving `--strict`, `--moduleResolution bundler`, and `--noEmit`.
- Retain the `.ts` import in `slide-master.ts`: changing it to extensionless would jeopardize real native Node tests.
- Add `tools/tests/test_rc255_standalone_typescript_ci.py` to the pre-npm quality gate: verify CI includes the guard, assert the compiler configuration and ESM import, run the exact standalone strict TypeScript compilation, and run real native Node TS tests of Arial and slide masters.
- Preserve all RC254 production typography and rendering corrections, and retain historical SHA-256 inventories unchanged.

## Local verification (run from project root)

```bash
python3 -m unittest -q tools.tests.test_rc75_typescript_ci tools.tests.test_rc255_standalone_typescript_ci
node --experimental-strip-types --test apps/web/test/rc195-master-typography.test.ts apps/web/test/rc254-all-widget-schema-fonts.test.ts
npm run build -w @quorivio/web
python3 tools/verify_rc_cycle255_inventory.py
```

A new GitHub full CI must pass after commit before release status can be upgraded. No Docker push, tag, or release performed.
