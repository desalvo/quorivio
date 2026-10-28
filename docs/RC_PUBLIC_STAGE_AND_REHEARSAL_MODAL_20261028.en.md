# Public participant stage and modal focus hardening


## RC cycle — 28 Oct 2026: live participant slide parity and modal resilience

**Baseline:** 740-file cumulative ZIP (singleton/mobile Chromium hotfix). **Version:** `0.1.0-dev`, EUPL-1.2 unchanged. **Observed GitHub main:** `8899c24155473ab8ff88cfa1ba767aa949be1ded`; last user-confirmed commit: `1a0bea5918098af52fdf9958b8e8e664d09c11d5`. Last GitHub full run `40689633215`: FAILED at Chromium editor UI acceptance before PostgreSQL steps; this ZIP's singleton hotfix is still unverified on GitHub.

**Implemented:** real participant 16:9 slide and persisted x/y/width/height/rotation parity; authorized slide background and picture crop; inline text marks in the live text/post-it widgets; a selectable linear reading mode defaulting on phone-size screens, with slide horizontal scroll when fidelity mode is manually selected. Rehearsal modal now isolates dynamically inserted sibling portals from assistive technology and restores their previous `inert`/`aria-hidden` state, with improved Tab navigation. Added Chromium regression runners and wired them before real editor acceptance in opt-in CI.

**Local verification:** `npm run build` PASS (API TypeScript, frontend TypeScript, Vite). `node --test`: 474/474 API PASS, 58/58 frontend PASS. Full Python suite: 965/965 PASS; RC-focused Python suite 383/383 PASS. Chromium: built React dashboard/editor singleton PASS at 1440 and 390px; actual rehearsal TS focus/dynamic portals PASS both; public participant CSS fixture 16:9/saved rotation/reading-mode 44px target PASS both. The failed full-Python first attempt was rerun successfully; results are not inferred from previous cycles.

**RC:** 32 weighted gates (15 accepted, 17 partial), score **67.0% → 67.0% (+0.0 percentage points)**. Local evidence did NOT promote a gate. Strict release candidate remains blocked.

**Still required:** a fresh maintainer-triggered full GitHub run `browser_test=true`, `publish_image=false` after commit; authenticated React participant and editor against PostgreSQL 18, independent side-by-side visual and screenshot comparisons of real sessions, Firefox/WebKit, physical Android/iOS touch, screen readers and AGID/WCAG independent sign-off; Kubernetes/Helm multi-replica/failover operational tests. No commit, push, tag or Docker publication was performed.

**Evidence/report:** `docs/validation/RC_PUBLIC_STAGE_REHEARSAL_PORTALS_LOCAL_20261028.json`; the RC gate matrix documents pending work without changing accepted gate statuses.
