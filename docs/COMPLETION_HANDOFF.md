# Quorivio 0.1.0-dev — RC282 — Participant/rehearsal answer-option ordering CI hotfix

**RC282:** Full CI [42619153721](https://github.com/desalvo/quorivio/actions/runs/42619153721) passed prior lockfile and pre-install stages but stopped in the full Node web suite: the historical editor-cycle38 test expected a static `widget-answer-option` class and failed against RC274 inline truth-feedback classes. The real JSX retains the input before the caption for both participant and rehearsal. Updated that source contract to assert the two graded JSX variants separately, verify input-first markup, caption and verdict icon; added negative mutation tests for reversed order, missing graded class and missing icon. Added the complete interaction suite as an early CI gate before npm and promoted RC281 to immutable historical inventory with RC282 current. Application runtime unchanged. Rebuilt bilingual PDF manuals with RC282 metadata; authentic Chromium screenshots and full CI are still pending. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag.

# Quorivio 0.1.0-dev — RC281 — CI negative-assertion source scan hotfix

**RC281:** The RC280 full CI [42612111250](https://github.com/desalvo/quorivio/actions/runs/42612111250) failed in the RC274 pre-install gate: a historical raw-text test incorrectly flagged a *negative assertion* in the new RC280 lockfile test as a prohibited npm install command. Expressed the same forbidden command with split source literals, keeping the regression assertion fully functional and leaving the RC274 fail-closed scanner unchanged. Added a dedicated early compatibility regression and promoted immutable RC280 to historical inventory with a new RC281 manifest. No application runtime changes. Bilingual manuals rebuilt for RC281; screenshot acquisition and complete GitHub CI remain pending. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag.

# Quorivio 0.1.0-dev — RC280 — Deterministic LDAP dependency lockfile fix

**RC280:** Fix committed RC279 full CI [42605580476](https://github.com/desalvo/quorivio/actions/runs/42605580476), which passed earlier preflight checks but failed npm ci because the LDAP dependencies were missing from `package-lock.json`. The lock now pins `ldapts@9.2.0` and `strict-event-emitter-types@2.0.0` with verified SHA-512 integrity, plus the API workspace dependency. Add fail-closed pre-install tests, keep historical inventories immutable, and regenerate all six bilingual manuals with RC280 build labels. Real Chromium screenshots and full GitHub CI are not yet verified. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE280_NPM_LOCK_SYNC.en.md`.

# Quorivio 0.1.0-dev — RC279 — OAuth HA manual contracts and CI repair

**RC279:** Fix GitHub Actions run [42599356568](https://github.com/desalvo/quorivio/actions/runs/42599356568): RC126/RC59 expected OAuth PostgreSQL one-use state text in an obsolete manual generator, even though the manuals are now sourced from bilingual Markdown. The test now checks published manual sources and the real PostgreSQL single-use OIDC/social callbacks. Also reconcile RC154 load-test/Gravatar manual checks with the Markdown sources, add authorized 500-participant CLI workflow and safety restrictions, update six bilingual PDFs, and retain RC278 as immutable historical inventory. No application runtime changes. The real-screenshot CI step was not reached and remains unverified; **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE279_MANUAL_CI_OAUTH_HA.en.md`.

# Quorivio 0.1.0-dev — RC278 — Evidence-backed live screenshot manuals

**RC278:** six IT/EN manuals with centrally sourced app/build, logo, creator/email, EUPL-1.2, indicative supported platforms/hardware; additional scaling and disaster recovery runbooks. Actual running-app Chromium/PostgreSQL screenshots embed in the PDFs only with verified source commit and SHA-256. GitHub CI publishes a separate screenshot/PDF artifact without mutating committed manuals. No real screenshots have been captured locally (npm registry unavailable); full CI screenshot acceptance remains pending. **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE278_LIVE_MANUALS.en.md`.

# Quorivio 0.1.0-dev — RC277 — Expanded bilingual operational manuals

**RC277:** Six fully rewritten guides, 164 total PDF pages, editable Markdown sources, 21 widget types, administrator Helm/Kubernetes/backup/LDAP/audit procedures, clearly labelled illustrative figures, and identical published PDF checks. Live screenshots and independent review remain pending. **85.25%** (43 gate accettati/17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; No commit/push/tag. `docs/RC_CYCLE277_EXPANDED_MANUALS.en.md`.

# Quorivio 0.1.0-dev — RC276 — Live linked results R contract

**RC276:** GitHub CI [42565597725](https://github.com/desalvo/quorivio/actions/runs/42565597725) passed RC275 but failed the RC191 cross-page test, which incorrectly required the removed live-only `showCorrectLive` state. The common `LinkedResultChart` already owns the R toggle and `hasKey` protection, shared by the presenter, editor and previews. Updated RC191 to assert shared state and source-page widget routing; five new negative mutation/functional contract tests and an early RC276 gate. No runtime changes. Immutable RC275 inventory is historical; RC276 is current. **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`; full CI/browser acceptance pending, no commit/push/tag. `docs/RC_CYCLE276_LIVE_RESULTS_TRUTH_CI.en.md`.

# Quorivio 0.1.0-dev — RC275 — Linked source truth toggle CI fix

**RC275:** corrected RC274 GitHub CI [42551661125](https://github.com/desalvo/quorivio/actions/runs/42551661125): outdated RC192 and RC196 checks expected `result={widget}` despite deliberate `result={viewWidget}` to apply answer truth R. New RC275 source-renderer regression ensures toggle and source-question synchronization, with no runtime changes. Historical RC274 retained; RC275 source inventory active. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; full CI/browser acceptance pending. No assistant commit/push/tag. `docs/RC_CYCLE275_LINKED_RESULTS_UI_CONTRACT.en.md`. 

# Quorivio 0.1.0-dev — RC274 — Answer grading and deterministic CI

**RC274:** fix late RC273 CI [42548617989](https://github.com/desalvo/quorivio/actions/runs/42548617989) from npm install lockfile mutation and privacy-test scope mismatch, switch to npm ci with historical preflight updates. Inline verified correct/incorrect answers after submission, R toggle on linked results in editor/presenter/previews, answers configured from properties or Format Widget → Content. RC273 now historic; RC274 active. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; full CI pending. No assistant commit/push/tag. `docs/RC_CYCLE274_TRUTH_FEEDBACK_CI_FIX.en.md`.

# Quorivio 0.1.0-dev — RC273 — Backup and audit TypeScript fix

**RC273:** fix four API TypeScript errors in the RC272 full CI [42547239843](https://github.com/desalvo/quorivio/actions/runs/42547239843): convert S3 payloads to web-compatible `Uint8Array` for `fetch`, preserve streaming Node WebDAV uploads and `duplex: 'half'` with a narrowly scoped Node/DOM boundary cast, and safely type and validate Express route parameter `id` for audit logging. RC272 becomes an immutable historical inventory, RC273 is current. Local RC270 transport tests and isolated API module typecheck passed; full API build and GitHub CI still need validation. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE273_API_TYPECHECK_HOTFIX.en.md`.

# Quorivio 0.1.0-dev — RC272 — CI RC241 result-row contract compatibility

**RC272:** RC241 test now accepts the direct or composed row style expression used by RC270 pie text color mapping; negative regressions ensure row formatting still cannot disappear. Full CI [42537006971](https://github.com/desalvo/quorivio/actions/runs/42537006971) stopped at that historic lexical guard, not at an observed runtime defect. RC271 inventory stays historical; RC272 is current. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. New full CI pending; no assistant commit/push/tag. `docs/RC_CYCLE272_UI_CONTRACT_CI_HOTFIX.en.md`.

# Quorivio 0.1.0-dev — RC271 — Current inventory and CI preflight hotfix

**RC271:** repair RC270 full CI [42535872914](https://github.com/desalvo/quorivio/actions/runs/42535872914), blocked by RC269 inventory still active when RC270 headers were published. Promote RC269 inventory to immutable historical, create RC271 source/ZIP SHA-256 manifest and current verifier; add backup/audit and wizard RC270 regressions to CI. No runtime behavior changed. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; new GitHub CI and real restore remain pending; no assistant commit/push/tag. `docs/RC_CYCLE271_INVENTORY_CI_PROMOTION.en.md`.

# Quorivio 0.1.0-dev — RC270 — Full backup, LDAP approval, audit and result charts

**RC270:** cumulative PostgreSQL and persistent-asset full backup with admin download, periodic POSIX/NFS/S3/WebDAV destinations, Helm/wizard storage wiring, pending LDAP self-registration and admin directory lookup, operational audit and result-chart formatting. CI gate broke on unpromoted inventory; see RC271. **85.25%** baseline unchanged; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

# Quorivio 0.1.0-dev — RC269 — LDAP, ownership and housekeeping handoff

**RC269:** RC268 GitHub full CI [42525045176](https://github.com/desalvo/quorivio/actions/runs/42525045176) and manual image publish [42527052932](https://github.com/desalvo/quorivio/actions/runs/42527052932) green. Add automatic presenter reauthentication redirect, 12-hour fail-closed cleanup, transactional primary ownership transfer with audit, LDAP/LDAPS TLS service/user binds and explicit account linking, RWO-safe wizard, contextual sidebar right-click/long-press and readable smartphone answer text. LDAP directory end-to-end and cluster still to be validated. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; RC269 full CI pending; no commit/push/tag. `docs/RC_CYCLE269_LDAP_OWNERSHIP_HOUSEKEEPING.en.md`.

# Quorivio 0.1.0-dev — RC268 — Preview, ordering and mobile visual parity handoff

**RC268:** RC267 full CI [42516844646](https://github.com/desalvo/quorivio/actions/runs/42516844646) and multiarch Docker publication [42518673212](https://github.com/desalvo/quorivio/actions/runs/42518673212) green. New fullscreen preview geometry/navigation, empty thumbnail sidebar contextual menu and before/between/after drop insertion, compact phone QR/results layout, and automatic page-scoped 16:9 for raster PDF/static slides shown to participant phones. Preserve explicit layout selection and accessible reading; no Kubernetes/database/converter changes. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; GitHub CI RC268 and authenticated cluster test pending; no commit/push/tag. `docs/RC_CYCLE268_PREVIEW_SIDEBAR_PHONE_FIDELITY.en.md`.

# Quorivio 0.1.0-dev — RC267 — Node CI shell invocation hotfix

**RC267:** Fix committed RC266 full CI [42511888604](https://github.com/desalvo/quorivio/actions/runs/42511888604): a missing shell line continuation executed a `.test.ts` file directly (`Permission denied`, exit 126). Restore one Node command for all three tests; a new dependency-free preflight executes the actual early CI shell block. Editor runtime and Kubernetes wizard are unchanged. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; GitHub RC267 full CI pending; no commit/push/tag. `docs/RC_CYCLE267_CI_NODE_RUNNER_CONTINUATION.en.md`.

# Quorivio 0.1.0-dev — RC266 — Participant canvas legacy CI hotfix

**RC266:** Fix historical RC173 test and add pre-RC227 CI guard for the RC265 participant stage background spread; preserve accessible reading and imported-image suppression. The committed RC265 full CI [42506410487](https://github.com/desalvo/quorivio/actions/runs/42506410487) failed on this obsolete assertion. No runtime, Kubernetes or Docker changes. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; RC266 full CI pending; no commit/push/tag. `docs/RC_CYCLE266_PARTICIPANT_BACKGROUND_CI_FIX.en.md`. **Additional RC266 runtime fix:** allow floating format, page and widget-properties panels to dock at viewport edges with a reachable title strip, and resize them with an accessible pointer/keyboard corner grip. Real Chromium desktop/mobile CSS regression and early CI preflight added. Kubernetes/database/converter unchanged.

# Quorivio 0.1.0-dev — RC265 — Full-canvas raster PDF/PPTX import

**RC265:** Imported PDF/PPTX image pages now support `cover`, `contain` and forced `fill`, opt-out inherited scheme/title/footer/page number suppression, genuine private page backgrounds, and real page thumbnails. RC264 full CI green [42498365156](https://github.com/desalvo/quorivio/actions/runs/42498365156), manual app/converter Docker publication succeeded; full RC265 CI pending. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE265_PDF_FULL_BLEED_IMPORT.en.md`.

# Quorivio 0.1.0-dev — RC264 — Pillow-independent PDF converter preflight

**RC264:** Committed RC263 full CI [42496843522](https://github.com/desalvo/quorivio/actions/runs/42496843522) stopped at pre-npm converter regression: mocked Poppler, but the synthetic PDF mount tests still invoked Pillow on an intentionally dependency-free runner. RC264 checks exact deterministic fixture PNG bytes in the mount tests without relying on Pillow, while production retains mandatory `Image.verify()` and `Image.load()`; absent Pillow now fails explicitly instead of `UnboundLocalError`. Added early RC264 gate, retained CVE/Trivy security checks. No wizard RC263 or Kubernetes mutation. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; GitHub full CI RC264 pending, no commit/push/tag. `docs/RC_CYCLE264_PILLOW_CI_FIX.en.md`.

**RC263:** Fixed the RC261 CI fixture to simulate Poppler availability while mocking subprocess conversion, independent of host packages. Reconciled Kubernetes API-defaulted `terminationMessagePath`/`terminationMessagePolicy` without weakening strict image, command, secrets, volumes, or security drift validation. Existing probe deployments can use `--sync-disk-monitor` without another PostgreSQL restart. Self-updating standalone wizard RC263. Local tests; GitHub full CI pending. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE263_CI_KUBERNETES_DEFAULTS.en.md`.

**RC262:** Added *Server configuration → Disk space and alerts* for asset PVC, conversion scratch and PostgreSQL data volume. App metrics use `statfs`; the read-only `db-disk-probe` monitors the database PVC with actual `df` data. `pg_database_size` is informational, never used for disk-alert percentages. SMTP notifications to approved platform admins trigger at 90% and rearm at ≤85%, with DB-locked cross-replica deduplication and stale samples shown as unavailable. Standalone Kubernetes wizard RC262: new generated internal DB workloads include the probe; existing deployments receive an explicit plan/apply workflow (PostgreSQL restart requires operator acknowledgment), persistent Kustomize overlay and private backups. Focused tests, builds and SHA-256 evidence; GitHub full CI pending. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE262_DISK_CAPACITY_MONITORING.en.md`.

---

# Quorivio 0.1.0-dev — RC261 — Cross-volume PDF/PPTX converter recovery

**RC261:** Fixed Kubernetes `EXDEV errno=18` on flattened PDF/PPTX import by staging and atomically publishing within one `/conversions` filesystem. Trivy remains fail-closed; converter Dockerfile requires Debian fixed `zlib1g deb13u1` for both HIGH CVEs. API maps worker conversion errors safely. RC261 standalone wizard can synchronize image-only deployed converter refreshes into `k8s-generated`, rejecting all unrelated drift. Full RC261 CI pending. **85.25%**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE261_CONVERTER_CROSS_MOUNT_AND_ZLIB_CI.en.md`.

# Quorivio 0.1.0-dev — RC260 — Kubernetes `generated` synchronization

**RC260:** Standalone self-updating wizard adds `--generated-dir` and `--sync-generated`: binds converter rollout plans to original Kustomize manifest hashes, synchronizes private token and strategic merge overlay only after successful rollout, supports local-only reconciliation of already-deployed converter, preserves the overlay and token during future regeneration, and leaves DB/PVC/Ingress/Service unchanged. Historical RC259 receipt retained; current inventory RC260. Full CI pending; **85.25%** (43 accepted/17 partial). No commit, push or tag. `docs/RC_CYCLE260_KUBERNETES_GENERATED_RECONCILIATION.en.md`.

# Quorivio 0.1.0-dev — RC259 — Self-updating standalone wizard and PPTX CI guard

**RC259:** RC258 full CI [42480854048](https://github.com/desalvo/quorivio/actions/runs/42480854048), commit `64744e1bb3aec55ba7de4482ed9a05640b4a5376`, failed only one of 2,325 Python tests: a stale text assertion for PPTX-imported projection font. Updated to verify `explicitWidgetFontFamily`, preserving the invalid-font guard. The standalone Kubernetes wizard now updates itself from official `desalvo/quorivio` over HTTPS at startup, exposes `--version`, atomically replaces its own file and re-execs original CLI arguments. Explicit `--no-self-update` for offline operation; RC258 embedded features and rollout guards unchanged. Historical RC258 inventory immutable; new RC259 inventory. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; GitHub full CI pending; no assistant commit/push/tag. `docs/RC_CYCLE259_WIZARD_GITHUB_AUTOUPDATE_AND_PPTX_CI.en.md`.

# Quorivio 0.1.0-dev — RC258 — Standalone Kubernetes wizard and safe rollout

**RC258:** Built on cumulative RC257. Fixed the overly strict `maxUnavailable: 25%` rejection for Kubernetes Deployments with 1–3 replicas (percentage rounded down); actual availability loss and Recreate remain blocked. A single copy of `k8s_wizard.py` now includes its inspected converter upgrade and cluster inspection helpers: new-install manifests, read-only live inventory, token provisioning, sidecar plan and guarded apply require no other Quorivio modules. No database Secret/PVC/Ingress replacement. Standalone fake-cluster integration tests, early CI gate, new RC258 inventory and immutable RC257 historical inventory. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full CI RC258 pending; no commit/push/tag. `docs/RC_CYCLE258_STANDALONE_K8S_WIZARD.en.md`.

# Quorivio 0.1.0-dev — RC257 — RC193 font tests and existing Kubernetes converter wizard

**RC257:** RC256 [full CI 42479602496](https://github.com/desalvo/quorivio/actions/runs/42479602496) on commit `9023bff41adf05863b7c2c508f836b012c3e2416` failed in RC193 requiring the obsolete raw `style?.fontFamily||'Arial'` expression. Migrated the historical check to `safeWidgetFontFamily(...)` for answers and submit, retaining editor focus tests. Added an early RC257 preflight scanning historical font assertions and running Node runtime font coverage. No production-code edits. Added an operator guide for the existing-cluster PDF/PPTX sidecar wizard, with token, reviewed plan, server dry-run and explicit patch. Historical RC256 inventory unchanged. **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. GitHub full CI pending; no assistant commit/push/tag. `docs/RC_CYCLE257_K8S_CONVERTER_RC193_CI.en.md`.

# Quorivio 0.1.0-dev — RC256 — Historical Arial CI compatibility

**RC256:** RC255 full CI [https://github.com/desalvo/quorivio/actions/runs/42478213918](https://github.com/desalvo/quorivio/actions/runs/42478213918), commit `22ced8d3f9bd09e228fa63e1034d7f57837867de`, failed in the RC242 historical check that required obsolete `fontFamily:style?.fontFamily||'Arial'`. Updated five historical Python test suites (RC145, RC161, RC194, RC195 and RC242), including footer font and negative mutations, to require validated `safeWidgetFontFamily(...)` instead. Added an early RC256 CI gate also exercising actual RC254 Node font behavior; production RC254 protection unchanged. Historical RC255 inventory immutable; new RC256 receipt. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE256_HISTORICAL_ARIAL_CI.en.md`.

# Quorivio 0.1.0-dev — RC255 — Strict TypeScript pre-npm compatibility gate

**RC255 handoff:** The RC254 full CI [42476782314](https://github.com/desalvo/quorivio/actions/runs/42476782314), commit `45bf2bea9ed09c82684012ffcaa0925dbaf48dd2`, stopped in RC197's historical RC75 standalone TypeScript test with `TS5097` at `apps/web/src/slide-master.ts:2`. The test invokes strict `tsc --noEmit --moduleResolution bundler` without `--allowImportingTsExtensions`, although native Node TS module execution requires `.ts` imports and the Vite app accepts them. Keep the production import and RC254 Arial safety intact. RC255 updates the RC75 test flags, adds a pre-npm RC255 contract running standalone strict compilation and native Node ESM master/font regressions, preserves RC254 receipt as historical, and creates a complete RC255 inventory. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE255_STANDALONE_TS_ESM_CI.en.md`.

**RC254:** Full CI RC253 [42432817088](https://github.com/desalvo/quorivio/actions/runs/42432817088), commit `93d029100ef09af4e3fe88119e83db38abc62960`, passed all 14 executed jobs (3 conditional skips). Audited 20 widget kinds, title/footer and independent answer text in both editors: shared `RichWidgetText` already omits missing CSS properties, but multiple view renderers still consumed raw font-family values. Introduced one validated font allowlist for base text, answers/submit, inline marks, results and footer page number. Prevents literal `undefined`/`null` families even in imported or malformed historical layouts, preserving every explicit supported font. Added Node tests and real compiled Chromium checks across 14 text-bearing widgets in regular and slide-master editors on 390px and 1440px screens. Historical RC253 receipt unchanged, new RC254 cumulative inventory. **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag. See `docs/RC_CYCLE254_ALL_WIDGET_SCHEMA_ARIAL.en.md`.

---

# Quorivio 0.1.0-dev — RC253 — Deterministic Arial Chromium browser gate

**RC253:** Committed RC252 [full CI 42431610890](https://github.com/desalvo/quorivio/actions/runs/42431610890) (`6af6db7e6ad812e20548fba8ce9c0451c26df2fe`) failed only in the compiled React Chromium browser gate: its offline page tried to connect to synthetic `ws://live/` and emitted `net::ERR_NAME_NOT_RESOLVED`. Confined the synthetic WebSocket to an in-memory test-only open/close fixture, explicitly refusing unexpected hosts while retaining strict console/React error assertions and actual title/answer Arial glyph checks. Production code unchanged. TypeScript/Vite and both mobile/desktop Chromium viewports passed locally; GitHub full CI RC253 pending. RC252 historical checksum inventory untouched; fresh cumulative RC253 SHA-256 inventory. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE253_OFFLINE_CHROMIUM_SOCKET.en.md`.

---

# Quorivio 0.1.0-dev — RC252 — React editor Arial DOM font regression

**RC252:** Fix the recurring initial Arial face defect at its source: the React rich-text DOM renderer wrote `font-family: undefined` to every unmarked span, which the browser treats as a literal font family and which overrides correct parent Arial styling on new titles and answer choices. The DOM CSS serializer now omits absent properties while preserving independently authored Verdana/Tahoma base faces, Georgia/Trebuchet MS per-character marks and font sizes. Added Node tests and production-compiled React Chromium at 390×844 and 1440×940 covering a real question-widget insertion, title/answer computed fonts, marked overrides and compact studio zoom. Maintainer-committed RC251 passed full CI [42416170735](https://github.com/desalvo/quorivio/actions/runs/42416170735); main multiarch image [42417768823](https://github.com/desalvo/quorivio/actions/runs/42417768823) and converter [42417918195](https://github.com/desalvo/quorivio/actions/runs/42417918195) were published. RC251 historical SHA inventory remains byte-identical; RC252 awaits full CI after maintainer commit. **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE252_WIDGET_ARIAL_DOM.en.md`.

---

# Quorivio 0.1.0-dev — RC251 — Public native-scale touch targets and CI recovery

**RC251:** Full GitHub CI [42412981696](https://github.com/desalvo/quorivio/actions/runs/42412981696) for committed RC250 `63e877449bb4821be14292f3f4cf8cc8770922a0` failed in real participant Chromium: root-level 80% zoom reduced authored 44px touch choices to 35.2px physically. Preserve compact studio/editor/master zoom but use native 100% document scale for public `/join/*` and `/screen/*`, hiding the studio zoom controller there. Added Node route tests, Python negative guards and Chromium physical measurements; genuine React/PostgreSQL integration and historical gates remain mandatory. RC250 inventory untouched; full CI rerun is needed. **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE251_PUBLIC_LIVE_TOUCH_ZOOM.en.md`.

---

# Quorivio 0.1.0-dev — RC250 — Full CI chromium thumbnail menu handoff

**RC250:** GitHub full CI [42410387603](https://github.com/desalvo/quorivio/actions/runs/42410387603), committed RC249 `cf0a1e45048ad49e6d320eddf610f205e4d4bc53`, passed early guards and independent Chromium CSS checks but failed `ci_browser_editor.py:266` when an expanded thumbnail menu overlapped its own toggle under the 80% root CSS zoom. `getBoundingClientRect()` gives zoomed *visual* coordinates, but fixed-position body portals apply the CSS zoom again. Corrected menu layout coordinates by dividing the final clamped result by the computed document zoom on open, scroll, resize, and root zoom changes; no forced clicks and original compiled React UI acceptance remains mandatory. Added negative Node reproducer, pre-npm contract and 8 real Chromium tests with expanded menu at zoom 64%, 80%, 100%, 120%. RC249 historical; full RC250 GitHub CI pending. **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE250_THUMBNAIL_CSS_ZOOM.en.md`.

---

# Quorivio 0.1.0-dev — RC249 — Thumbnail menu trigger-safe anchoring

**RC249:** GitHub full CI [42405687692](https://github.com/desalvo/quorivio/actions/runs/42405687692) for committed RC248 `9027af34f0d8182d12bda366a89e239286b63a41` failed the real Chromium editor because the expanded portaled thumbnail menu intercepted its own toggle. Menu now anchors beside the actual trigger rectangle and repositions after scroll/resize/zoom, preserving keyboard/escape and accessible scroll. Added pre-npm negative guard, Node geometry and real Chromium hit-target acceptance with no forced clicks. RC248 immutable, full RC249 CI pending. **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE249_THUMBNAIL_MENU_ANCHOR.en.md`.

---

# Quorivio 0.1.0-dev — RC248 — Editor stage containment handoff

**RC248:** Continue from maintainer-committed RC247 `6a7f8e5eae6a972a218fca4b45348067ef58307d`. GitHub full CI [42401914583](https://github.com/desalvo/quorivio/actions/runs/42401914583) failed the historical RC178 Chromium layout with a 15px canvas overflow at 1440×900. Limit desktop canvas dimensions using actual editor-stage CSS container height (`100cqh`), with 29px horizontal and 28px vertical rulers and a safety margin. Keep UI zoom 80%-based compact and large 16:9 canvas, unchanged mobile scrolling. New fail-closed early static contract and 15 Chromium real-viewport/zoom scenarios, retain RC178. Run full GitHub CI after user commit. **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE248_EDITOR_STAGE_FIT.en.md`.

---

# Quorivio 0.1.0-dev — RC247 — Editor and converter handoff

**RC247:** Resume from RC246 cumulative. Restore editor/preview result font parity via stage-relative `cqw`; apply Whole widget fonts to title, answers, nested subquestions, rich marks and buttons; enforce Arial defaults without overriding authored fonts. Browser-like compact UI zoom displays 100% for former 80%, fills physical fullscreen overlays, expands 16:9 canvas and removes empty dashboard side gutters. Converter publisher remains manually authorized, tags `main` as `latest`, Git tags verbatim. Historical RC246 inventory unchanged. Run complete full CI on maintainer commit, verify real editors and operator acceptance. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE247_EDITOR_FONT_ZOOM_CONVERTER.en.md`.

---

# Quorivio 0.1.0-dev — RC246 — Existing Kubernetes worker handoff

**RC246:** RC245 source commit c108694705d2bd0d8d8444f7840a944b5913e25d passed full CI GitHub 42382296263 (11/11 mandatory jobs, 14 successful). The primary app image was published with amd64/arm64 in workflow 42385404670 under desalvo/quorivio:sha-c108694705d2 and latest. RC246 extends the live Kubernetes wizard with read-only Deployment discovery, a non-destructive scoped JSON Patch plan for a sidecar PDF/PPTX worker, an explicitly initiated token addition to the existing Secret, separate deliberate apply/rollout with context/UID/resourceVersion validation, and a separate manual-only converter image publisher. No database/PVC/Ingress/Service recreation, credential resets or original Kustomize overwrite. The isolated converter Docker image is NOT included in the prior app publication and must be published explicitly; no real cluster upgrade performed. RC246 full CI and operator sign-off pending. **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE246_EXISTING_K8S_CONVERTER_UPGRADE.en.md`.

---

# Quorivio 0.1.0-dev — RC245 — Compact phone question CI handoff

**RC245 handoff:** Starting from user-committed RC244 `9af6cb4c99f8347c386b59f58ec1eced903928d3`, full CI run `42380437684` stopped at `tools/ci_browser_participant.py` due to the stale RC207 `questionHeight>=278-1` check. RC241 compacted the automatic mobile question from 278px to 238px for two short options. The corrected real React/PostgreSQL browser requires both authored responses, actual touch heights >=44px, text >=18px, compact stage budget and no private presenter widgets. RC217 mutation guard reconciled; RC245 early Python/Node tests and isolated Chromium fixture added. No application UI or safety flags changed. Preserve RC244 receipt, promote RC245 current; rerun full GitHub CI. 85.25% (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE245_COMPACT_PHONE_QUESTION.en.md`.

---

# Quorivio 0.1.0-dev — RC244 — Editor Arial baseline CI reconciliation

**RC244 handoff:** Start from user-committed RC243 `a0e7dbcf22b6f73ce8a04caa028ef4745825698e`. Full CI [42377514266](https://github.com/desalvo/quorivio/actions/runs/42377514266) passed strict React TypeScript, then RC224 Chromium found inherited DM Sans on the slide-master widget root. Replace root `font-family:inherit` with an Arial default on both editors, preserving custom inline fonts; make RC242 browser fixture independently test default typography without inline Arial. Add RC244 pre-npm negative mutation guard, retain real browser tests and all historical inventories. RC243 historical, RC244 current; full CI after commit pending. **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. `docs/RC_CYCLE244_EDITOR_ARIAL_BASELINE.en.md`.

---

# Quorivio 0.1.0-dev — RC243 — React global zoom effect cleanup / strict TypeScript

**RC243:** Full GitHub CI [42376234500](https://github.com/desalvo/quorivio/actions/runs/42376234500) for RC242 commit `f2899cc76320667a442b504d9e89f38c6f1611ff` stopped at the strict React TypeScript check because the global zoom `useEffect` destructor returned the string from `CSSStyleDeclaration.removeProperty`. Replace the expression-bodied cleanup with a void-returning block while preserving global zoom behavior, persistence, and accessibility. New fail-closed RC243 negative guard runs before npm, full TypeScript remains mandatory. RC242 historical, RC243 current; RC243 full GitHub CI pending. Certified **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. See `docs/RC_CYCLE243_ZOOM_EFFECT_TYPECHECK.en.md`.

---

# Quorivio 0.1.0-dev — RC242 — Arial widget defaults, compact slide-master ribbon and global zoom

**RC242:** Starting from RC241, all text descendants on the page and slide-master canvases inherit Arial by default, preserving authored custom typefaces. The scheme Save and status action is kept in one sticky compact row with reduced buttons, while other commands can scroll horizontally on narrow devices. A persistent global zoom controller (70–150%, 10% steps, reset to 100%) is displayed across login, public pages, dashboard, presenter and both editors, including portaled windows. Added early CI tests and real Chromium fixture at 390/760/1440px. RC241 becomes historical, RC242 is current. GitHub full CI pending; certified **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE242_WIDGET_ARIAL_ZOOM.en.md`.

---

# Quorivio 0.1.0-dev — RC241 — Result typography, phone editor parity and numeric format controls

**RC241:** Building on the RC240 cumulative package, implemented independently persisted result-row typeface/size/colour, uniform final-word typography, more compact automatic phone question height and identical 390px insets in edit/rehearsal, a common 1280×720 presenter preview stage, and editor cut/copy/paste/info/undo/redo toolbar actions. All numeric inputs in **Formato widget**, including independent result rows, retain a keyboard-editable draft until Enter/blur and expose explicit increment/decrement buttons. Added tests and fail-closed early CI gate. RC240 immutable historical. The verified full GitHub RC239 campaign is the last acknowledged green run; RC241 integrated Chromium/TypeScript checks still pending. Certified **85.25%** (43 accepted/17 partial); independent operator sign-offs remain outstanding. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. See `docs/RC_CYCLE241_EDITOR_RESULT_FORMAT_PHONE.en.md`.

---

# Quorivio 0.1.0-dev — RC240 — Full-green acceptance and protected external evidence handoff

**RC240 handoff:** Work from user-committed RC239 `0594b72806a7b6bf27de07a5fb2856747c8fd68d`; confirmed full CI [42284582481](https://github.com/desalvo/quorivio/actions/runs/42284582481) succeeded all 11 RC campaign requirements (14 job successes, 3 publication skips). Current ledger now links its GitHub receipt, retaining Oct legacy CI in a dedicated historical field; old SHA manifests unchanged. Operator-evidence attachment intake and verification now pin read-only regular-file descriptors, reject swaps/edits, verify destination bytes and roll back temp manifests. Mandatory RC240 tests are early in CI. Operational/legal reviews still missing for **17 partial gates**, certified **85.25%** (43 accepted); do not claim an official RC. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. Next: full CI RC240, then independent operator evidence using the existing private `tools/rc_external_evidence.py` CLI. Details in `docs/RC_CYCLE240_FULL_GREEN_EVIDENCE.en.md`.

---

# Quorivio 0.1.0-dev — RC239 — Explicit contextual widget format handoff

**RC239:** Based on user-committed RC238 `e1f7d2f234a712a112f98b23e3774905825a28d8`, full CI [42274460486](https://github.com/desalvo/quorivio/actions/runs/42274460486). Real editor/PostgreSQL persistence, conflict handling and JSON export passed, then RC193 timed out while looking for the formatter scope in the properties inspector. Keep RC223's correct separate format dialog and use **Formato widget** from the question context menu after closing properties; scope subsequent font actions to the visible toolbar and preserve all typing/focus assertions. Add mandatory pre-npm RC239 negative regressions; retain the genuine Chromium/PostgreSQL gate. RC238 immutable historical inventory, RC239 current; runtime untouched. Full GitHub CI still pending, certified **85.25%** (43 accepted, 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Do not commit, push or tag without the user's request. `docs/RC_CYCLE239_CONTEXTUAL_FORMAT_CHROMIUM.en.md`.

---

# Quorivio 0.1.0-dev — RC238 — Participant auto-phone / Chromium handoff

**RC238:** From GitHub-committed RC237 `4c4b7ee0451e0a20abb791da2a0ea585eddc8f63` and failed full CI [42269302109](https://github.com/desalvo/quorivio/actions/runs/42269302109). The production quality gate reached real participant Chromium/PostgreSQL and failed a stale 16:9 default assertion on a 390px touch mobile browser. Preserve correct RC227 auto-phone default and explicit override: assert automatic phone view on join and reload, explicitly restore 16:9 before comparing cross-device faithful geometry, and retain later phone/accessible-mode checks. Historical RC176 mode guard now scopes ordering to explicit phone switch. New mandatory RC238 fail-closed pre-npm tests. App untouched; RC237 historical integrity unchanged; RC238 current. Full GitHub CI not yet certified. Certified **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE238_PARTICIPANT_PHONE_CHROMIUM.en.md`.

---
# Quorivio 0.1.0-dev — RC237 — Rename-scope CI handoff

**RC237:** Continue from user-committed RC236 `910c60216d9e18c7602a47070a5d822588f1194f`; GitHub full CI [42256926397](https://github.com/desalvo/quorivio/actions/runs/42256926397) failed because a negative-mutation test for the RC218 thumbnail rename locator also matched the suffix of RC236 `export_actions`. Replaced the substring check with a line-anchored exact rename assignment and added mandatory RC237 negative tests. Runtime and browser behavior unchanged. Historical RC236 integrity retained; RC237 current. GitHub CI still pending. **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE237_RENAME_ACTION_SCOPE.en.md`.

---
# Quorivio 0.1.0-dev — RC236 — Browser page-action disclosure reconciliation

**RC236:** Full CI [42252842551](https://github.com/desalvo/quorivio/actions/runs/42252842551), commit `98a3a39c15aa83deaab722f1ed872f0f7ff9883e`, failed in the authenticated Chromium editor because it queried `Nuova pagina prima` in a closed native `<details>` group. Updated the browser's create/import/export disclosure interactions and a second export after reload, plus PostgreSQL Chromium export. The application source is unchanged. Added mandatory pre-npm RC236 mutation tests; RC224 native Chromium menu fixture passes all four viewport cases. RC235 historical receipts unchanged. GitHub integrated CI pending; **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE236_THUMBNAIL_MENU_DISCLOSURES.en.md`.

---
# Quorivio 0.1.0-dev — RC235 — Cross-cycle responsive browser compatibility

**RC235:** Full CI [42249042835](https://github.com/desalvo/quorivio/actions/runs/42249042835), commit `774c8431972fdff1a73ad780352c1cf6550e17ad`, passes the former RC233 palette-overflow test but fails the historical RC226 Chromium assertion at 320 px: it demands horizontal widget scrolling, explicitly superseded by RC234's vertically wrapped palette. Reconciled the historical browser fixture with production-like icon wrappers and required single-column geometry, horizontally scrollable page thumbnails, bounded horizontally overflow-free palette, vertical scrolling and last-tool reachability. Browser RC226 4/4, RC171 3/3 and RC234 9/9 locally pass. Also reconciled RC143's pre-tabbed formatter fixture with its actual `role=tabpanel` semantics and RC178's desktop-only left-filmstrip assertion with RC226's mobile top filmstrip; both historical browser tests now pass. Pre-npm mutation-tested RC235 guard added, and historical receipts preserved. Application CSS/TypeScript unchanged. RC235 full CI pending. Certified **85.25%** (43 accepted/17 partial), unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. Details: `docs/RC_CYCLE235_RESPONSIVE_BROWSER_COMPAT.en.md`.

---
# Quorivio 0.1.0-dev — RC234 — Responsive editor palette Chromium correction

**RC234:** Full GitHub CI `42245983528` at RC233 commit `d744de0eac508c5e6196e97315c09aa388c55985` failed real Chromium at 620 px: the palette overflowed 1198 px within a 608 px container. Resolved RC226/RC171 CSS cascade conflict by restoring vertical wrapping, bounded height and no horizontal overflow in the one-column mobile editor. Added RC234 real Chromium regression at nine widths (320–1440 px), mutation-tested CSS/source contract, and mandatory workflow verification. RC233 is historical, RC234 current. RC234 full CI pending; certified **85.25%** (43 accepted/17 partial), unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE234_PALETTE_RESPONSIVE.en.md`.

---
# Quorivio 0.1.0-dev — RC233 — Linked-results TypeScript compile gate fix

**RC233:** GitHub CI `42241665883` for RC232 (`68391862f85036cf0327e511afbfd5ff0db5da2e`) reached the strict frontend TypeScript gate and failed on seven TS2339 references to `showSourceTitle`, `showSourceAnswers` and `showCorrectAnswers` in `apps/web/src/main.tsx`, because the typed editor history omitted these existing canonical `PageDesign` keys. RC233 adds them to the narrow `Pick<>`, retaining strict typing and preserving presenter-only answer truth. Added RC233 pre-npm type contract regression; RC232 remains historical and RC233 is current. CI integration pending; last confirmed all-green RC219 `42197607753`. Certified **85.25%** (43 accepted / 17 partial), unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE233_LINKED_RESULTS_TYPECHECK.en.md`.

---
# Quorivio 0.1.0-dev — RC232 — Native converter CI dependency order correction

**RC232:** Full GitHub CI run `42237834439` for RC231 (`86721afdd9ebed4ee9158d5770d7e4535c3b77a8`) stopped at the RC229 pre-npm legacy consolidation stage: the 35-case real PDF/PPTX converter boundary module ran before installing Poppler, ReportLab and LibreOffice, producing 6 errors and 3 failures in the 101-test step. RC232 keeps pure-source tests before npm, moves the real conversion boundary suite after native/Python dependencies and adds a fail-closed ordering preflight. Historical RC231 remains pinned; RC232 is current. No application logic or policy change. Integrated CI RC232 pending; last confirmed full-green RC219 `42197607753`. Certified **85.25%** (43 accepted/17 partial), unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. Details: `docs/RC_CYCLE232_CONVERTER_CI_DEPENDENCIES.en.md`.

---
# Quorivio 0.1.0-dev — RC231 — Python import-path CI handoff

**RC231:** Full CI `42233651517` failed at the new RC230 pre-npm unittest due to `ModuleNotFoundError: ci_inventory_reference_guard`, because the helper was imported as `tools.verify_rc_current_inventory` without a sibling module path. Its module now deterministically adds the local tools directory to `sys.path` and resolves the same verifier names used by all legacy tests. Added Python subprocess acceptance without `PYTHONPATH`, RC231 current manifest and historical RC230 receipt. No application, database, auth or publish changes. Last full-green CI RC219 `42197607753`; full GitHub RC231 validation pending. **85.25%** certified (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE231_IMPORT_PATHS.en.md`.

---
# Quorivio 0.1.0-dev — RC229 — Historical source contract and background error handoff

**RC229:** New cumulative includes all RC228 work, which fixes failed GitHub quality gate `42226572219` (old RC225 schema gallery label in portaled modal). Local full Python discovery uncovered additional stale tests on import label/QR link/mobile scaling/named upload/PPTX fixture; updated these tests and restored sanitized `backgroundUploadError` handling in `uploadNamedFile` when `library==='backgrounds'`. Added RC229 101-case pre-npm acceptance. No permissions, database, publishing or privacy change. GitHub full CI still to be run after user's next commit; last verified full-green RC219 `42197607753`. **85.25%** certified (43 accepted/17 partial), flags `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE229_GLOBAL_DISCOVERY_RECONCILIATION.en.md`.

---
# Quorivio 0.1.0-dev — RC228 — RC225 legacy gallery gate recovery

**RC228:** Continue from cumulative RC228 after user-committed RC227 (`ec9de12e8f7e39cbc90d573bc2758b7fdf034ce2`). GitHub run `42226572219` failed at the RC225 Python check `test_gallery_covers_all_background_flows`: outdated inline schema gallery label despite the new accessible master dialog. Fixed the historical test to verify dialog semantics and selected background rather than the obsolete label, added tests for the exact committed shape and negative mutations, plus a CI pre-npm check. No runtime change; next full CI is pending. Last green RC219 `42197607753`; certified **85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE228_CI_GALLERY_CONTRACT.en.md`.

---
# Quorivio 0.1.0-dev — RC227 — Accessible background and responsive participant handoff

**RC227:** Continue from this cumulative archive, preserving RC226. The master ribbon opens the named, scrollable image library from a compact accessible icon command instead of embedding all thumbnails. Keyboard focus is trapped/restored, with Escape to close. Participant phone layout adapts to orientation/width until a manual 16:9, smartphone or reading selection overrides it. 398 web Node, 9 targeted Python, four Chromium fixture sizes and TSX syntax parsing pass. Full compiled React, PostgreSQL and integrated GitHub CI remain required. Last full-green CI RC219 `42197607753`; certified **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. See `docs/RC_CYCLE227_MASTER_BACKGROUND_PHONE_ROTATION.en.md`.

---
# Quorivio 0.1.0-dev — RC226 — Responsive studio handoff

**RC226:** All RC225 sources retained; accessible icon/caption master ribbon and shared widget colors, phone-default participant projection and mobile-safe studio, session selection/dashboard, editors and preview. No changes to API, database or permissions. Node API 628, web 394, focused Python 30, four representative CSS Chromium layouts passed; full compiled React and GitHub CI pending. Last green CI RC219 `42197607753`; **85.25%** certified (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE226_RESPONSIVE_STUDIO.en.md`.

---
# Quorivio 0.1.0-dev — RC225 — Asset library handoff

**RC225:** Preserves RC224 cumulative. Safe persistent filenames, server-enforced duplicate prompts, asset rename/delete with 204-aware immediate refresh, thumbnail-and-name background galleries, and proper master background preview. DB migration and portable bundle metadata retain names and exempt library copies from duplicate checks. Local API 628/frontend 390, RC225 Python and Chromium CSS green. Full CI required; last green RC219 `42197607753`. **85.25%** certified (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. `docs/RC_CYCLE225_ASSET_LIBRARY_AND_SCHEME.en.md`.

---
# Quorivio 0.1.0-dev — RC224 — Thumbnail context menu and Arial defaults handoff

**RC224:** Based on RC223, keeps all historical functionality while organizing thumbnail actions into keyboard/touch expandable groups with true viewport-clamped internal scrolling. Tested all new canvas/scheme widgets for Arial effective defaults without breaking customized title/master fonts. Node API/web, targeted Python and actual CSS Chromium viewport fixtures pass; compiled React and PostgreSQL full CI still pending. Last green RC219 run `42197607753`; certified **85.25%**, 43 accepted/17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. See `docs/RC_CYCLE224_THUMBNAIL_MENU_AND_ARIAL.en.md`.

---
# Quorivio 0.1.0-dev — RC223 — Context format, footer, QR and participant count handoff

**RC223:** Cumulative RC222+ code. Format panel opens only on context-menu Format, is tabbed and responsive, preserves complete server-validated border/effect/content/source link settings. Authored footer alignments, reserved QR URL row and self-sized participant counter corrected. Local Node/API/Python and two-size Chromium CSS fixture acceptance run; compiled React and full PostgreSQL CI pending. Last green GitHub CI RC219 `42197607753`, certified **85.25%**, 43 accepted/17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. See `docs/RC_CYCLE223_CONTEXT_FORMAT_AND_STAGE_LAYOUT.en.md`.

---
# Quorivio 0.1.0-dev — RC222 — Compact format and editor answer handoff

**RC222:** Base RC221 preserved; format toolbar vertically compact with phone swipe; corrected editor-only choice glyph spans (`white-space`/ellipsis) and applied normalized Arial/whole-widget answer font to main choices and subquestions. Test coverage: full API/web Node, Python source contracts, Chrome stylesheet fixture (1440/390), historical inventories and release headers. Full RC222 CI and genuine production server browser test pending. Last fully green RC219 `42197607753`. **85.25%**, 43 accepted/17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. See `docs/RC_CYCLE222_EDITOR_FORMAT_PARITY.en.md`.

---
# Quorivio 0.1.0-dev — RC221 — Results and PDF handoff

**RC221:** Last verified full-green campaign **RC219** `42197607753`. RC221 adds owner-only result truth controls, independently styled source questions and options, and preselected image-fidelity or partial editable PDF/PPTX import through a private Poppler worker. RC220/221 require full CI. **85.25%**, 43 accepted/17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag/release. See `docs/RC_CYCLE221_RESULTS_GRADING_AND_PDF_IMPORT.en.md`.

---
# Quorivio 0.1.0-dev — RC220 — PDF converter administration and linked-results formatting

**RC220:** RC219 fully green on GitHub run `42197607753`: 14 successful jobs (three final-image/publication jobs skipped). RC220 adds a platform-admin panel for an isolated PDF/PPTX worker with readiness checks, deployment prerequisites and persistent enable/disable control; separately configurable linked source title and answers, with bullet-prefixed bold responses and distinct customizable question colour. New full RC220 CI still pending. Certified **85.25%** (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag. See `docs/RC_CYCLE220_PDF_WORKER_AND_LINKED_RESULTS.en.md`.

---
# Quorivio 0.1.0-dev — RC219 — Full Python discovery and historical contract reconciliation

**RC219:** RC218 full CI (`42194028262`) reached the global `unittest discover` suite (2,115 cases: four failures and two import errors). Fixed two RC214 helper imports that broke under bare-module discovery and four stale contracts for unsaved page navigation, shared footer-number formatting, and independent answer underline/strikethrough. Added fail-closed negative mutations and early pre-npm testing in both import modes; application runtime unchanged. Full RC219 CI pending; last fully green RC203. Certified **85.25%** (43 accepted, 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE219_FULL_DISCOVERY_RECONCILIATION.en.md`.

---
# Quorivio 0.1.0-dev — RC218 — Browser PostgreSQL thumbnail rename handoff

**RC218 handoff:** Continue from the new cumulative RC218 ZIP. RC217 run `42191917542` / quality job `127805753403` timed out on the obsolete exact-name `Rinomina pagina` locator in real Chromium PostgreSQL editor acceptance. The current thumbnail menu uses `Rinomina pagina (R)` or `Rinomina pagine selezionate (R)`. Updated the browser test to scope the portaled `Azioni pagina 1` group, assert one anchored match, and retain real database readback/conflict/export checks. Added early negative-mutation preflight; no app-runtime changes. Full CI still required, last full green RC203. Certified **85.25%**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. Details in `docs/RC_CYCLE218_REAL_EDITOR_THUMBNAIL_RENAME_CI.en.md`.

---
# Quorivio 0.1.0-dev — RC217 — Dynamic participant-phone stage handoff

**RC217:** Continue from RC217 cumulative. RC216 full run `42150766799` failed because the old real Chromium participant fixture enforced 998px after RC207 increased minimum question choice rows, legitimately yielding 1028px. The updated browser contract derives expected height from seven visible public widget bounds, checks 16px margins/8px gaps/footer and rejects phantom private controls. RC168/RC169/RC177 historical tests reconciled, new early Python/Node mutation controls and local real Chromium 390/1440 green. GitHub RC217 full CI pending; runtime unchanged; certified **85.25%**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. See `docs/RC_CYCLE217_PUBLIC_PHONE_DYNAMIC_HEIGHT.en.md`.

---
# Quorivio 0.1.0-dev — RC216 — Chromium reauthentication handoff

**RC216:** Continue from cumulative RC216. RC215 full GitHub CI `42145939288` failed because a stale `main.narrow` selector looked for the old login container despite the correct accessible form already being rendered after a mocked 401. Chromium acceptance now checks the login controls and protected-editor absence, then requires the same workspace to reopen after authentication is restored without cookie deletion. New early preflight and negative mutations; application runtime unchanged. Full RC216 CI required; last full-green RC203. Certified **85.25%**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. See `docs/RC_CYCLE216_AUTH_RECOVERY_BROWSER_LOGIN.en.md`.

---
# Quorivio 0.1.0-dev — RC215 — Chromium result glyph test handoff

**RC215:** Continue from cumulative RC215. Full RC214 run `42144060435` reached RC141 Chromium test and failed due to comparing an output *element box* with a text `Range`. Test now compares glyph ranges and verifies final word/count remain on one line without clipping. Chromium passes across editor, presenter, rehearsal and participant at 1440/390 px, and rejects a synthetic 8 px offset. Early pre-npm negative-mutation guard added. Full RC215 GitHub CI still required; last full-green RC203. Certified **85.25%**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. See `docs/RC_CYCLE215_CHROMIUM_RESULT_GLYPH_ALIGNMENT.en.md`.

---
# Quorivio 0.1.0-dev — RC214 — Thumbnail selection and Escape focus CI handoff

**RC214:** Continue from cumulative RC214 preserving all RC204–213 features. Run `42142002249` failed the RC106 legacy inline thumbnail click contract. Reconciled three historic tests with Ctrl/Cmd multi-select, normal navigation, D/R/Backspace, dynamic labels and closed-session protections. Fixed Escape focus restoration in the portalled thumbnail menu; added fail-closed mutations and early pre-npm coverage. Full RC214 GitHub CI remains required for React/Chromium/PostgreSQL/Kubernetes; latest fully green RC203 `42110429701`. Certified **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag. See `docs/RC_CYCLE214_THUMBNAIL_SELECTION_CI.en.md`.

---
# Quorivio 0.1.0-dev — RC213 — Frontend page order typecheck handoff

**RC213:** Continue from the RC213 cumulative ZIP, preserving all RC204–RC212 features. The RC212 GitHub CI run `42140973603` identified real React `pageOrderPending` temporal-dead-zone TypeScript errors TS2448/TS2454. Initializer relocated before shortcut effect; pre-npm negative mutation tests guard recurrence. Need full GitHub CI for RC213. Latest fully green RC203 `42110429701`; certified **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag. See `docs/RC_CYCLE213_PAGE_ORDER_TYPESCRIPT_CI.en.md`.

---
# Quorivio 0.1.0-dev — RC212 — Public projection CI handoff

**RC212:** Resume from RC211 with all RC204–211 capabilities preserved. Reconciled RC185 with RC206: `presenter_activity_id` may be read internally only to compute the shared `presenter_page_number` but must not appear in the participant snapshot. Added Python negative mutations, four Node tests executing the actual function and a new CI preflight. RC212 full CI pending; last fully green RC203 `42110429701`. Certified **85.25%** (43 accepted, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag. See `docs/RC_CYCLE212_PARTICIPANT_PROJECTION_CI.en.md`.

---
# Quorivio 0.1.0-dev — RC211 — Numbering CI reconciliation handoff

**RC211:** Reconciled historic RC91/RC195 assertions to the RC206 presenter-visible page number shared by participant footer, retaining independent participant content. Added early fail-closed RC211 mutation checks. RC211 full CI pending; last full-green RC203 `42110429701`. Certified **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag. See `docs/RC_CYCLE211_PRESENTER_NUMBERING_CI.en.md`.

---
# Quorivio 0.1.0-dev — RC210 — Thumbnail rename CI reconciliation handoff

**RC210:** Resume from RC209, preserving all RC204–RC209 features. GitHub run `42138018546` quality job `127630992928` failed early because the October thumbnail test looked for direct `void renameCanvasPage(a)`; RC206 correctly routes thumbnail and R shortcuts via the ordered multi-selection handler, which calls `renameCanvasPage(page)` for authorized title-only updates. Updated historic source contract, added 3 negative/positive pre-npm regressions and retained the seven-module early CI gate (35 tests locally green). No product runtime changes. New full CI pending; last complete green RC203 `42110429701`. Certified **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. See `docs/RC_CYCLE210_THUMBNAIL_RENAME_CI.en.md`.

---
# Quorivio 0.1.0-dev — RC209 — Open Session owner actions handoff

**RC209:** Continue from this cumulative, preserving RC204–RC208. Owners can reset `active`/`paused`/`closed` sessions to ready or fully delete sessions from the Open Session list, with confirmation and no dashboard restoration. Existing owner-only reset API now accepts `closed`, erases all participant responses and rotates credentials while preserving authored pages/widgets and renewing expiry; deletion reuses existing complete erasure. UI rejects double clicks, refreshes listing, preserves login cookies. Node API 616, web 368 and 18 focused Python regressions green. PostgreSQL end-to-end lifecycle script extended; full CI pending. Last fully green RC203 `42110429701`. Certified **85.25%**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. Details: `docs/RC_CYCLE209_SESSION_LIST_ACTIONS.en.md`.

---
# Quorivio 0.1.0-dev — RC208 — Session recovery handoff

**RC208:** Starting from the RC207 cumulative, addressed the blank/frozen owner dashboard when reopening an already-running session. Authentication is checked before owner live WebSocket or session requests; the initial `/auth/me` and owner session snapshot have 12-second bounds, with a visible retry/return-to-sessions UI and automatic capped retry for transient failures. Expired authentication returns to the login view without erasing cookies; inaccessible or deleted sessions clear only the tab-local workspace route. Invalid/cross-session WebSocket snapshots cannot poison the dashboard, and missing optional statistics are normalized. A single unexpected React rendering crash automatically clears stale workspace routing and remounts once, with a visible non-destructive recovery fallback. QR polling remains live but has a 9-second per-request timeout and retains cache invalidation on URL rotation. Added Node tests, Python preflight and Chromium fixture scenarios for active-session restore, rotated code, 503 recovery, and 401 reauthentication. Chromium, integrated PostgreSQL and full GitHub CI for RC208 remain to be certified. Last independently verified full-green baseline: RC203, run `42110429701`; RC204–RC207 cumulative changes remain included. Certified **85.25%** (43 accepted/17 partial gates); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag. Read `docs/RC_CYCLE208_SESSION_RECOVERY.en.md`.

---
# Quorivio 0.1.0-dev — RC207 handoff — readable phone questions

**RC207 handoff:** Continue from RC206 cumulative. Eliminated unintended desktop 1280-cqw scaling of responses, input fields, buttons and rich-text marks in the independent 390px smartphone stage. Defaults: 22px question title, 18px answer fields/options/buttons, 44px minimum tap targets; explicit desktop and phone overrides preserved. Auto layout reserves room for 255-character wrapping and subquestions. New Python/Node preflight and actual Chromium CSS sizing check registered in CI. Local Node 616 API, 360 web, 40 Python tests and real Chromium fixture green. React TypeScript typecheck unavailable locally without vite/client, full integrated CI pending. Last verified full green RC203 `42110429701`. Product **85.25%** certified, 43 accepted/17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag. Details: `docs/RC_CYCLE207_SMARTPHONE_READABILITY.md`.

---
# Quorivio 0.1.0-dev — RC206 — Page selection, numbering, results and image library

**RC206:** continuing from cumulative RC205, presenter footer page numbers count only presenter-visible pages and are shared by all synchronized audience views, eliminating gaps. Ctrl/Cmd+click permits multiple thumbnail selection; **D** duplicates, **R** renames and **Backspace** deletes selected pages with a single confirmation for group deletion, while text fields and the canvas are protected from shortcut interception. The thumbnail context menu uses a viewport-bounded, independently scrollable document portal, so every action remains accessible. Question choices accept up to 255 characters in UI/API. Results bar rows have clearer spacing and count badges. Canvas contextual library controls rename user-owned background images and allow deletion only when no slide/master references remain, including legacy copies identifiable by SHA-256; controls are also present in the scheme editor. Local Node API 616/616, frontend 356/356 and 24 focused Python regressions passed; TypeScript syntax parsing passed; full React/TypeScript build, Chromium/PostgreSQL, visual editor/preview typography parity and RC206 GitHub full CI remain unverified. Latest fully green CI: RC203 (`42110429701`) including verified multiarch Docker Hub publication. Certified completion **85.25%** (43 accepted/17 partial gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, or tag. Details: `docs/RC_CYCLE206_PAGE_SELECTION_AND_NUMBERING.md`.

---
# Quorivio 0.1.0-dev — RC205 — Editor/master parity and PDF import handoff

**RC205 handoff:** Continue from this cumulative, preserving all RC200–RC204 changes. User-provided screenshot showed footer formatting palette taking the full page; common editor/scheme format ribbon is now compact with one typography selector scoped to entire widget/title/answers/submit/page-number. Source page results and their demo values appear in editor, while participation privacy remains enforced outside the editor. Imported PDF/PPTX pages now have a session-owned full-page image widget, are opened after confirmation, and PPTX export removes duplicate full-page images. The rasterized imported content can be overlaid by editable Quorivio widgets, but original PDF/PPTX page elements are not magically converted into editable text/shapes. Requires `QUORIVIO_ENABLE_CONVERTER=true`, an isolated converter URL/token and working shared volume; it fails visibly when not configured. Targeted Python regressions and syntax-only TypeScript validation passed; full build/CI pending. Last verified full green RC203 (`42110429701`). Certified **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE205_EDITOR_WIDGET_CONSISTENCY.en.md`.

---
# Quorivio 0.1.0-dev — RC204 — Anonymous export protection handoff

**RC204 handoff:** Resume from this complete cumulative after RC203 full-CI success, run `42110429701`, and verified native AMD64/ARM64 Docker Hub publish. Added a fixed five-distinct-participant threshold per anonymous statistical response bucket, unique respondent counts, suppression for missing IDs, non-identifying anonymous filenames, explanatory UI, and executable regression coverage including real OOXML worksheet cells. No changes to session QR refresh, editor grid, import/export portability, Kubernetes/OCI or publishing policies. API Node 615 and web Node 352 locally green before the final focused XLSX test, which also passes. Full RC204 GitHub CI and independent external release sign-offs remain outstanding. **85.25%** certified (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. Read `docs/RC_CYCLE204_ANONYMOUS_COHORTS.en.md`.

---
# Quorivio 0.1.0-dev — RC203 — Editor layout CI handoff

**RC203** handoff: Start from this full cumulative; RC202 committed, GitHub Actions run `42107111552` / job `127524721412` fails ONLY at real Chromium `tools/ci_editor_mock_layout_chromium.py` after successful Python staging, Node suites and builds. RC200 header CSS accidentally reduced the grid to two rows; wrapped widget rail was too short and canvas exceeded viewport. Three rows restored in all editor breakpoints, 280px reserved for desktop canvas fit, four Chromium widths checked and RC203 fast negative regression added. No changes to session QR updates or export/import behavior. Full RC203 CI pending; last complete green RC199 `42096705867`. **85.25%** certified (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE203_EDITOR_GRID_RECOVERY.en.md`.

---
# Quorivio 0.1.0-dev — RC202 — Python conversion dependency CI handoff

**RC202 handoff:** Resume from this cumulative; RC201 committed by maintainer, run `42105427044`, job `127518865236` fails before dependency install in `test_rc200_editor_portability` with missing `pptx`/`PIL`. Fixed only CI/test staging: early `RC200EditorPortability` class (4 dependency-free checks), late `RC200NativePowerPointPortability` class (2 fail-closed real PPTX cases) after required Python dependencies, added RC202 negative-staging regression. Preserve RC201 no-reload QR updates, RC200 portable formats, history and manifest receipts. Full RC202 CI is pending; last green RC199 run `42096705867`. **85.25%** certified (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. Read `docs/RC_CYCLE202_CI_DEPENDENCY_STAGING.en.md`.

---
# Quorivio 0.1.0-dev — RC201 — Live QR handoff

**RC201 handoff:** Resume from this cumulative. RC200 import/export work retained; RC199 last full CI success `42096705867`. Canonical QR URLs now auto-refresh in dashboard/widgets, update immediately from live owner snapshots after a rotated join code, poll every 12 seconds to catch public-origin changes, refresh on focus/online/visibility, remove stale QR pixels on revoke or fetch error, and use the shared DB-configured public origin across replicas. Reset keeps owner WebSockets but disconnects deleted participants. Local QR state 4/4, focused Python 21/21; full React/PostgreSQL/Kubernetes CI pending. Certified **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag. Read `docs/RC_CYCLE201_LIVE_QR_SYNC.en.md`.

---
# Quorivio 0.1.0-dev — RC200 — Editor portability handoff

**RC200 handoff:** RC199 has full green CI (run `42096705867`). New compact editor title/owner row, no duplicate sidebar scheme command; thumbnail menu can insert PDF/PPTX after selected slide using the isolated worker; transferable `.quorivio` now includes referenced slide snapshots with owner-independent asset remapping; native PPTX/PDF export preserves imported raster slides; owner-only identifiable statistics or default anonymized aggregated CSV/XLSX. Local targeted tests pass; CI of RC200 pending. Certified **85.25%** (43 accepted, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag. `docs/RC_CYCLE200_EDITOR_PORTABILITY.en.md`. 

---

# Quorivio 0.1.0-dev — RC199 — GitHub #299 active release-header regression fix

**RC199:** starts from maintainer-committed RC198 (`0375877`), GitHub Actions #299 production quality gate failed at `Validate active RC release headers against the current inventory` because RC198 status summaries lacked explicit flags in their current (pre-divider) sections. Synchronized all four RC199 headings/flag declarations; added early regression tests and a ZIP-contained-header preflight; retained immutable RC198 inventory and historical entries. No runtime edits, no claim of full GitHub CI pass. **85.25%** certified (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE199_RELEASE_HEADER_CI_FIX.en.md`.

---

# Quorivio 0.1.0-dev — RC198 — Answer decoration parity

**RC198:** based on user-committed RC197 (`0794f02`, CI #298 launched). Added independently validated answer underline and strikethrough for Whole widget / Answers scopes and independent subquestions. API Node 605/605, frontend Node 348/348 passed; compiled React/TypeScript CI pending. **85.25%** certified (43 accepted, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE198_ANSWER_DECORATION.en.md`.

---

# Quorivio 0.1.0-dev — RC197 — Kubernetes Python integration contract reconciliation

**RC197:** GitHub run #297 (`42085779348`) failed in the Kubernetes Python step after 2,024 tests (six stale historical assertions). Reconciled and moved early before npm the independent rehearsal page, smartphone, reaction, typography and typed subquestion checks. No runtime changes. Full Python `2,027` run: `2,026` passed (1 skipped), targeted `35/35`, API Node `603/603`, frontend Node `345/345` green; full CI pending. Certified **85.25%**, 43 accepted/17 partial; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Last published baseline RC190. No commit/push/tag. `docs/RC_CYCLE197_KUBERNETES_PYTHON_RECONCILIATION.en.md`.

---

# Quorivio 0.1.0-dev — RC196 handoff — strict frontend types

**RC196 handoff:** Source is RC195 cumulative, now corrected for GitHub #296’s three React TS errors (`linkedResultQuestion` import and `showSourceQuestion` editor typing). Added early Python negative-mutation guard and post-install full frontend strict compiler, without altering API, result permissions or projection routing. Frontend/API Node suites green; full Vite CI must confirm. Preserve immutable inventories; RC196 cumulative SHA receipt. RC190 remains published baseline; **85.25%** certified (43 accepted/17 partial). No commit/push/tag. `docs/RC_CYCLE196_FRONTEND_RESULTS_TYPES.en.md`.

## Previous cycle RC195

# Quorivio 0.1.0-dev — RC195 handoff — master font CI contract

**RC195 handoff:** GitHub run #295 failed the RC161 pre-npm literal `fontFamily:'Arial'` grep. The default is now shared in `slide-master.ts`, with custom master/widget precedence resolved through `widgetDisplay`, `stageWidgetTypography` and `widgetTypographyStyle`. Updated historic RC161 and added early, fail-closed RC195 Python/Node tests without changing app runtime. Latest fully green and published baseline RC190 (`42027634427`/`42032833536`). Full RC195 CI pending. Certified **85.25%**, 43 accepted/17 partial; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag. `docs/RC_CYCLE195_CENTRALIZED_FONT_CI_RECONCILIATION.en.md`.

## Previous cycle RC194

# Quorivio 0.1.0-dev — RC194 handoff — typography and caret-selection fixes

**RC194 handoff:** Added `widget-typography-defaults.ts` shared between editor and stage; normalized Arial/bold 22 question versus regular 16 answer for missing defaults; repaired answer line-wrap and CSS `font-family` priority across surfaces. `widget-text-marks.ts` now inherits the previous character style when inserting, including exact mark boundaries and UTF-16 text. Widget Format restores highlighted selection via `restoreDomTextRange` after edits. New Node/Python/browser regression preflights and immutable inventory; all 342 frontend and 603 API tests pass locally. Full integrated CI still pending. Last green published RC190 `42027634427`/`42032833536`. Certified **85.25%**, no commit/push/tag. `docs/RC_CYCLE194_QUESTION_TEXT_TYPOGRAPHY.en.md`.

## Previous cycle RC193

# Quorivio 0.1.0-dev — RC193 — Intermittent editor caret and answer typography fixes

**RC193:** RC193 handoff: Added focus ownership in `RichWidgetText` (only active DOM element restores selection), clearing stale caret memory at blur and avoiding redundant sibling DOM rewrites. Restored numeric font-size field and always-visible spinner arrows in Widget Format, in all scopes, with temporary editing state and commit on blur/Enter. Applied default Arial and author font to answer options and subquestions despite historical CSS `font:inherit!important`; updated properties fallback. Real browser/PostgreSQL smoke added to CI to type continuously without reload. Previous RC192 intact; final integrated CI pending. Certified **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE193_EDITOR_FOCUS_FONT.en.md`.

## Previous cycle RC192

# Quorivio 0.1.0-dev — RC192 — Source-authored results content and confirmed page deletion

**RC192 handoff:** From cumulative RC191, added `showSourceQuestion` for read-only source-authored question title/options above linked statistics in rehearsal/live, respecting source typography and subquestion marks. Fixed DELETE /pages/:aid to unlink cross-page audience/result dependencies and increment affected revisions transactionally, instead of returning 409; editor confirms, reloads and reports detachment. Last GitHub full green RC190 `42027634427` and publish `42032833536`; RC192 full CI pending. Certified completion **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. `docs/RC_CYCLE192_SOURCE_RESULTS_AND_DELETE.en.md`.

## Previous cycle RC191

# Quorivio 0.1.0-dev — RC191 — Cross-page result routing and split-screen rehearsal parity

**RC191:** Based on published RC190, full green GitHub Actions run `42027634427` and successful Docker Hub multiarch publish run `42032833536` (commit `bb80a3ce`). Fixed cross-page Results widgets in rehearsal with a source-activity resolver shared with the live presenter view, removed full-WebSocket-snapshot cancellation of HTTP statistics requests (3s polling), and aligned side-by-side/participant/mobile rehearsal with hidden presenter pages and per-page audience routing. Updated historical assertions and added dependency-free CI regression preflight. Local frontend Node 326/326, API Node 599/599, targeted Python checks PASS. Full post-commit React/Chromium/PostgreSQL CI for RC191 pending. Certified completion **85.25%** (43 accepted gates, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, or tag. Details: `docs/RC_CYCLE191_CROSS_PAGE_RESULTS_REHEARSAL.en.md`.

## Previous cycle RC190

# Quorivio 0.1.0-dev — RC190 — Built-React MFA test fixture repair

**RC190:** GitHub run `42023471301` (job `127231773092`) passed the RC189 TypeScript build but stopped inside `tools/ci_rc186_mfa_enter_chromium.py`: the “Informativa cookie funzionali” dialog never appeared. The test mounted compiled React on `about:blank`, an opaque origin, without the in-memory `localStorage`, `sessionStorage`, and `document.cookie` fixtures already used in recovery and preview tests. React reads storage while mounting and could not render the initial dialog. RC190 installs those isolated mocks before loading the compiled bundle, with no change to production cookies, consent, or MFA behavior. The isolated Chromium fixture passed at 1440/390px and Python regression checks passed. The compiled-React E2E and whole RC190 CI must still run on GitHub (npm dependencies unavailable offline here). Last fully green CI: RC184 run `41993094578`. Certified readiness **85.25%** (43 accepted gates, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, or tag. See `docs/RC_CYCLE190_MFA_FIXTURE_CHROMIUM.en.md`.

## Previous cycle RC189

# Quorivio 0.1.0-dev — RC189 — Strict portable page map typing and early API CI build

**RC189:** GitHub run `42021367453`, job `127224676741`, passed RC92 but the API build failed with `TS2345` (`Map<unknown,unknown>` instead of `ReadonlyMap<string,string>`) in `createFromPortable`. A typed string-only portable ID map preserves legacy imports and cross-page links. Added a negative TypeScript regression and an early mandatory `tsc --noEmit -p apps/api/tsconfig.json` just after npm, before expensive browser/PostgreSQL checks. Local Node suites: 599 API + 321 frontend; full RC189 GitHub CI remains to be verified. Certified completion **85.25%** (43 accepted, 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE189_PORTABLE_IMPORT_TYPECHECK.en.md`.

# Quorivio 0.1.0-dev — RC188 — Separate presenter/audience first-page CI reconciliation

**RC188:** reconciled the legacy RC92 assertion expecting `ORDER BY position,id LIMIT 1`. Since RC185, starting a projection must load ordered pages, choose the first **presenter-visible** page (`firstPresenterPage`), resolve its audience target (`audienceForPresenter`), and atomically update both projection pointers under the session row lock without rewinding an existing presentation. Added an early RC188 fail-closed preflight with negative mutations and a real TypeScript routing behavior test. No runtime changes. Reconciled old RC144/RC167/RC168/RC169/RC131, deadline and page-number preflights. RC187 GitHub run `42011405908` stopped at RC92 before npm; ClamAV passed. Last fully green CI remains RC184 `41993094578`. Certified completion **85.25%** (43 accepted gates, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE188_PRESENTER_START_CI.en.md`.


**Completed local checks:** 87/87 dependency-free CI preflight commands, 599/599 API tests, 321/321 frontend tests, RC92/RC185/RC188 contracts and SHA-256 source inventory. Post-commit GitHub CI for RC188 remains required.

---

# RC187 — Optional true/false answer keys handoff

RC187 extends the uncommitted cumulative RC186 baseline with optional single/multiple-choice grading, independent question answer keys, widget properties and canvas contextual editor selectors, default-False behavior, full reset, and private post-submission answer feedback. Answer keys stay hidden from public snapshots, revisions isolate changes and duplicate requests reference stored submissions. Local Node/Python regressions pass; full GitHub CI with TypeScript/Vite and authenticated React/PostgreSQL still pending. Last fully green GitHub run RC184 `41993094578`. Certified **85.25%** (43 accepted, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. See `docs/RC_CYCLE187_QUESTION_ANSWER_KEYS.en.md`.

---

# RC186 — TOTP Enter keyboard handoff

RC185 remains the cumulative uncommitted functional baseline in this conversation. RC186 makes the TOTP field submit on Enter through a real form, with validation and a one-request-at-a-time guard while preserving the email and recovery MFA paths. Added early source contracts and a built React Chromium CI fixture. GitHub build/browser acceptance must be checked after the next commit. Last confirmed full green RC184 run `41993094578`. Certified **85.25%** (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag. See `docs/RC_CYCLE186_MFA_ENTER.en.md`.

---
# RC185 — Dual projection and cross-page results handoff

Baseline: RC184 user-committed, GitHub Actions `41993094578` success (14 successful jobs). New source provides two independent projection pointers, canvas routing and presenter navigation skipping, cross-page live results through existing authenticated APIs, server-side scope/identity checks, portable archive remap and autosave/three-way merge support. See `docs/RC_CYCLE185_DUAL_PROJECTION.en.md` and validation receipt. No commit/push/tag done. Certified completion stays **85.25% / 43 accepted + 17 partial**. After user commit, verify migrations/real PostgreSQL with question page hidden from presenter, results-only presenter page mapping to public questions, WebSocket and native browsers, portable roundtrip and full CI with no publication.


Release flags: `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

---
# Quorivio 0.1.0-dev — RC184 — converter APT security update

**RC184:** GitHub Actions run `41988947593` passed Production quality gate, Chromium/PostgreSQL, ClamAV and Kubernetes/Podman/OCI checks; the only RC failure was the converter Trivy scan: `apt`/`libapt-pkg7.0` 3.0.3 vulnerable to CVE-2026-109518 (fixed in 3.0.4). Added early fail-closed APT upgrade and installed-version check in the Dockerfile, plus a security/Trivy preflight before expensive tests, preserving the blocking HIGH/CRITICAL scan. **85.25% certified (43 accepted/17 partial)**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`; the next CI must validate the actual Trivy scan. No assistant commit/push/tag. See `docs/RC_CYCLE184_CONVERTER_APT_SECURITY.en.md`.

---

# Quorivio 0.1.0-dev — RC183 — full Python discovery CI handoff

**RC183:** GitHub run `41952294082` reached the final 1,948-test Python discovery after successful build, React/Chromium and PostgreSQL acceptance. Four historic RC139/RC141/public-stage source-string assertions failed; reconciled with real shared title, three-mode public presentation and activity-scoped media contracts. Added early CI guard and negative mutation tests. No application runtime changes. Certified **85.25% (43 accepted/17 partial)**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`; full post-commit CI pending. No assistant commit/push/tag/deploy. See `docs/RC_CYCLE183_FULL_PYTHON_DISCOVERY_RECONCILIATION.en.md`.

---
# Quorivio 0.1.0-dev — RC182 — editor conflict indicator CI handoff

**RC182 after user-committed RC181:** CI `41944096707` passed compiled browser and participant/PostgreSQL checks, then failed at `ci_browser_editor_conflict_visibility.py` because the 1100px error status was clipped by the later RC171 140px important cap. Fixed responsive error-only wrapping, added 12 Chromium cases across 1440/1100/960/390px and red-before/green-after regression, moved the browser guard before database setup. Current inventory refreshed, historical manifests preserved. **85.25% certified (43 accepted / 17 partial).** `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag/deploy. GitHub CI for RC182 not yet run. See `docs/RC_CYCLE182_CONFLICT_INDICATOR_FIDELITY.en.md`.

---
# Quorivio 0.1.0-dev — RC181 — Chromium accessible disclosure dock CI handoff

**RC181 after user-committed RC180:** GitHub `41931287829` passed earlier checks but `ci_accessible_disclosure_chromium.py` failed because its historical fixture required a toolbar/disclosure overlap removed by the RC180 dock. Reconciled the browser assertion and its historical unittest; early CI regression now enforces no overlap, genuine pointer hit-test and working accessible controls in touch/desktop Chromium. No runtime behavior changed. New immutable source receipt; CI acceptance remains pending. **Certified 85.25% (43 accepted/17 partial).** `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag/deploy. See `docs/RC_CYCLE181_ACCESSIBLE_DISCLOSURE_DOCK_CI.en.md`.

---
# Quorivio 0.1.0-dev — RC180 — editor palette/context handoff

**RC180:** GitHub `41913987787` confirmed RC179 selection controls work but exposed the opposite pointer obstruction: the fixed arrangement panel blocked the `Linee` insert button in the wrapped palette. The latest cumulative moves contextual selection/arrangement panels into a bounded, scrollable dock inside the stage, after the insert rail; it does not need z-index escalation. Red-before/green-after native Chromium pointer testing alternates Duplicate → Linee → Align → Linee without closing the selection tools, at 1440/960/390 widths. Historical inventory receipts preserved; CI checks added before authenticated editor E2E. **85.25% certified / 43 accepted / 17 partial**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full GitHub CI pending user commit. No assistant commit/push/tag/deploy. See `docs/RC_CYCLE180_EDITOR_TOOLBAR_RAIL_POINTERS.en.md`.

---
# Quorivio 0.1.0-dev — RC179 — Editor contextual pointer handoff

**RC179:** fixed real Chromium editor click obstruction from CI `41878608401`: RC178's multirow palette (z13) covered the stage (z1) floating `Duplica selezione` tool despite its child z48. CSS lifts the stage only while selection tools are open, preserving header and palette behavior. Verified a red-before/green-after native Chromium click at 1440×900, 960×800 and 390×844 plus early Python regression. Re-run full GitHub CI after user commit to confirm the remaining authenticated React/PostgreSQL browser checks. **85.25% certified / 43 accepted / 17 partial**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no assistant commit/push/tag/deploy. See `docs/RC_CYCLE179_EDITOR_SELECTION_STACKING_CI.en.md`.

---

# Quorivio 0.1.0-dev — RC178 — editor palette/Chromium CI handoff

**RC178 after RC177:** analyzed run `41871700136` where Chromium editor mock failed on legacy x-scroll assertion after successful npm installation, Node unit tests and frontend/backend compilation. Fixed a real CSS clipping bug: wrapped catalog now receives an automatically sized, vertically scrollable row rather than fixed 80px; bounded 16:9 canvas remains visible. Updated the browser assertion and added mutation-tested RC178 preflight. Certified completion **85.25% (43 accepted / 17 partial)**; authenticated/physical-device acceptance pending. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/deploy. See `docs/RC_CYCLE178_EDITOR_PALETTE_CI.en.md`.

---
# Quorivio 0.1.0-dev — RC177 — CI handoff on historical live selectors

**RC177:** reproduced GitHub Actions `41865155281` failure in RC167 historical contract. Reconciled historical RC144/167/168/169 preflights to reflect RC176's separate phone, reading and faithful 16:9 modes plus the 998px public phone fixture. Added negative regression and CI early test, rotated immutable current inventory to RC177, kept RC176 and earlier checksums unchanged. No runtime functional modification and **85.25% (43 accepted / 17 partial)**. 589 preflight tests now pass (one skipped), plus 313 web and 588 API tests; 1770-file cumulative ZIP integrity verified. Build and authenticated browser CI pending. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit/push/tag/deploy. See `docs/RC_CYCLE177_HISTORICAL_LIVE_CI_RECONCILIATION.en.md`.

---
# Quorivio 0.1.0-dev — RC176 — Accessible DOM order and participant modes

**RC176 after RC175:** corrected actual keyboard/screen-reader DOM order in public accessible reading (footer last, no decorative graphic or presenter-only widgets), with the authored 16:9 stage unchanged. Fixed the authenticated Chromium fixture that conflated phone and accessible views; independently assert all three display modes and desktop/mobile normalized slide geometry. Shipped real TypeScript policy + Chromium CSS checks. **313/313 Web Node, 588/588 API, 25/25 targeted Python and Chromium CSS PASS.** Current Vite/React+PostgreSQL/CI not yet run. **85.25% certified (43 accepted, 17 partial)**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/deploy. See `docs/RC_CYCLE176_ACCESSIBLE_DOM_AND_MODE_PARITY.en.md`.

---
# Quorivio 0.1.0-dev — RC175 — Public 16:9 media fidelity handoff

**RC175 cumulative after RC174:** fixed a measured Chromium discrepancy where an image or video in an authored live participant widget reverted to intrinsic/default height on a narrow viewport instead of following its 16:9 widget frame. Media-only fit containers now have definite height; public videos use the projection-media class and stage-fidelity/stage-phone CSS preserves object-fit without distorting media. Browser CSS acceptance at 1280/390/320 px passes for image, video, and source-cropped image, with neutral accessible reading unchanged. **309/309 frontend Node + 588/588 API Node tests pass.** Full Vite build, authenticated React/PostgreSQL and physical-device screenshots still need independent CI validation. **85.25% certified (43 accepted / 17 partial).** `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/deployment. See `docs/RC_CYCLE175_PARTICIPANT_MEDIA_FIDELITY.en.md`.

---
# Quorivio 0.1.0-dev — RC174 — Single-stage participant handoff

**RC174 cumulative after RC173:** active participant pages no longer render duplicate session logos/titles or legacy media outside authored widgets, and 16:9 on narrow phones scales label/textarea padding and text with the slide. Chromium DOM/CSS checks at 1280/390/320 px and 307 web Node + 588 API Node + 23 targeted Python checks pass. Authenticated React/PostgreSQL, real-device validation and Vite build in CI are still pending. **85.25% certified (43 accepted / 17 partial).** `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/deploy. See `docs/RC_CYCLE174_PARTICIPANT_SINGLE_STAGE.en.md`.

---
# Quorivio 0.1.0-dev — RC172 — Mixed phone authoring handoff

**RC172 cumulative after RC171:** manually placed phone widgets reserve space, automatic widgets adapt without avoidable overlap, and editor/public phone stage heights agree. Compact automatically keeps authored phone text and color styles. **296 web Node tests pass**; Python preflight included, full Vite CI and authenticated browser/device checks still pending. **85.25% certified (43 accepted / 17 partial)**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/deploy. See `docs/RC_CYCLE172_PHONE_MIXED_AUTHORING.en.md`.

---
# Quorivio 0.1.0-dev — RC171 — Mobile editor/palette handoff

**RC171 cumulative after RC170:** top-header phone editor toggle, compact automatic phone stage preserving explicit overrides, properly sized line/shape icons and right-click/long-press/keyboard/ellipsis preset access. Local tests and inventory in the package; authenticated real-browser and full Vite CI still required. **85,25% certificato / 85.25% certified (43 accepted / 17 partial)**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/deploy. Vedi / See `docs/RC_CYCLE171_EDITOR_PHONE_PALETTE.it.md`.

---
# Quorivio 0.1.0-dev — RC170 — Master-aware phone footer numbering parity

**RC170:** fixed unreadably small phone page numbers and conflicting 5px/10px preview/live margins; editor, preview and public phone use authored logical pixel sizes and independent padding, including manual number anchors, while 16:9 desktop sizing is unchanged. The standard page editor displays the inherited master footer number without materializing the master widget into the page draft. Node/Python and local Chromium 390/1440 checks added; authenticated Chromium/PostgreSQL validation awaits CI. **85.25% certified (43 accepted / 17 partial gates)**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE170_PHONE_FOOTER_NUMBER_PARITY.en.md`. No commit/push/tag/deploy.

---
# Quorivio 0.1.0-dev — RC169 — Rating and phone font handoff

**Cumulative RC169 after RC168:** one rating rendering component and master-aware mobile title size, expanded disposable real-browser/PostgreSQL acceptance for rating controls and footer; new GitHub CI not yet confirmed. Preserve historical manifests; **85.25% (43 accepted / 17 partial)**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`, no commit/push/tag/deploy. See `docs/RC_CYCLE169_RATING_PHONE_RENDER_PARITY.en.md`.

---
# Quorivio 0.1.0-dev — RC168 — Participant phone visual fidelity handoff

**RC168:** filter presenter-only widgets before mobile stage size and layout generation in both participant preview and live rendering. Adds Chromium 390/1440px layout and PostgreSQL-authenticated widget/footer acceptance, preserving mobile overrides, master inheritance and 16:9. Independently reviewed physical-device A3 remains pending; certified completion **85.25% (43 accepted / 17 partial)**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE168_PHONE_VISIBLE_GEOMETRY.en.md`. Do not automatically commit/push/tag/deploy.

---
# Quorivio 0.1.0-dev — RC167 — Live presentation fidelity handoff

**RC167:** RC166 passed GitHub run 41808754419 including verified multiarch publication. Shared title/graphics/QR policy and participant-only widget filtering eliminate live/preview differences. Disposable PostgreSQL Chromium now asserts no legacy line/shape captions or presenter-only shells; test targets and failure artifacts are hardened to prevent token leaks. GitGuardian's prior incident was marked «ignore» by the operator, scanners remain enabled. **Certified completion 85.25% (43 accepted / 17 partial)**; independently reviewed A3 remains pending. No commit/push/deploy; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE167_LIVE_PREVIEW_FIDELITY.en.md`.

---
# Quorivio 0.1.0-dev — RC166 — Ephemeral CI credentials and GitGuardian triage

**RC166:** full RC165 GitHub run `41802327982` passed. Preventive hardening for external GitGuardian "Generic Password" report: remove fixed credentials in primary CI; use ephemeral run-scoped values. **The actual incident still requires its file/line from the GitGuardian portal**; do not classify it without evidence. Certified completion 85.25% (43 accepted / 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE166_GITGUARDIAN_TRIAGE.en.md`.

---
# Quorivio 0.1.0-dev — RC165 — Participant/CI handoff

**RC165 after RC164:** fix stale disposable Chromium participant acceptance by writing explicit editable question and topic-question widgets on the legacy Title-only page before activation. Confirm native controls, widget answers and presenter-only topic data; preserve independent legacy moderation coverage and omit standalone Q&A UI. No runtime changes. GitHub full CI and authenticated browser still pending. **85.25% certified** (43 accepted / 17 partial). No assistant commit, push or deploy. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE165_AUTHORED_PARTICIPANT_BROWSER.en.md`.

---
# Quorivio 0.1.0-dev — RC164 — Chromium palette CI handoff

**RC164 after RC163:** adapt actual Chromium editor rail acceptance to RC161 graphic insert triggers (`data-graphic-palette`) and exercise right-click dialogs for Linee/Forme. Preserve icon-label uniqueness and current runtime; new negative-mutation preflight. Full GitHub CI and authenticated integration remain pending. **Certified completion 85.25%** (43 accepted, 17 partial). No assistant commit/push/deploy; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE164_GRAPHIC_PALETTE_CHROMIUM.en.md`.

---
# Quorivio 0.1.0-dev — RC163 — TypeScript build handoff

**RC163 after RC162:** fix missing `showQrUrl` editor history declaration and unreachable checks for shape/line in the non-graphic insert path, matching the TS2339/TS2367 errors reported in GitHub run `41756050958`. Early preflight with negative mutations. RC162 history preserved; next step run full CI, then real editor/mobile QR and Docker acceptance. **Certified completion 85.25%** (43 accepted / 17 partial). No assistant commit, push or deploy. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE163_TYPESCRIPT_BUILD_HOTFIX.en.md`.

---
# Quorivio 0.1.0-dev — RC162 — Smartphone editor and responsive QR handoff

**RC162 after RC161:** a sliding Desktop/Smartphone editor switch, editable phone geometry with automatic defaults and explicit resets, and QR visibility flags (title off by default, URL optional) with compact responsive styling. Mobile edits cannot freeze untouched auto positions or replace canonical desktop geometry. Backend validates QR-only URL option. Regression tests and Chromium compact QR fixture added; full GitHub CI plus authenticated preview/live parity still pending. **Certified completion 85.25%** (43 accepted / 17 partial); no assistant commit, push or deploy. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE162_SMARTPHONE_QR.en.md`.

---
# Quorivio 0.1.0-dev — RC161 — Master and graphic presets handoff

**RC161 after RC160:** Arial default, inherited and secured master picture backgrounds, portable archive image remapping, graphics-only lines and shapes with mouse/right-click, mobile long-touch and keyboard presets. Presets remain editable in shared properties and custom font/phone backdrops are preserved. Full GitHub CI and live authenticated acceptance still pending. **Certified completion 85.25%** (43 accepted / 17 partial). No assistant commit/push/deploy. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. See `docs/RC_CYCLE161_MASTER_GRAPHIC_PRESETS.en.md`.

---
# Quorivio 0.1.0-dev — RC160 — Authored interaction and mobile footer parity

**RC160 after RC159:** removed always-on participant word/question and reaction controls outside the canvas; kept authored widget interaction. The footer is last in accessible reading and at the bottom of the automatic smartphone layout, with explicit phone edits unchanged. The optional rating comment is visibly white in Chromium fixtures across surfaces. Full CI and real authenticated presenter/participant acceptance remain open. **Certified completion 85.25%** (43 accepted / 17 partial). No assistant commit/push/deploy. See `docs/RC_CYCLE160_WIDGET_OWNERSHIP_FOOTER.en.md`. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

---

# Quorivio 0.1.0-dev — RC159 — Live/preview parity and presenter rate limits

**RC159 after RC158:** GitHub runs `41730792802` and `41739841860` against RC157 are confirmed successful, including multiarch Docker Hub publication in the second run. Implemented distinct lifecycle colors, optional white rating comment parity, exact submit text, shared fail-closed presenter-specific rate buckets, and live participant 16:9 canvas/title/background parity plus master-aware presenter title sizing. Local Node, Python and Chromium CSS fixture tests pass; new full CI and authenticated screenshot comparison are still required. RC158 historical inventory immutable; RC159 current. **Certified 85.25%** (43 accepted / 17 partial); no assistant commit/push/deploy. See `docs/RC_CYCLE159_LIVE_PREVIEW_UI_RATE_PARITY.en.md`. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

---

# Quorivio 0.1.0-dev — RC158 — Manual Docker browser dependency handoff

**RC158 after RC157:** manual workflow `41737243981` stopped at mandatory real Chromium JPG/Logo PostgreSQL acceptance with missing Python `playwright`, because the earlier Playwright install was conditional on `browser_test`. Node 582+251 and npm build passed; image-build was skipped, not failed. RC158 provisions missing Python browser deps immediately before this unconditional test and smoke-tests the preinstalled Chromium binary when not already exported; never bypasses the acceptance. An early CI regression enforces ordering and opt-in publishing security. RC157 historical manifest immutable. **Certified 85.25%** (43 accepted / 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. New full CI and real container build required; 500-user trial pending. No assistant commit/push/deployment.

---

# Quorivio 0.1.0-dev — RC157 — Release evidence import safety handoff

**RC157 after RC156:** GitHub run `41723978345` failed during grouped SHA-256 evidence checks because historical RC146 unittest package imports omitted the tools module path, despite passing the prior 1,802-test Python suite. The release status guard now resolves sibling modules in both script/package contexts, grouped CI sets `PYTHONPATH: tools` and an early no-PYTHONPATH regression reproduces the original invocation. RC156 remains historical, RC157 current. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Runtime unchanged; full CI and real 500-user demonstration pending. No assistant commit/push/deployment.

---

# Quorivio 0.1.0-dev — RC156 — Full Python-suite editor contract handoff

**RC156 after RC155:** the full integration workflow run `41720825704` failed with three obsolete source-snippet assertions among 1,798 Python tests. Tests now check device-aware uploads, page/device remount isolation and live unsaved rehearsal including mobile state, with negative mutations and early CI checks. Application unchanged; RC155 preserved historical; RC156 is the current checksum inventory. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Re-run full GitHub CI; independent actual 500-user test and operator sign-off remain pending. No assistant commit/push/deployment.

---

# Quorivio 0.1.0-dev — RC155 — Revision-conflict ribbon regression CI fix

**RC155 after committed RC154:** GitHub Actions run `41719228484` passed early inventory and CI preflight, but failed the frontend Node editor autosave suite: the historical RC139 source-contract test still matched `active&&!ribbonDismissed&&widgets.some`, while the RC153 runtime correctly added `!suspendFormattingRibbon` to prevent a selected-widget toolbar from intercepting the revision-conflict reconciliation button. Updated the historical RC139 assertion to check both the suspend flag and the parent `suspendFormattingRibbon={pageConflict}` binding. Added four Node and four Python RC155 checks, including negative mutations for the missing guard, broken wiring and accidental loss of active selection. Added an early CI Python guard ahead of npm and preserved RC154 as immutable historical evidence. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full GitHub CI, authenticated Chromium/PostgreSQL and real 500-person load test still require independent confirmation. No assistant commit/push/deployment. See `docs/RC_CYCLE155_RIBBON_CONFLICT_CI_FIX.en.md`.

---

# Quorivio 0.1.0-dev — RC154 — Live test presence and opt-in Gravatar

**RC154 after RC153:** the test presentation now includes connected-participant counters, two independent questions, 0–9 ratings, reactions and results. Added explicitly authorized reset/start, 500 independent widget answers and WebSocket presenter-observed peak validation to the Git-tracked CLI; optional opt-in Gravatar image import/refresh on successful login with local storage, antivirus and privacy safeguards; administrator manuals regenerated in IT/EN. The prior RC153 inventory remains immutable. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full GitHub CI, authenticated browser/PostgreSQL and actual server 500-user rehearsal remain pending. No commit/push/deployment by assistant. See `docs/RC_CYCLE154_LIVE_LOAD_GRAVATAR.en.md`.

---

# Quorivio 0.1.0-dev — RC153 — 500-answer test and conflict-safe editor handoff

**RC153 cumulative after committed RC152:** CI `41711064819` reached real PostgreSQL-authenticated Chromium editor acceptance and failed because the floating widget ribbon intercepted the revision-conflict reconciliation button. Suppress the ribbon while the conflict UI is active, retaining recoverable edits. Add a 3-page owner-private, lazily and transactionally provisioned load-test presentation (unique marker, clean replacement after deletion), plus an explicitly confirmed 500-participant anonymous poll CLI measuring the actual database response delta. Keep all historical RC152 receipts immutable. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full CI and authorized real-server testing pending; no assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC152 — Browser result wrapping acceptance handoff

**RC152 cumulative after committed RC151:** fix RC141 Chromium acceptance mismatch seen in run `41708756081` without reverting RC143 product behavior. Long labels wrap within the widget; final word and square-bracket count remain together. The same production stylesheet is exercised in four authored widget shells at 1440/390px with a realistic fixed 320px sample and explicit participant-authored font size. Add mutation checks for a forced non-wrapping label and detached count; retain RC151 inventory as historical, promote RC152 as current and synchronize release docs. Runtime unchanged. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full GitHub CI and external acceptance pending; no assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC151 — Robust strict-type preflight handoff

**RC151 cumulative after committed RC150:** fix the RC115 negative-mutation preflight failing in run `41706075530`: extracting the live `Pick` fields and verifying mutations are non-no-op guards against both missing permissions and append-only type changes. Added RC151 tests, preserved historical RC150 receipt, synchronized CI and four active release headers; no runtime edits. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full GitHub build, browser and external approvals pending. No assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC150 — TypeScript build hotfix for widget history

**RC150 cumulative after committed RC149:** fix two TypeScript TS2339 errors in GitHub Actions run `41700222536` by adding `position` and `resultTopCount` to editor history through a typed `Pick` from the canonical `PageDesign.widgets`. This preserves all saved widget state and operations. Added regression checks, synchronized status headers and generated a new inventory, while keeping RC149 history immutable. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full npm build and integration CI still require the next GitHub run. No assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC149 — Device-aware background contract CI regression

RC149 after committed RC148: GitHub Actions run `41690976927` stopped in the historical RC110 background upload contract. That contract matched only the older unconditional desktop `backgroundAssetId` binding and two-argument upload call, while current editor intentionally routes phone background selection and upload independently. RC110 checks now require the desktop fallback and isolated phone branch, with negative regression mutations. Runtime editor code is unchanged. RC148 historical manifest remains immutable. Local CI validation does not substitute for npm, browser or external acceptance. **Certified 85.25%** (43 accepted / 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC148 — Device-aware Undo history and CI handoff

**RC148 after committed RC147:** address CI run `41688028731`: the RC117 preflight incorrectly required the desktop-only callback in phone mode. New source contract enforces phone isolation, atomic Undo and stale-fit protections; additional RC148 preflight and current inventory. No editor runtime changes; RC147 immutable historical receipt maintained. **Certified completion remains 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full GitHub CI/browser acceptance pending. See `docs/RC_CYCLE148_ATOMIC_UNDO_CI_PRECHECK.en.md`. No assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC147 — Portable source archive and CI inventory handoff

**Cumulative RC147 after RC146:** fix clean-checkout checksum failure from run `41678059398`: generated Python caches can no longer enter cumulative packages or active inventories; historical RC146 receipt preserved unchanged, four active headers synchronized, and verification now covers Git index parity and inherited bytecode. **Certified completion remains 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Details: `docs/RC_CYCLE147_CI_INVENTORY_REPRODUCIBILITY.en.md`. Full CI not yet confirmed, no assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC146 — Complete CI release metadata handoff

**Cumulative RC146 after RC145:** exact fix for GitHub Actions `41674561888` release-header gate: synchronized active release headings and completion metadata in the four English/Italian status/handoff files; historical release notes and immutable RC145 receipt retained. Added a dedicated release-header regression test, made RC145 historical and RC146 current in CI. **Certified completion remains 85.25%** (43 accepted / 17 partial): `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Earlier RC145 mobile background and Arial changes are retained; no change to runtime behavior. Details: `docs/RC_CYCLE146_CI_RELEASE_HEADER_FIX.en.md`. Local validation only; full CI and external acceptance pending. No assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC144 — Independent smartphone layouts and 0–9 rating parity

**Cumulative RC144 after RC143:** ten-slot rating 0–9; portrait 390px phone editor, per-page mobile geometry and optional separate background; real participant and rehearsal parity without forced tiny scaling; mobile draft saved with collaborative CAS and secure active-slide asset access; explicit Arial default. **Local evidence:** 821/821 Node tests, 22/22 focused legacy Python cases, 6/6 RC144 Python contracts and Chromium CSS preflight at 1225px and 390px. **Certified completion remains 85.25%** (43 accepted / 17 partial): `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full Python sweep timed out; Vite production TypeScript compilation blocked by absent local `vite/client` package; GitHub CI, real devices and external approvals pending. No assistant commit/push/release. Details: `docs/RC_CYCLE144_INDEPENDENT_PHONE_RATING_FONT.en.md`.

---

# Quorivio 0.1.0-dev — RC143 — Formatting window, ranked results and scaled smartphone stage

**Cumulative RC143 after RC142 TypeScript hotfix:** floating format window closes visibly and exposes all controls; linked Result widget shows a configurable stable top 5 (1–20) with wrapped labels and attached counts; smartphone rehearsal scales the 1280×720 desktop stage as one unit with no page background image. Details `docs/RC_CYCLE143_RIBBON_CLOUD_MOBILE_PARITY.en.md`. Existing RC142 hotfix retained. **Certified 85.25%** (43 accepted / 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full npm/Vite CI and actual phone acceptance remain pending; no assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC142 — Cross-page clipboard, mobile preview and footer styling

**RC142 cumulative after RC141:** copied widgets persist across page switches within the same session, Backspace/Delete works on selection, formatting supports vertical alignment and independent footer number styling/padding (default 5 px), reactions and rating button sizes, a responsive smartphone preview from dashboard/editor and a participant device toggle in side-by-side preview, and a fully visible top ruler. Details: `docs/RC_CYCLE142_EDITING_MOBILE_FOOTER.en.md`. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. This is local validation, not a GitHub CI success; no assistant commit/push/release.

**CI correction:** Run `41624931068` failed at frontend `tsc` (`TS2353` and `TS2304`); RC142 hotfix corrects Footer CSSProperties and shared clipboard paste button. Full CI pending.

---

# Quorivio 0.1.0-dev — RC141 — Shared reaction/choice visuals and resilient results

**RC141 cumulative after committed RC140:** fixes RC140 TypeScript errors and adds replaceable 0–10 ratings (one DB row), a default-off results-only option, atomic result/count rows, automatic live-result fit, shared eight-emoji reactions, and aligned multiple-choice editor inputs. Local checks must still be corroborated by GitHub CI and a real deployment. Details: `docs/RC_CYCLE141_WIDGET_RESULTS_RATING_PARITY.en.md`. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC140 handoff

**RC140 committed** (commit `2612d704ac9ea886a3770e7eab9148a3f2186876`); GitHub CI run `41501239826` failed at TypeScript build on five nullable `toolbarRange` accesses, one implicitly typed text mark and four answer-style property assignments. This corrective cumulative retains the RC138–RC140 widget and formatting changes and fixes those compile-time types without changing their behavior. The complete 221-test frontend Node suite and strict standalone TypeScript check for `widget-text-marks.ts` pass locally. Full npm/Vite build and browser acceptance still require GitHub CI because the local offline npm cache is incomplete. Details: `docs/RC_CYCLE140_FORMAT_SCOPE_PARITY.en.md`. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC139 handoff

**Baseline: RC137 committed and CI-green** (run `41475936282`), **RC138–RC139 cumulative remains uncommitted**. One visual 0–10 rating control is now reused on editor/rehearsals/presenter/participant, editor double heading removed, text cursor/selection respects pointer events, and the formatting ribbon closes without deselecting a widget. Uniform internal padding replaces the old editor-only right gutter; no change to authored widget coordinates. RC139 documentation: `docs/RC_CYCLE139_RATING_CARET_AND_CANVAS_PARITY.en.md`. **Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. GitHub CI and real browser verification pending; no assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC138 — Intentional widget layers, result widget fidelity and Kubernetes inspection

Baseline: **RC137**, GitHub CI `41475936282` green, commit `4b33e67ec2ee22973b557ab3ec6759bad356dedc`.

- All widgets can overlap intentionally via mouse, touch, keyboard, copy/paste, and eight-edge resizing. The canvas bounds still apply and Undo/Redo remains functional.
- Results live in their authored slide widget on the presenter screen, showing aggregates only; participant projections never render results or mirror participants' inputs into the presenter answer fields.
- Results now offer an auto-resize/scale toggle. Manual resizing disables scaling, maintaining chosen text/chart size and allowing scrolling within the widget, without a misleading downscale indicator.
- Presenter/participant rehearsal uses intrinsic submit-button width, matching the authored editor layout.
- Short free-text answer frequency data are aggregated into anonymous 1–2 word labels (max 48 characters); long responses contribute only to counts.
- The wizard accepts `--inspect-cluster` with `--output` and `--set namespace=... --set name=...`, writing a nonsecret read-only cluster inventory to `quorivio-cluster-discovery.json`. It does not read Secret values, mutate Kubernetes, or regenerate credentials in inspection mode. It is a discovery foundation **not** an auto-apply or complete reconciliation feature; never apply full generated installation manifests to an existing cluster without manual approval and Secret/PVC preservation.

CLI example: `python3 tools/k8s_wizard.py --inspect-cluster --output ./quorivio-inspection --set namespace=quorivio --set name=quorivio`.

**Certified 85.25%** (43 accepted / 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. RC138 remains uncommitted with new GitHub CI and independent acceptance pending. No assistant commit/push/release.

---

# Quorivio 0.1.0-dev — RC137 handoff — Private presenter projection and canvas upload (2 November 2026)

**RC135 ultima baseline CI completa verde** (`41437489546`); **RC136+RC137 committati** (`f2dd75030c07e3d948b14b2ec4c51e9c2cf9e34a`), ma la CI `41473679963` ha fallito in `tsc` su un test Node sotto `apps/web/src`. Hotfix: test trasferito in `apps/web/test` (già eseguita dalla CI), senza modificare il codice applicativo. Risposte partecipanti isolate da widget e domande sullo schermo reale e nella prova affiancata; risultati e statistiche mostrati soltanto su richiesta esplicita del presentatore. Migliorata segnalazione del motivo HTTP del fallimento nel caricamento background e compatibilità MIME JPEG, senza bypass di antivirus o controllo formati. Nuovo preflight RC137; CI GitHub hotfix da verificare dopo la correzione. **Certificato 85.25%** (43 accepted /17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Dettagli in `docs/RC_CYCLE137_PRESENTER_PRIVACY_BACKGROUND.en.md`. Nessun commit/push/pubblicazione.

---

# Quorivio 0.1.0-dev — RC136 handoff — Independent acceptance workflow (2 November 2026)

**Committed and full-CI-green baseline: RC135**, GitHub Actions run `41437489546`, commit `6c1118e93076c5d2eb8d60e96a43f8c663178053` (17 jobs passed, explicit multiarch publication passed). **RC136 is a local cumulative review-tool improvement; no commit/push/release is performed.** Added 17-gate offline evidence packets, automatic SHA-256 attachment import and verification, commit binding, independent reviewer fields, missing-facet detection, documented IT/EN review workflow, new automated contract tests, and strict RC gate that cannot be satisfied by changing ledger statuses alone. Existing product runtime and approved RC135 CI baseline remain unchanged. **Certified 85.25%** (43 accepted /17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Only independent real-world signoffs can unblock formal RC; CI RC136 still pending. See `docs/RC136_EXTERNAL_ACCEPTANCE_EN.md` and `docs/RC136_EXTERNAL_ACCEPTANCE_IT.md`.

---

# Quorivio RC135 handoff — legacy editor contract CI repair

**RC134 committed, CI failed:** GitHub run `41435798792`, commit `3c75a548b277d179db49f1293fef3d5da5926f8b`; one RC89 source assertion still matched a removed editor label, so no application build or browser gates ran. **RC135 is the new local, uncommitted cumulative starting from committed RC134**, preserving all RC131–RC134 changes. Updated legacy checks for the actual free-answer label (typographic apostrophe), native disabled presenter answer choices, manual resize autoFit logic and pointer slider guard. Added early Python CI checks and a new SHA-256 source inventory; no production app changes. See `docs/RC_CYCLE135_LEGACY_CI_EDITOR_CONTRACTS.en.md`. Last verified green GitHub baseline RC130, run `41420021082`. **Certified 85.25%**, 43 accepted/17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. GitHub CI still unverified for RC135; no assistant commit/push/release.


**RC135 local verification:** 1,689 Python tests (1,688 passed, 1 skipped, 0 failures); 209/209 frontend Node tests; no TSX/TypeScript parse errors. Source/ZIP SHA-256 inventory validated. npm/Vite compilation and GitHub CI remain unverified.
---

# Quorivio RC134 handoff — presenter question/answer UI fidelity

**Committed CI-green baseline RC130:** workflow `41420021082`, commit `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d`. **Uncommitted cumulative RC131–RC134:** collision-safe mouse/keyboard movement and resizing, authored participant typography, and corrected real presenter projection of read-only answer fields, choices and disabled submit buttons with topic-question rehearsal parity and a mobile 16:9 CSS fix. See `docs/RC_CYCLE134_PRESENTER_QUESTION_PARITY.en.md`. Local Node 209/209, Chromium CSS 1440/390 PASS; TypeScript syntax PASS, npm/Vite and GitHub CI pending. Certified **85.25%** (43 accepted/17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Do not claim external RC acceptance, no assistant commit/push/release.

# Quorivio RC133 handoff — collision-safe eight-edge resize

**Committed baseline RC130:** GitHub `41420021082` green at `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d`. **Uncommitted cumulative RC131–RC133:** continuous drag collision/participant font (RC131); keyboard movement and answer-height accessibility (RC132); eight-edge pointer and Shift+arrow widget resize now stop at first contact instead of bouncing (RC133). See `docs/RC_CYCLE133_BOUNDARY_RESIZE_PARITY.en.md`. Node 209/209 and targeted Python 11/11 pass locally. Full GitHub validation pending; certified score **85.25%** (43 accepted/17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Do not claim external RC acceptance; no assistant commit/push.

# Quorivio 0.1.0-dev — RC132 handoff: keyboard-safe layout and answer field height (2 November 2026)

**Committed baseline RC130:** GitHub `41420021082` green at `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d`. **Still uncommitted RC131–RC132 cumulative work:** continuous collision-safe widget pointer movement and audience font parity (RC131), keyboard nudge first-contact limit and accessible vertical text-answer height slider (RC132). See `docs/RC_CYCLE132_KEYBOARD_COLLISION_AND_ANSWER_RESIZE.en.md`. GitHub full CI pending; current audited gate score **85.25%** (43 accepted /17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/release by assistant.

# Quorivio 0.1.0-dev — RC131 handoff: continuous drag and audience font parity (2 November 2026)

**Committed and CI-green baseline:** RC130, GitHub run `41420021082` at `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d` (quality, native browser/PostgreSQL, Kubernetes, native AMD64/ARM64 and authorized Docker Hub publication green). **Uncommitted RC131:** analytic first-contact collision stopping even for extremely thin barriers; group/diagonal preservation; participant 16:9 rendering honors authored fonts despite legacy mobile CSS; isolated Chromium four-surface geometry/typography regression at desktop and mobile. `docs/RC_CYCLE131_CONTINUOUS_DRAG_AND_AUDIENCE_PARITY.en.md` records limits and tests. **Certified 85.25%, 43 accepted/17 partial**. Strict external sign-off not complete; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. The next CI has not validated RC131 yet.

**RC131 local verification:** 1,677 Python tests (1 skipped, zero failures), 192/192 frontend Node tests, Chromium stage fidelity PASS at 1440/390px, TSX syntax diagnostics 0. Full build and GitHub CI still pending. 

---

# Quorivio 0.1.0-dev — RC130 — Authenticated Chromium editor reentry and JPG/Logo acceptance CI fix (2 November 2026)

**RC130 CI update (GitHub run `41417000544`, commit `b6e3f2e0181478682beaa9b06e2831d9b4decaa3`):** RC129 passed the browser reload regression and reached real PostgreSQL JPG background/Logo acceptance, where the shared `open_editor` helper still tried to click a dashboard `Apri sessione` behind the already restored editor. RC130 now checks the exact tab-local session/page identifiers, confirms the session title and page with authenticated PostgreSQL API, and asserts that the restored editor, selected thumbnail and canvas are visible. First-time session opening remains unchanged; mismatched recovery fails closed. Both real browser acceptance scripts use the same recovery check after reload. Added five dependency-free executable regression cases to the early CI preflight. No force-click, mocked HTTP in actual browser acceptance, production UI changes, Docker publication or relaxed gate.  Local full-suite reruns exposed a 5-second subprocess timeout in the RC125 fake-Docker simulation under parallel host load; its isolated security assertions passed. RC130 raises this **test harness** timeout to 15 seconds without changing Docker publisher logic or acceptance checks. Live Chromium/media persistence acceptance and complete GitHub CI must still be rerun after commit. **Certified completion 85.25%**, 43 accepted / 17 partial. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Local RC130 verification:** full Python suite 1,674 executed, 1,673 passed, 1 skipped, 0 failures (after increasing the fake-Docker subprocess test timeout). Five RC130 regression cases passed. Frontend application code unchanged; real GitHub Chromium/PostgreSQL acceptance and full CI remain pending.

# Quorivio RC129 — Chromium editor reload acceptance handoff

**RC129 CI evidence:** GitHub workflow `41389141345` failed at the Chromium editor UI test after reload: the restored editor's selected thumbnail intercepted a stale dashboard `Apri sessione` click. This is expected protection, because RC128 deliberately restores the authenticated page. The Chromium test now waits for the restored editor and requires its active thumbnail, exact four saved widgets, session and page continuity. New early CI regression tests cover this, preserving real pointer safety and strict release flags. The real browser and full GitHub gate remain unverified on RC129. **Certified completion 85.25%**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Current local hotfix verification:** Full Python suite 1,666 tests: 1,665 passed, 1 skipped, 0 failed; 185/185 frontend Node tests passed. Corrected RC89, RC91 and RC124 legacy source contracts; app logic, Docker publication and current release gate scoring unchanged. GitHub still requires a fresh successful run. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.


**RC128 CI smart-guide regression hotfix (GitHub run `41387175909`, commit `3c01b88f994cd28d88c43330170dc21a737e4109`):** The release-header preflight passed, but RC124 source-contract preflight failed 2/4 assertions because it still expected drag-on-collision to revert fully to origin and the older alignment-guide expression. RC128 deliberately stops dragged widgets at the first collision boundary and only draws magnetic guides if the proposed snap is reachable. Updated `tools/tests/test_rc124_smart_guides.py` to require actual first-contact sweep and no-tunnelling guards, guide visibility at the accepted snapped position, and the RC128 Node regression suite in CI. Full-suite checks also identified outdated RC91 footer font-unit and RC89 free-text presenter-label assertions; both now validate the current authored typography and read-only presenter submit controls. No production widget geometry or release-security logic was changed in this hotfix. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. GitHub full CI and live browser visual parity must still be rerun on the corrected commit.


Source cumulative includes RC127 native OCI runtime and 17 external gate acceptance checklist. New RC128 fixes: presenter's free-text preview shows the disabled real submit button, not simulated answers; shared logical slide geometry/fonts in single and split rehearsal; a draggable free-text field-height handle in editor; full horizontal ruler; per-tab authenticated workspace/session/page recovery; collision-constrained widget dragging with first-contact stopping. Tests: 185/185 frontend Node pass, 5/5 RC128 Python pass. Syntax checked; npm/Vite build, live Chromium visual checks and RC128 GitHub CI not yet validated. See `docs/RC_CYCLE128_EDITOR_PREVIEW_RECOVERY.en.md`. Certified release gate remains 85.25% (43/60 accepted, 17 partial); strict RC not accepted. No push/publication. Suggested cumulative commit since confirmed RC126: `Add native OCI runtime gates and fix editor-preview parity, reload recovery and collision boundaries [full-ci]`.

GitHub run `41385372942` failed the early release metadata preflight before compiling or running the app. Current release safety flags are explicitly `rc_strict=false`, `publish_image=false`, `publish_latest=false`. They are documentation-only declarations, not workflow switches; no publication was authorized.

---

# Quorivio 0.1.0-dev — RC127 — Real native ARM64 runtime and external RC acceptance plan (2 November 2026)

**Verified GitHub baseline:** run `41377221623`, commit `d5cff85367a8e906d6e0d59a41ecf82477245b99`: all RC126 full CI jobs completed successfully, including separate native AMD64/ARM64 builds and Docker Hub `latest`/`sha-d5cff85367a8` publication. **RC127 local development:** replace the QEMU-based ARM64 OCI *runtime* test with independent native ARM64 and AMD64 runners, disposable PostgreSQL 18, CPU/UID/runtime and HTTP/CSP probes. Added a deterministic action plan for the 17 outstanding external gate approvals. No operator evidence is fabricated. **Local RC127 Python suite: 1,661 tests passed (1 skipped)**; source/archive inventories verified. Native Docker runtime/Node/TS/GitHub CI for RC127 still require the next run. See `docs/RC_CYCLE127_NATIVE_RUNTIME_AND_EXTERNAL_ACCEPTANCE.en.md`.

**Certified completion: 85.25%** (43 accepted / 17 partial, 60 gates); provisional local estimate 85.75%. **Strict RC not ready** without independent review. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push or release performed. **Suggested commit after RC126:** `Run native ARM64 and AMD64 OCI runtime acceptance and track external RC approvals [full-ci]`.

---

# Quorivio 0.1.0-dev — RC126 — CI regression compatibility with native Docker pipeline (2 November 2026)

**Actual GitHub result:** run `41371521619` at commit `d0aa86bd9efe12180e418344aabd9255e5056a3a` completed **failure**. Production quality gate passed TypeScript/Vite build, real PostgreSQL/Chromium checks and ClamAV, then failed in the late Kubernetes wizard/worker Python suite: 8 obsolete CI-workflow assertions out of 1,656 tests (1,648 passing). The final RC campaign summary failed as a consequence; Docker native image jobs were skipped (not executed). This is not evidence of a repeat QEMU hang or a completed Docker Hub publication.

**RC126 change:** update seven historical Python test suites containing eight obsolete expectations about single-job Docker build/tagging and legacy release job names. Assertions now inspect parsed GitHub Actions job boundaries, verify manual opt-in vs explicitly marked `[publish-docker]` push, require the full RC campaign for commit publication, preserve image-build/Trivy prerequisites, and prohibit credentials/publishing in rootless Podman smoke. Keep real `linux/amd64` and `linux/arm64` runners and fail-closed manifest checks from RC125 untouched. Run these eight suites in the early pre-npm preflight, alongside existing RC125 native digest failure tests; late full suite remains mandatory. See `docs/RC_CYCLE126_CI_NATIVE_PUBLISH_CONTRACTS.en.md`.

**Evidence:** 57 targeted tests executed locally: 56 passed, one environment-dependent skip, historical receipts and current SHA-256 inventory verified. A local attempt at the entire Python suite exceeded the execution limit; this is not a full-suite pass. The revised GitHub workflow, Docker Hub authentication, actual native ARM64 push and manifest still require GitHub execution. **Certified product completion: 85.25%** (43 accepted / 17 partial out of 60); engineering estimate **85.75%** remains provisional. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push, Docker publication or release by assistant.

**Suggested commit after confirmed RC125:** `Align legacy CI contracts with native multiarch publication and gate both digest builds [full-ci]`.

---

# Quorivio 0.1.0-dev — RC125 — Native multiarch Docker publication (2 November 2026)

**Root cause:** GitHub Docker Hub job `41361426087/attempts/2` reports `qemu: uncaught target signal 4 (Illegal instruction)` during ARM64 `npm install`; AMD64 finishes successfully. **Fix:** separate native Ubuntu AMD64 and ARM64 GitHub runners, push by digest only, validate both architectures and assemble/tags the manifest in a later protected job. Per-platform 35-minute and manifest 10-minute timeouts; no implicit publishing with `[full-ci]`. All previous authorization and CI acceptance conditions are retained. See `docs/RC_CYCLE125_NATIVE_DOCKER_PUBLISH.en.md`.

**Evidence:** local workflow contracts and simulated Docker failure-injection PASS. Native hosted ARM64 build, authenticated Docker Hub push and final registry index **not yet verified**. **Certified completion: 85.25%** (43 accepted, 17 partial gates / 60). RC124 provisional **85.75%** engineering estimate remains unpromoted. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or publication.

**Cumulative commit since RC122 (RC123–RC125):** `Fix native multiarch Docker publication and improve editor media uploads and magnetic grid guides [full-ci]`.

---

# Quorivio 0.1.0-dev — RC124 — Smart alignment guides and absolute grid (2 November 2026)

**CI baseline:** RC122 run `41350047731`, all 11 automatic campaign jobs succeeded; overall run was cancelled due to a stuck Docker publication. RC123 cumulative has not been committed yet.

**RC124 functional work:** transient independent-axis magnetic alignment guides for page and master/scheme editing, visible absolute 5% grid and correct group bounding-box snapping, collision rejection, pointer transparency and no persisted guide state. See `docs/RC_CYCLE124_SMART_GUIDES_AND_GRID.en.md`.

**Certified completion: 85.25%**, 43 accepted and 17 partial gates out of 60. **Local engineering estimate: 85.75% (+0.50 provisional)** only if the proposed narrow A1-SMART-GUIDES subgate passes the full CI and is formally accepted; the certified ledger is unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Cumulative commit RC123–RC124:** `Unify safe editor image uploads, bound Docker publication, and add PowerPoint-like alignment guides with absolute grid snapping [full-ci]`. No commit, push or publication by the assistant.

---

# Quorivio 0.1.0-dev — RC123 — Editor media lifecycle and bounded Docker publication (2 November 2026)

**Verified baseline:** GitHub run `41350047731`, commit `a97b80b8d09ebd1a6054111bf88326581e2cc80f`: **11/11 automatic RC jobs passed**, but the overall run ended cancelled because its Docker publication job stalled. Automated quality is verified; Docker Hub publication is not.

**RC123:** unify safe filename-based MIME fallback for five editor media flows (Logo, backgrounds, asset library, fill images, converted image import). Add real browser file-chooser + disposable PostgreSQL persistence acceptance to CI, not yet GitHub-certified. Bound the explicit `[publish-docker]` job to 45 minutes while `[full-ci]` remains non-publishing. Details: `docs/RC_CYCLE123_MEDIA_PICKER_AND_PUBLISH_BOUNDARY.en.md`.

**Certified completion:** **85.25%**, 43 accepted / 17 partial gates of 60; unchanged pending GitHub confirmation. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, release or external publication.

**Suggested commit since RC122:** `Unify safe editor image uploads and bound authorized multiarch Docker publication [full-ci]`.

---

# Quorivio 0.1.0-dev — RC122 — Historical browser and handoff acceptance recovery (1 November 2026)

**Previous full CI:** `41347115255`, commit `993189dd67cd555825afdbbf77e7352e5148cde4`, passed frontend compilation, compiled Chromium and real PostgreSQL browser including JSON export. The late Python suite reported only two historical contract mismatches: mandatory adjacent browser command lines (new conflict visibility preflight sits between them) and an 85.25% score search limited to first 1,300 characters.

**RC122:** update those two historical tests to validate preserved browser execution ordering within the same PostgreSQL acceptance step and current ledger score in the full active handoff section. Preflight invokes both historical suites and five new positive/negative tests ahead of npm, without bypassing the late Python suite. No application behavior changes. All earlier receipts and regressions remain.

**Certified completion:** **85.25%**, 43 accepted, 17 partial of 60, unchanged; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. GitHub RC122 full CI pending; no assistant commit/push/publication.

**Suggested commit since RC121:** `Align historical browser ordering and handoff progress checks with current CI contracts [full-ci]`.

---

# Quorivio 0.1.0-dev — RC121 — Safe page-draft JSON export (1 November 2026)

**Previous full CI:** GitHub Actions `41341765759` at commit `494416c3cc3c20db6c3da6330ba69d42df51196c` passed the React/TypeScript build, early Chromium editor acceptance, PostgreSQL audience tests, and the real editor's autosave/conflict/merge flow, then failed on `page.expect_download()` in `tools/ci_browser_editor_postgres.py`. The downloaded failure artifact reported `JS errors: ['invalid_draft_value']`; the page-thumbnail context menu remained open with no export. Downstream RC jobs were skipped.

**RC121 fix:** the export path now removes `undefined` *optional object properties* from in-memory widget models before strict validation and JSON serialization, for both the draft and its baseline. Required page fields are still validated; array holes, non-finite numbers, unsupported values, cyclic objects, duplicate widget IDs and prototype pollution remain rejected. Exports do not mutate live editor state and keep the v2 format and revision/merge invariants. A failed export leaves the menu open with an accessible error instead of a silent click. Five API Node regressions and five Python preflight contracts were added. The full PostgreSQL browser test still requires an actual downloaded JSON file and its original `format` and `base_revision` assertions.

**Certified completion:** **85.25%**, 43 accepted and 17 partial gates out of 60, unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. RC121 full GitHub CI is pending; no assistant commit, push or publication.

**Suggested commit since RC120:** `Handle optional widget props safely in page draft JSON exports and preserve strict backup validation [full-ci]`.

---

# Quorivio 0.1.0-dev — RC120 — Visible editor revision-conflict status (1 November 2026)

**Previous CI:** GitHub Actions `41338170505`, commit `273196b30ab24f0e71d198c1dda1a75f24a08023`, passed TypeScript build, initial Chromium editor acceptance and Chromium PostgreSQL audience acceptance. It failed at `Chromium editor PostgreSQL persistence and conflict acceptance`: the text `Conflitto di revisione` existed in the DOM but was not visible. Dependent campaign jobs were skipped.

**RC120 fix:** the actual CI DOM shows the preview toolbar flex layout shrinking the conflict status until it becomes visually clipped. The status now has a non-shrinking readable width; on narrow screens error status is positioned directly below the header, without disabling conflict detection, PostgreSQL version checks or reconciliation. Conflict styling applies whenever `pageConflict` is true, even without a separate save error. Chromium regression uses the production stylesheet at widths 1440, 1100, 960 and 390 px; existing real PostgreSQL conflict visibility and merge checks remain mandatory.

**Certified completion:** **85.25%**, 43 accepted and 17 partial gates out of 60, unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full RC120 CI not run yet. No assistant commit, push or publication.

**Suggested commit since RC119:** `Prevent editor revision conflict status from collapsing and test real Chromium visibility [full-ci]`.

---

# Quorivio 0.1.0-dev — RC119 — Content-only autofit and stable group duplication (1 November 2026)

**Previous CI:** GitHub Actions `41336263788`, commit `68b82e3846e1ba62db28495ecc431b09c49ab0b5`, passed release documentation checks and React build, then the Chromium editor test reported 3 widgets after group duplicate (expected 5). The attached browser screenshot shows short text widgets extended to the bottom of the canvas. Downstream RC jobs were skipped.

**RC119 root cause and fix:** the auto-fit effect used the outer widget `scrollHeight`, including resizing controls extending past its borders; this triggered repeated layout expansion for short labels and exhausted collision-free duplication room. Auto-fit now measures inner content scroll height versus its bounded frame, explicitly excluding resizing chrome. The Chromium test checks short-fixture geometry before duplication and asserts immediately on native placement-rejection dialogs, retaining exact two-widget selection, five after duplication and three after one Undo.

**RC certification:** 85.25% (43 accepted, 17 partial / 60), unchanged; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full GitHub CI including real compiled React/Chromium is still required. No assistant commit/push/publication.

**Commit suggestion since RC118:** `Prevent resize handles from causing runaway widget autofit and restore Chromium group duplication [full-ci]`.

---

# Quorivio 0.1.0-dev — RC118 — Localized release-documentation preflight correction (1 November 2026)

**Verified status:** RC117 full CI GitHub Actions run `41332909058` (commit `90cef44a8e32cca63c08b9d9e6374e100ff4284b`) failed early on historical documentation checks: four tests require the decimal-comma Italian percentage `85,25%` but the RC117 active Italian headers used `85.25%`. Frontend compilation and the Chromium editor tests did NOT run, so the previous Undo bug remains unverified end-to-end. ClamAV passed.

**RC118 fix:** current localized release headers now display the certified score **85,25%** in Italian and **85.25%** in English. The early `verify_rc_release_status.py` guard computes the score from the actual `RC_GATE_MATRIX.json` ledger through `rc_gate_audit`, and verifies exact locale-specific percentages in the CURRENT sections only. Negative tests reject missing scores, stale scores, and wrong decimal separators; the existing flags and exact cycle verification remain. The audit ledger is untouched: 43 accepted and 17 partial gates out of 60.

**Further full-suite regression repairs:** the historical browser-contract test now checks the exact accessible selection helper instead of two obsolete `.check()` calls; Chromium requires Shapes and Lines in the palette and rejects legacy Separator. Strict 5→3 widget counts, selected accessible rows and one-step Undo remain mandatory.

**Limitations:** GitHub full CI, especially real Chromium group duplication / single Undo / Redo, remains to be verified. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, Docker publication, or promotion to final RC.

**Suggested commit since RC117:** `Fix locale-specific RC completion headers and enforce ledger-matched release documentation [full-ci]`.

---

# Quorivio 0.1.0-dev — RC117 — Atomic auto-fit Undo (1 November 2026)

**Status:** RC116 full CI GitHub run `41330955017`, commit `086274a5725a6e8b5d852aabb9cab463057882d4`, compiled TypeScript successfully and created exactly 5 widgets after two-widget duplication, but a single Ctrl+Z left 5 widgets instead of restoring the original 3. ClamAV passed; downstream campaign jobs were skipped.

**Fix:** `WidgetCanvas` previously recorded DOM-computed `autoFit` layout corrections as independent user-edit history entries. The page editor now uses `reconcileWidgetAutoFit` to incorporate a derived geometry update into the same history step. It rejects stale-render updates, changed widget identities, and active pointer gestures. The real Chromium browser gate focuses a non-editable toolbar control before sending Ctrl+Z and keeps its strict count assertions: 5 after duplication, 3 after exactly one undo; no multi-undo masking. New Node tests assert duplicate -> auto-fit -> single undo -> redo and stale-effect rejection. A fail-closed RC117 source preflight runs before npm.

**Limits:** Full GitHub CI RC117 pending. Certified completion stays **85.25%**, 43 accepted/17 partial of 60; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or Docker publication.

**Suggested commit since confirmed RC116:** `Keep auto-fit adjustments in the originating Undo step and verify Chromium group undo [full-ci]`.

---

# Quorivio 0.1.0-dev — RC116 — Deterministic Chromium group selection (1 November 2026)

**Status:** RC115 full CI (GitHub run `41328071305`, commit `731bf6e0505f9431ae51abc46839437d31e2f155`) passed the API/frontend compile and early Chromium steps but failed in `ci_browser_editor.py`: a group duplicate yielded 6 widgets instead of the asserted 5. The aggregate campaign failure was downstream.

**Diagnosis and fix:** the browser acceptance test checked two boxes without unchecking a third widget potentially retained from earlier layer and undo actions. It now explicitly configures First/Second via real accessible controls, unchecks any other selection and checks both accessibility inputs and canvas selected IDs. The exact post-duplicate count of five, deletion confirmation, undo, collision and Chromium execution remain mandatory. A desynchronization fails with actionable diagnostics. No application duplication logic or expected widget count was weakened.

**Status:** certified product completion 85.25% (43 accepted and 17 partial of 60 gates), `rc_strict=false`. Full GitHub CI RC116 pending. No publication.

**Suggested commit since confirmed RC115:** `Make Chromium group-selection acceptance deterministic and retain strict duplication checks [full-ci]`.

**Release flag:** `publish_image=false`.

**Release flag:** `publish_latest=false`.

---

# Quorivio 0.1.0-dev — RC115 — Frontend strict TypeScript build hotfix (1 November 2026)

**Status:** RC115 cumulative from committed RC114; full CI RC114 failed in `Production quality gate` at the frontend `npm run build`. Early preflight, 567 API and 165 frontend tests had passed. Certified completion remains **85.25%** (43 accepted and 17 partial of 60 gates), `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Correction:** Explicitly type auto-fit/collision candidate arrays (TS7022/TS7006); include `showTitle` and `autoFit` in the editor's `PageDesign`-derived Pick (TS2339); narrow shape, line direction and stroke dash controls to `WidgetTextStyle` discriminated unions (TS2345). No API changes, validation bypass or weakened compiler checks. RC115 regression preflight, including negative mutations, executes before npm.

**Limits:** Local npm installation is unavailable because the registry cannot be reached (`EAI_AGAIN`); full TypeScript/Vite compile remains an obligatory GitHub CI gate. No commit, push, tag or publication.

**Suggested commit since RC114:** `Fix strict TypeScript inference for widget autofit, editor properties and graphic styles [full-ci]`.

---

# Quorivio 0.1.0-dev — RC114 — Editor CI preflight handoff (1 November 2026)

**Status:** RC114 cumulative local correction after the failed RC113 GitHub full CI on `6a51c67074a4dccb481e13516f4dc04601c2ada7`. Two legacy RC89 preflight assertions rejected intentional safer behavior: only dismiss background-upload context on confirmed success, and accept newly validated answer style keys. Five new negative RC114 assertions check that unsafe regressions still fail. RC113 historical SHA-256 catalog retained and RC114 is the only current inventory. Full CI has not yet verified RC114. Baseline RC107 full CI `41309042012` green; certified **85.25%** (43/17/60). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Next:** Push only after user commit. Run full CI via `[full-ci]`. If green, resume feature development and reconcile CI evidence without counting manual/independent acceptance automatically.

**Additional full-suite reconciliation:** A complete 1,607-test Python run found three further stale/graphic contracts: the canvas menu right-click expectation, Shift+Arrow resize now disabling auto-fit, and duplicated legacy Separator/Line icons. The old contracts are now updated to verify context hit-testing and collision-safe keyboard resizing; the obsolete Separator icon is removed from the insertable mapping, leaving unique icons for all 20 insertable widgets. The historical Separator remains supported in saved documents. RC114 includes two further negative/graphic regressions. The full suite must be rerun after packaging and in GitHub Actions.


---

# Quorivio 0.1.0-dev — RC113 — Inline editing, media upload, optional titles, fitted content, and graphic shapes/lines (1 November 2026)

**Certified baseline:** RC107 full CI `41309042012` SUCCESS, commit `99a801ab7623347ba776b8214d054aa872ddb5c6`, Docker Hub published. RC108–RC113 remain cumulative **uncertified local changes**. Version `0.1.0-dev`, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Certified completion remains **85.25%** (43 accepted/17 partial of 60).

**Editing and titles:** Double-click activates in-place text editing without launching Widget Properties. Properties remain available through explicit context-menu commands. `showTitle` defaults to true and is strictly validated; page/master properties expose the switch without removing saved text or semantic accessible names.

**Media:** Logo/Image uploads accept OS file-picker JPEG/JPG and supported MIME fallback, preserve server-side signature scanning, validate the returned media UUID, refresh the library, clear autosave blocked state and provide useful diagnostics rather than reporting an early missing attachment as upload failure. Background uploads are a separate flow and still require real browser/PostgreSQL verification.

**Content fitting:** Shared `WidgetContentFit` observes geometry and content and uniformly reduces visual contents to fit authored rectangles, without moving widget borders/handles. The editor displays a percentage status by Delete only when scaling is active. The accessibility reading mode is intentionally unscaled.

**Graphics:** New Shapes and Lines replace Divider in the creation palette, without deleting legacy divider data. Standard editable SVG polygons and four line directions support fill, outline, width, dash and color. Graphic widgets may overlap interactive widgets; collision rejection between ordinary widgets remains unchanged. Decorative overlays do not intercept live participant actions.

**Acceptance:** Node and targeted local checks and immutable SHA-256 manifest; GitHub full CI and real physical/user browser upload and resizing acceptance remain pending. Do not promote the certified gate percentage or announce a final RC. No commit, push, tag or publication performed.

**Cumulative commit since RC107:** `Complete grouped PPTX and editor workflows, fix asset uploads and inline widget editing, and add scalable graphic shapes and lines [full-ci]`.

---

# Quorivio 0.1.0-dev — RC112 — PowerPoint-style master editor, Footer and rulers (1 November 2026)

**Certified baseline:** RC107 GitHub full CI `41309042012` SUCCESS, commit `99a801ab7623347ba776b8214d054aa872ddb5c6`, Docker Hub published. RC108–RC112 cumulative changes remain **uncertified on GitHub**. Version `0.1.0-dev`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Certified completion stays **85.25%** (43 accepted, 17 partial of 60); no local-only promotion.

**Slide scheme editor:** RC105 selected-only border-box resize handles are now shared with the master canvas; Exit remains above overlapping content and receives pointer hits. The top PowerPoint-like ribbon groups Insert, Align, Distribute, Save, and a horizontal widget rail enables adding non-media widgets. Masters support up to 16 valid widgets; a single Title and Footer each plus multiple generic kinds. Persisted master widgets are inherited by page views, with result/source links remapped to inherited IDs. Media widgets (Image, Video, Logo, PDF) are shown in the master rail and enabled only when the session library contains a compatible authorized asset; their asset selection is editable in master properties.

**Configurable footer:** central session title vs custom label, font/size/bold/italic/underline/color, geometry, independent page-number visibility and placement within the Footer (0–100% in both axes), separator visibility and color. Existing footers retain the 10px lower-right number when custom coordinates are absent. React and native PPTX use the same customizable numbering, with strict API validation; numbers remain dynamic by slide order.

**Page editor rulers:** the same horizontal and vertical rulers displayed in the master are now visible around the normal page editor canvas, responsive on desktop/mobile while retaining 16:9 ratio.

**Evidence and limits:** Node API 567/567 and frontend 159/159 passing. Native Chromium CSS checks on 1440px and 390px verify selected-only handle positions, Exit hit target and page ruler. Generated PPTX checks cover custom number placement and suppression plus separator. Full React/Vite production build and authenticated end-to-end master-editor gestures still require GitHub full CI. No commit/push/tag/image publication.

**Suggested cumulative commit since RC107:** `Export grouped-question PPTX, improve interactive widgets and backgrounds, fix previews, and complete draggable slide schemes and configurable footer [full-ci]`.

---

# Quorivio 0.1.0-dev — RC111 — Rehearsal visibility, result text wrapping, scheme navigation (1 November 2026)

**Baseline:** RC107 GitHub full CI `41309042012` SUCCESS and Docker Hub publication, commit `99a801ab7623347ba776b8214d054aa872ddb5c6`. RC108–RC111 cumulative changes remain **uncertified on GitHub**. Version `0.1.0-dev` unchanged. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Presenter / Participant / Side-by-side preview:** The authenticated page editor sits in a fixed `z-index:9000` layer, while its body-portalled rehearsal backdrop was below it at 5000. All three buttons updated pressed state but displayed the modal under the editor. The global body rehearsal backdrop now stacks at 15000, above the editor and its draggable property/ribbon windows (12000). The modal keeps its existing focus trap, accessible dialog, click-away closure and page-specific unsaved preview state. A real Chromium CSS geometry regression checks hit testing above the editor at desktop and mobile widths; the compiled React rehearsal CI regression now checks actual topmost hit testing in addition to DOM presence. Full application acceptance still requires GitHub.

**Linked result widgets:** Previously the source question and long answer labels were forced into a single ellipsized line. They now wrap to the actual widget width in bar/table/cloud and other linked modes, break long unspaced terms safely and remain scroll-accessible when manually sized too short. Count values and chart tracks retain their semantics. CSS tests use native Chromium desktop/mobile viewports and verify multi-line text without horizontal overflow. Source data/aggregation is unchanged.

**Scheme editor discoverability:** Retain the global title/footer scheme canvas and concurrency-safe save. Add a dedicated `Editor degli schemi` link to the authenticated dashboard navigation for an open session and a `▤ Schemi` button in the fullscreen page-editor header, in addition to the existing `Modifica schemi` action above the thumbnail strip. Opening the scheme editor from the fullscreen page editor blocks navigation while autosave is pending to prevent data loss.

**Acceptance and limits:** Node API 565/565, web 157/157, RC111 contract tests and native Chromium CSS smoke tests pass locally. The npm offline cache is incomplete, so a fresh production React/Vite build and end-to-end application modal test must be verified by GitHub CI. Certified completion remains **85.25%** (43 accepted, 17 partial of 60); do not promote automatic or independent gates without evidence. No commit, push, tag or Docker publication performed.

**Suggested cumulative commit since RC107:** `Export grouped question PPTX, improve response inputs and footers, fix JPG backgrounds, word clouds and floating previews, and expose slide schemes [full-ci]`.

---

# Quorivio 0.1.0-dev — RC110 — Background JPG upload, ranked clouds and free-answer field sizing (1 November 2026)

**Baseline:** RC107 GitHub full CI `41309042012` SUCCESS and Docker Hub published, commit `99a801ab7623347ba776b8214d054aa872ddb5c6`. RC108–RC110 cumulative local changes are **not yet certified** by GitHub CI.

**Background upload fix:** The canvas context menu opens the system file picker and calls the authorized `/api/sessions/:id/backgrounds` raw-image upload. On success the returned session-scoped asset id is applied to the current page, background library is refreshed, and page autosave retains the ID. Errors no longer silently close the canvas menu: pending and failed upload states appear in the menu with `role=status`, and only a successful server response closes it. JPG, JPEG, PNG, GIF, WebP are accepted with MIME fallback for common platform file pickers. API remains fail-closed with size, image-signature, ClamAV and authorization checks. *The real OS-picker/JPG/PostgreSQL/browser end-to-end path remains to be certified in CI and deployment.*

**Word clouds:** Top five ranked words/options have five different accessible colors; ranks six onward share a neutral color. Count descending with stable alphabetical tie-break; deterministic, without mutating source data. Applied to presenter-linked results, widget results and moderated audience topic word cloud. Other chart modes retain original ordering.

**Free text response field dimensions:** New `style.answerFieldWidth` (25–100%) and `style.answerFieldHeight` (48–400px) can be set from the floating ribbon and widget Properties. Shared `answerInputStyle` applies to the actual participant textarea, rehearsal and canvas preview. Backend strictly validates integer ranges and disallows arbitrary CSS/HTML; existing documents with unspecified values use 100%/96px. This does not change submit-button size or manual outer widget resize. Auto-fit remains available where free layout space permits.

**Cumulative:** RC108 editable grouped-question PowerPoint and RC109 responsive answer controls/auto-fit/single-line footer remain included. Node API 565/565, web 157/157, RC110 targeted tests passed locally. The Python full suite did not complete within the available timeout, and integrated browser+real PostgreSQL upload is unverified. Version remains `0.1.0-dev` and the certified RC gate score remains **85.25%** (43 accepted, 17 partial of 60). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Commit/push/tag/publication not performed.

Suggested cumulative commit since the last confirmed RC107: `Export grouped question PPTX, improve editor answers and footer, and fix JPG backgrounds, cloud colors and response field sizing [full-ci]`.

---

# Quorivio 0.1.0-dev — RC109 — answer controls, auto-fit and single-row footer (1 November 2026)

**Baseline:** RC107 GitHub full CI `41309042012` SUCCESS; the maintained SHA `99a801ab7623347ba776b8214d054aa872ddb5c6` is published on Docker Hub. RC108 and RC109 are local cumulative changes **not yet GitHub-CI certified**.

**Editor and answer controls:** Questions, timed quizzes and audience-topic questions now show their real (disabled preview) Submit button on the edit canvas, including independent nested questions. Answer text boxes and options have independently configurable font family, font size, text color, bold and italic; the answer button font size (12–40 px) is configurable from the PowerPoint-like floating ribbon and the widget properties dialog. Shared style helpers apply in the authenticated participant surface, rehearsal and editor. Fields are validated strictly by the API and cannot smuggle arbitrary CSS or HTML.

**Auto-fit:** Eligible text/interactive widgets expand to fit their content by default after text, font, or answer-control changes. Growth is bounded to the 16:9 slide and uses the existing collision-rejection policy. A manual edge-resize or Shift+Arrow resize disables auto-fit only on that widget; a Properties checkbox reenables it. The algorithm never silently moves other widgets or writes outside the canvas. If the slide has no free space, content cannot be guaranteed to fit without manual rearrangement (deliberate fail-closed choice).

**Footer:** New footers use a 7%-height single-row strip starting at 93%, center the session title horizontally, add a subtle separator line above, keep transparent background, and preserve the independent 10 px lower-right page number. Previously saved custom geometries remain unchanged; legacy normalization still works.

**Previous cumulative RC108:** Native editable PowerPoint export of grouped questions and rich text with no answer-key disclosure remains included.

**Verification:** API Node 565/565; frontend Node 154/154; RC109 Python contracts and old footer/rehearsal contracts passed locally. Chromium real application and full CI remain to be verified via GitHub.

**Certified weighted completion:** 85.25% (43 accepted / 17 partial, 60 gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No additional gate credit without evidence. Suggested cumulative commit since RC107: `Export grouped questions to PPTX and improve editor answers, auto-fit and slide footers [full-ci]`. No assistant commit, push, tag or image publishing.

---

# Quorivio 0.1.0-dev — RC108 — grouped-question PowerPoint handoff (1 November 2026)

**Verified baseline:** RC107 GitHub full CI run `41309042012` **SUCCESS**, commit `99a801ab7623347ba776b8214d054aa872ddb5c6` on `main`; 11/11 automatic RC campaign jobs succeeded. Docker image `desalvo/quorivio:latest` was published for this commit. This is the new committed baseline. No assistant remote operations.

**RC108 functional development (local, pending CI):** native PowerPoint export now writes the entire visible content of grouped question/timed-quiz widgets, including up to five nested questions, labels, descriptions, individual options, and field-specific editable rich-text runs. UTF-16/Unicode formatting and explicit validation follow the API contract; invalid nested IDs, missing mark targets and oversized output fail before publishing a partial deck. Correct answer IDs and private answer keys are never exported in this public visual deck. Reimporting such a PPTX yields an **editable plain text widget**, NOT a reactivated multi-question quiz. Changing PowerPoint text does not change Quorivio quiz logic. Added 9 real-PPTX regressions to the post-dependency CI quality gate. Details: `docs/RC_CYCLE108_GROUPED_QUESTION_PPTX.en.md`.

**Certified weighted completion remains 85.25%** (43 accepted / 17 partial, 60 total). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. A green CI is necessary but does not replace independent device, privacy/accessibility, Office fidelity and operational sign-offs. New code receives no RC gate credit prior to external verification. Suggested next commit since RC107: `Export complete grouped questions and styled answers in editable PowerPoint slides [full-ci]`.

---

# Quorivio 0.1.0-dev — RC107 — ANSI-aware Vite preview CI readiness (1 November 2026)

The RC106 full CI in `logs_111954785384.zip` completed Chromium browser checks, but `ci_preview_proxy_guard.py` failed incorrectly with `compiled-preview readiness evidence is absent`. Vite's colorized terminal startup banner has ANSI sequences between `Local`, `:` and the URL. RC107 strips ANSI styling from a diagnostic copy of the log, preserves strict startup host/port checks and fail-closed socket/proxy diagnostics, and adds regressions using the reconstructed observed banner and negative failure fixtures. `docs/RC_CYCLE107_ANSI_PREVIEW_GUARD.en.md`.
**Certified gate-weighted readiness: 85.25%** (43 accepted, 17 partial / 60). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. GitHub push commit RC106 `6b5cd19230c8b68fe4ba852abbb6236b24c06a5a` is the confirmed baseline; RC107 only is new. No assistant commit/push/tag/publication.

---

# Quorivio 0.1.0-dev — RC106 — Chromium proxy and historical portal CI fix handoff (1 November 2026)

**RC106 handoff:** failed GitHub push full campaign `41305315027`, SHA `454eaf729c9487146f2c89a47178a64161d5683b`. The real blocking failure was one obsolete source-structure assertion in `tools/tests/test_editor_contextual_layout_v2.py`; updated to demand the RC105 draggable page-settings body portal. `ECONNREFUSED` in the Chromium job was an unreported Vite preview WS proxy failure (no API until later PostgreSQL phase). `preview.proxy={}` is now explicit, and `tools/ci_preview_proxy_guard.py` runs in the Chromium step `EXIT` trap and fails on proxy/socket errors or missing preview startup evidence, even if Playwright succeeded or failed earlier. Real API live/PG tests remain in the workflow. Test with `[full-ci]` and reconcile independently. Details `docs/RC_CYCLE106_CI_PREVIEW_AND_PORTAL.en.md`.
**Certified gate-weighted readiness: 85.25%** (43 accepted, 17 partial / 60). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No new gates credited, no final RC.
**Most recent maintainer commit:** RC105 SHA `454eaf729c9487146f2c89a47178a64161d5683b`, confirmed by push GitHub run; RC106 changes are new and uncommitted. No assistant remote mutations.

---

# Quorivio 0.1.0-dev — RC105 — floating windows and resize geometry handoff (1 November 2026)

**RC105 handoff:** selected-only, absolute eight-edge handle geometry; draggable viewport-constrained property/page windows; ribbon moved to a fixed portal outside canvas layout, preserving text selections. See `docs/RC_CYCLE105_FLOATING_EDITOR_AND_RESIZE.en.md`; new browser and Python contracts are integrated into CI. GitHub full CI and real loaded app drag acceptance remain pending.
**Certified gate-weighted readiness: 85.25%** (43 accepted, 17 partial / 60 total, total weight 100). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Final release is not approved.

**Maintainer commit baseline RC102:** `b3d753e06f6eca2bf771bae7699c65f9370ed399` (full campaign `41265300884` green). RC103, RC104 and RC105 are additive and not yet committed. Only the maintainer commits or publishes.

**RC104 handoff:** `tools/pptx_portable.py` now translates API-approved `textMarks` to/from native editable PowerPoint runs, including unicode offsets, field identity, style inheritance and validation. New integration tests `tools/tests/test_rc104_pptx_inline_text_roundtrip.py` are explicitly staged after pip deps in `.github/workflows/ci.yml`. Seven cases passed locally before packaging, plus native PPTX suite and RC103 QR tests. This is new uncredited functionality, not external certification. See EN/IT RC104 guides.

**Next maintainer step:** commit cumulative RC103+RC104+RC105 with `[full-ci]`, check CI standard/extended, validate PowerPoint and LibreOffice UI with an external representative deck corpus, then address independent residual gates. Docker Hub publication is not enabled by `[full-ci]`.

**Suggested post-RC102 message:** `Add participant QR PowerPoint export and editable rich-text PPTX roundtrip; reconcile thumbnail browser gate [full-ci]`.

---

# Quorivio 0.1.0-dev — RC103 — full CI evidence and PPTX participant QR handoff (1 November 2026)

**Certified gate-weighted readiness: 85.25%** (43 accepted, 17 partial / 60 total, total weight 100). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Do not declare final RC, independently certified accessibility/privacy or production publication.

**Committed baseline (maintainer):** RC102 SHA `b3d753e06f6eca2bf771bae7699c65f9370ed399`, full RC campaign GitHub Actions `41265300884` SUCCESS (workflow_dispatch, 2026-11-01; 11/11 mandatory jobs). Container publication was skipped. This RC103 package consists only of changes after that commit; no commit/push/tag/deployment/publication by the assistant.

**Evidence reconciliation +0.50 points:** native real-browser thumbnail reordering on compiled React passed Chromium, Firefox and WebKit (desktop 1440 and mobile-size 390). Firefox/WebKit quality job `124728693190` logs native HTML drag-and-drop, authoritative recovery after committed PUT response loss, rejected reorder and Alt+ArrowUp keyboard save. Chromium in quality job `124726769311`. New *disjoint* gate `A2-NATIVE-DND` accepted at weight 1, A2 residual partial weight 3 -> 2; A2-ORDER and A2-PAGE-JSON were already credited. Strict RC still blocked on independently reviewed visual fidelity, physical device and other parent gates. Receipt `docs/validation/RC_CYCLE103_NATIVE_THUMBNAIL_RECONCILIATION_20261101.json`; `docs/RC_GATE_MATRIX.json` is the source of truth.

**RC103 new functionality (LOCAL ONLY; zero acceptance credit):** PowerPoint export now renders each QR widget as a scannable PNG with a readable, editable, clickable participant URL below. The API supplies the canonical public join URL to the isolated converter only for decks containing QR widgets; reusable portable JSON export remains unchanged and does not persist the join credential. The worker includes pinned Python `qrcode==8.2`; malformed, missing, presenter or relative links fail closed rather than becoming misleading QR images. Exported QR decks are static: rotating/revoking the join token makes downloaded codes stale. 4 targeted native PPTX checks; complete GitHub API/export/worker integration and operator scan on a phone still need verification. No claimed fidelity for unrelated interactive widgets.

**Next closure:** get RC103 `[full-ci]` green (standard + optional browser PostgreSQL/cross-browser/container), then schedule external manual audit for physical devices, OIDC providers, public TLS/CSI RWX, accessibility, GDPR and production restore. Keep auto-publication disabled except explicit separately authorized `[publish-docker]` policy.

**Suggested single-line post-RC102 commit:** `Reconcile native cross-browser thumbnail gate and export participant QR links in PowerPoint [full-ci]`.

---

# Quorivio 0.1.0-dev — RC102 — editor context portal and commit-intent CI handoff (1 November 2026)

**Certified readiness: 84.75%** (42 accepted/17 partial out of 59). `rc_strict=false`, `publish_image=false`, `publish_latest=false` by default. Version remains 0.1.0-dev, EUPL-1.2.

**Source baseline:** RC101 cumulative archive, following last maintainer-confirmed RC100 commit `4930ee872798a70ad3ad92f907b647098d339adf`, GitHub standard run `41256022328` success. No assistant commit, push, tag or Docker deployment. All future suggested commits are cumulative only since RC100 until a newer commit is confirmed.

**Observed blocker:** `logs_111827641365.zip`, full opt-in Chromium editor acceptance fails `AssertionError: Canvas selection menu is covered by the editor header or another element`, at `tools/ci_editor_context_tools.py:85`, after numerous browser successes including the RC101 layout. No other independent failing acceptance is established from this log. RC campaign summary failed because its production quality dependency failed.

**Changes:** Portalled `.canvas-background-context` to `document.body`; fixed, viewport-bounded `.canvas-background-context-floating`, with Escape and outside-dismiss behavior. Added real pointer smoke fixture and unit contract tests. CI `push` main marker `[full-ci]` runs all automated RC opt-ins and summary. Marker `[publish-docker]` runs the same tests and then requires `validate`, `image-build`, and `rc-campaign-conclusion` all `success` before a protected `production` Docker Hub push. Tags: `sha-<12>` and `latest` from main; independent authorization script validates event/ref/repository/SHA/message and campaign result. Preserve manual workflow_dispatch publication and non-publishing manual campaign. Do not use `[publish-docker]` until explicitly intending to update `latest`.

**Next checks:** CI standard/extended GitHub on RC102, built React real editor Chromium and PostgreSQL, actual production publication only if explicitly requested. RC strict release remains blocked. GitHub/remote deployments unchanged by assistant.

**Suggested commit (recommended):** `Fix Chromium canvas context overlay and add gated commit CI modes [full-ci]`.

---

# Quorivio 0.1.0-dev — RC101 — Chromium horizontal editor rail hotfix (1 November 2026)

**Verified RC readiness: 84.75%** (42 accepted, 17 partial of 59). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Baseline:** RC100 confirmed on commit `4930ee872798a70ad3ad92f907b647098d339adf`, standard workflow `41256022328` successful. RC101 includes one layout remediation, one real-browser test modernization, a source preflight and supporting documentation/inventory. Next commit message must cover RC101 only; no push/tag performed.

**Observed extended gate:** the Chromium editor mock test in uploaded `logs_111825862452.zip` detected `sb y=900 height=16`, `rb y=78 height=822` at 1440×900; existing assertions still assumed the old right-hand rail. The middle grid row consumed all remaining height; end users could not see the slide. CSS now bounds the horizontal palette to 80px. Updated Chromium acceptance checks toolbar placement above the stage, slide visibility, 16:9, and horizontal scroll at desktop and touch viewports. Nine local browser checks passed; complete opt-in GitHub RC campaign and any checks dependent on npm are not certified.

---

# Quorivio 0.1.0-dev — RC100 — CI release metadata and package finalization hotfix (1 November 2026)

**Verified RC readiness: 84.75%** (42 accepted, 17 partial, 59 total). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Carry-forward handoff:** cumulative RC100 includes all RC96–RC99 fixes since the maintainer-confirmed RC95 commit. New RC100 changes: update the active header in all four docs to RC100; add the dynamic metadata guard `tools/verify_rc_release_status.py`; add negative regression tests that reject stale release headers; enforce the guard in standard CI before other unit and integration work.

**Observed failure:** RC99 standard CI artifact `logs_111823397377.zip`, Production quality gate, 4 failures out of 30 document tests (each file still headed RC98 despite current RC99 inventory). This happened before the rest of the pipeline. **Required next validation:** standard + extended GitHub CI on RC100, especially full Python suite and browser/runtime gates; current RC completion remains 84.75% without another accepted gate.

**Packaging invariant:** after assembling and hashing the cumulative source tree, extract the finalized ZIP to a fresh directory, run `verify_rc_release_status.py`, legacy RC96 release-status tests and the new RC100 tests, then verify source/ZIP SHA-256 catalogs. No remote actions were performed.

---

# Quorivio 0.1.0-dev — RC98 — TypeScript build hotfix after standard CI (1 November 2026)

**Verified RC readiness: 84.75%** (42 accepted, 17 partial, 59 total). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

The submitted standard CI `logs_111819994228.zip` (Production quality gate; observed commit `21505ad2541d5be6135ed84fc33697146cf75b8e`) passed earlier documentation and PPTX staging preflights but stopped in `npm run build` on four TypeScript diagnostics at `apps/web/src/main.tsx`: TS18047 twice at line 834, TS2304 at line 1005, and TS2349 at line 1605. RC98 null-guards both accesses to pending formatting state, refreshes presenter navigation through its actual React `setData` setter, and passes arrays (not updater callbacks) from `WidgetCanvas` to the slide-master editor. TypeScript remains strictly blocking in GitHub CI, and no quality gate has been disabled.

**Local evidence:** 4/4 targeted source regressions, TSX syntax 0 parse diagnostics, 565/565 API Node tests, 150/150 frontend Node tests. The full strict TypeScript/Vite build could not be reproduced locally because `npm ci --offline` lacked cached dependencies; the online install attempt did not complete. The external GitHub CI must verify the build. Historical inventory verification and ZIP integrity are also checked for the cumulative package. No RC readiness increment, remote repository operation, commit, push, tag or publication is claimed.

**Suggested cumulative commit since the last explicitly confirmed RC95 commit:** `Fix RC documentation and PPTX CI staging, and resolve presenter and slide-master TypeScript build errors`

---
# Quorivio 0.1.0-dev — RC97 handoff — native PowerPoint regression staging (1 November 2026)

**Certified RC readiness: 84.75%** (42 accepted, 17 partial out of 59 gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

Maintainer-confirmed commit baseline remains RC95; RC96 was packaged but not explicitly confirmed committed. Uploaded `logs_111818903235.zip` show RC96 documentation gate 30/30 PASS then RC90 native footer test errors on missing `pptx` before pip dependencies are installed. RC97 restricts RC90/RC91 early preflight to dependency-free checks; installs converter dependencies at the existing later gate; explicitly runs both native PPTX cases before full discovery. New RC97 order regression. Certified progress remains 84.75% (42 accepted, 17 partial of 59). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Fresh GitHub CI, TypeScript build and native browsers are not yet certified.

**Suggested single-line cumulative commit since RC95:** `Fix RC documentation checks and stage native PowerPoint CI tests after dependencies`

---
# Quorivio 0.1.0-dev — RC96 — CI documentation and dated inventory hotfix (1 November 2026)

**Certified RC readiness remains 84.75%** (42/59 accepted; 17 partial).

**Release state:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`. The maintainer confirmed RC95 as the latest committed baseline; RC96 contains only post-commit fixes. The uploaded CI (`logs_111817757197.zip`) failed early on six documentation-acceptance assertions, before compilation. RC96 restores the explicit release flags and fixes a legacy test that pinned all future inventory dates to 31 October 2026; SHA-256 validation and immutable historical receipts remain mandatory. GitHub CI for RC96 is not yet verified.

**Post-RC95 commit suggestion:** `Fix CI release-status documentation and date-agnostic current inventory validation`

---
# Quorivio 0.1.0-dev — RC95 — selection-aware rich text and PowerPoint-style ribbon (1 November 2026)

**Certified readiness remains 84.75%** (42 accepted / 17 partial out of 59 gates); no fresh external CI evidence yet. Cumulative source includes all RC89–RC94 development since the last maintainer-confirmed commit. No assistant commit, push, tag, publication, deployment or change to remote repositories.

**Rich text selection:** changes to font family, 10–96 px size, color, bold, italic, underline and strikethrough are saved as bounded, validated, per-character range marks. The selection remains retained when a ribbon button is pressed; the editable DOM restores the highlighted range after React re-renders. Bold/italic/underline/strike buttons use the effective style of ALL highlighted characters (including title defaults and existing inline spans), toggle it off if uniformly active, and back on when pressed again. Marks are coalesced, not endlessly appended, and unrelated fields (questions, answer options, descriptions) remain untouched. There is no user-authored HTML persistence.

**Ribbon visual design:** a professional, custom PowerPoint-inspired light ribbon with vector icons and semantically grouped **Carattere, Paragrafo, Forma, Disponi** sections, explicit active states, focus visibility, touch-size targets, help labels, horizontal scrolling on narrow screens, and reduced-motion compliance. The quick toolbar keeps object fill/border, alignment and property controls separate from selection-level text formatting. Font choices match the backend allowlist; unsupported fonts are not silently accepted.

**Title/Footer:** new titles default to bold, black `#000000`, transparent fill, no outline, 24px font size. New page titles and drag-created titles follow the same defaults, with explicit scheme/instance overrides still respected. Footer center content now renders saved inline marks on the presenter/participant projection. Editing auto-derived titles and footers freezes their displayed text to preserve valid mark ranges when manual formatting is applied.

**Local checks:** API Node 565/565 PASS; frontend Node 150/150 PASS, including 7 new RC95 unit/contracts; TS/TSX source parse PASS; Python PPTX exporter compiles. **Not verified locally:** full `tsc`/Vite build (npm dependencies not available), real Chromium/Firefox/WebKit or mobile editor interactions, live PostgreSQL and fresh GitHub standard/extended CI. Those release gates stay open. Native PPTX per-character markup parity across every widget kind is not claimed.

**Suggested cumulative commit (single English line):** `Refine slide schemes and presenter navigation, add QR links and vector borders, and introduce PowerPoint-style rich-text ribbon`

---
# Quorivio 0.1.0-dev — RC94 — borderless widget defaults, vector shape outlines and floating context menus (1 November 2026)

**Certified completion remains 84.75%** (42 accepted / 17 partial of 59 gates). This cumulatively includes the work from RC89–RC93 since the last explicit maintainer-acknowledged commit. No assistant commit, push, tag, server mutation or publication. The strict release gate and image publication remain disabled.

**Widget border 0 pt (default):** backend page-design validation, canvas style, style/shape inspectors, thumbnails, live presenter, rehearsal, participant rendering and editable PowerPoint post-it export now accept and honor zero-width strokes. A color or dash preset alone does not silently enable a border; an explicit request to choose a visible border selects 1 pt, while entering 0 removes the outline without losing the chosen color. Historical zero-width widgets are not silently rewritten.

**Actual shape contours:** clipped polygon elements cannot display their rectangular CSS border. Triangle, diamond, hexagon, cloud and speech bubble now use a single SVG vector path whose geometry matches the responsive clip polygon. The vector overlay follows every widget's size/rotation, stroke color, width and solid/dashed/dotted style in the canvas, rehearsal, live presenter, participant view and slide miniatures. For editable PowerPoint post-it shapes, native PowerPoint diamond, hexagon, cloud, callout, circle and rounded rectangle are now exported instead of a rectangle and imported using equivalent type metadata. Shape fidelity for other widget kinds and advanced fill/effect blending still requires independent PowerPoint and browser checks.

**Floating menu:** the context menu remains portaled to document.body to escape the widget clipping context. Its location is now calculated from the selected widget's live screen rect and the viewport, placing it to a side or above/below rather than always under the click/over the widget. On constrained screens the lowest-overlap visible location is chosen; scrolling/resizing dismisses stale coordinates. Right click, touch hold, keyboard context key and background-menu routing remain supported.

**Local checks:** API Node 565/565; Web Node 143/143; RC94 Python native-shape and menu contracts 4/4; RC93 QR and UI style contracts 11/11; TS/TSX syntax parse diagnostics 0 and portable Python compile passed. No full tsc/Vite build, real browser/touch rendering, live PostgreSQL or fresh standard/extended CI execution is claimed. Those gates remain open and scoring is unchanged.

**Suggested cumulative commit:** `Refine global schemes and presenter navigation, add participant QR URLs, fix zero-width widget borders and shaped outlines, and float context menus`

---
# Quorivio 0.1.0-dev — RC93 — participant QR with readable canonical URL (1 November 2026)

**Externally certified release readiness remains 84.75%** (42 accepted and 17 partial of 59 gates). This package is cumulative from the last maintainer-confirmed commit, including RC89–RC92. No assistant commit, push, tag, deployment or publication. Strict release and image publishing remain disabled.

**Change:** A newly placed QR widget defaults to **Accesso partecipanti**. All existing QR widgets now display their title, a scan-ready participation QR, and the **full exact URL encoded in the QR** immediately underneath. One shared React view is used by the page editor, presenter projection, rehearsal preview and live participant rendering. Long links wrap safely in small/resized widgets. The URL is not inferred from a short code or guessed from the browser origin: the owner-only `/api/sessions/:id/qr?format=json` returns precisely the same canonical URL that its SVG/PNG encodes (using the validated same-host browser-origin override); the public `/api/join/:code/qr-url` is accessible only for active non-expired sessions and returns the same canonical link as `/api/join/:code/qr.svg`. No privileged presenter URL or session ID is embedded in the default participation QR. When a link fails to load the widget shows an unavailable message instead of an invalid code. URL changes on session code rotation invalidate the cached widget view. The old session QR downloads remain available.

**Evidence:** `node --experimental-strip-types --test apps/api/test/*.test.ts` PASS 565/565; `node --experimental-strip-types --test apps/web/test/*.test.ts` PASS 139/139; RC93 Python QR contracts PASS 6/6; TypeScript/TSX syntax diagnostics 0. Full TypeScript/Vite build, real authenticated PostgreSQL and real browser end-to-end rendering were not performed locally (npm dependencies unavailable); fresh GitHub standard and extended CI are still pending. No new RC scoring credit until those gates pass. PowerPoint export still handles the existing supported widget subset; QR native export fidelity is not claimed in this cycle.

**Suggested cumulative commit:** `Refine slide schemes and footer placement, synchronize presenter navigation, and display participant QR links with readable URLs`

---
# Quorivio 0.1.0-dev — RC92 — authenticated live presenter screen (1 November 2026)

**Externally certified completion remains 84.75%** (42 accepted / 17 partial, total 59 gates); no new claim of external RC certification. Cumulative after the maintainer's last declared commit, including RC89–RC91 pending changes. No commit, push, tag, GitHub workflow run or publication was performed by the assistant. Strict release and Docker Hub publishing remain disabled.

The dashboard's **Apri schermo presentatore** opens an authenticated live page at `/screen/<session id>`. If the session is already active with a published page, it displays that exact page in its persisted order, even after closing and reopening the screen; it does not reset `opened_at`. When a ready or active session has no published page, opening the authorized screen atomically selects and publishes its first page. This single-transaction server action starts ready sessions and cannot overwrite a page chosen by another presenter; draft, paused and closed sessions are not automatically activated. Empty presentations display an informative message.

Presenters advance with Left/Right/Up/Down/PageUp/PageDown or with small overlay arrows at the bottom left and right. On pointer devices the controls appear on hover/focus in each lower corner. On touch devices the controls are always visible (disabled when at a boundary). The controls are rendered only after an authenticated `GET /sessions/:id` confirms owner/co-presenter access; the participant view receives no navigation controls. Navigation uses the established authoritative `POST /sessions/:id/activities/:aid/open` endpoint and the WebSocket broadcast shared by audience and dashboards. A new optional `expected_current_activity_id` precondition prevents a stale screen from overwriting another presenter's subsequent page change. The normal dashboard open action still works without this new precondition.

The browser Fullscreen API enters and exits from a visible screen toolbar. Native Escape also exits fullscreen. The stage remains keyboard accessible; keyboard shortcuts avoid form fields, editing controls and media widgets. Page counters, previous/next disabled states, in-flight locks, and recoverable network errors are included. Read-only participant presentations and published page timers retain their existing backend restrictions and semantics.

**Local validations:** Web Node tests 139/139 green, 13 targeted Python RC90–RC92 contracts green, TypeScript/TSX syntax parse diagnostics 0. The full Python suite was attempted but timed out inside converter/browser integration tests; full TypeScript/Vite, authenticated PostgreSQL transaction race, native Firefox/WebKit/Chromium pointer and touch interactions, and fresh GitHub standard/extended CI have not been run in this environment because npm dependencies were unavailable offline and npm registry DNS failed. All remain pending for actual certification.

**Commit message (one line; cumulative):** `Refine global schemes and slide footers, simplify session actions, and add synchronized presenter slideshow navigation`

---
# Quorivio 0.1.0-dev — RC88 — capacity QR URL normalization (31 October 2026)

**RC completion: 84.75%** (42 accepted, 17 partial); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. GitHub RC87 extended workflow `41241863260` on `982817a7080edb29ca4667e2de6877585af09098` successfully passed editor Chromium and idle WebSocket tests but stopped at 500-user capacity: `tools/ci_capacity_500.py` passed the API's relative `join_url` directly to `tools/load_500.py`, whose CLI correctly requires an absolute URL. RC88 normalizes only on the configured loopback origin and tests rejection of cross-origin/malformed paths. The 500-user load and 90s p95 SLO gates remain real and must be rerun in GitHub; no RC credit until proof. All historical manifests remain immutable. To continue, extract complete RC88 ZIP, `git add -A`, verify source manifest and CI, commit yourself, then run `rc_acceptance_suite=true` with no publishing. No assistant commit/push/tag.

---
# Quorivio 0.1.0-dev — RC87 — phase-independent idle live acceptance (31 October 2026)

**RC score unchanged: 84.75%** (42 accepted, 17 partial gates), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Logs `logs_111783956906.zip`: Chromium editor/palette acceptance and cross-replica WebSocket acceptance pass; 70-second idle test fails due to fixed 35/55 second thresholds unrelated to a server-start-aligned 20-second timer. RC87 adjusts receiver assertion (25-second silence timeout, at least three authoritative session snapshots, traffic in final 40/20 seconds), adds deterministic phase-offset regressions, preserves real PostgreSQL/WS test and private participant projection. CI GitHub retest required; no credit before evidence, no commits/publishing by assistant.

---
# Quorivio 0.1.0-dev — RC86 — real Chromium palette acceptance (31 October 2026)

**RC completion: 84.75%**, 42 accepted and 17 partial gates; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. The uploaded `logs_111780102568(1).zip` shows browser acceptance passed the context-menu part and many other Chromium checks, then hit `assert await buttons.count()==17` in `tools/ci_browser_editor.py`. The real widget palette now has 19 kinds including Title and Footer. The fixed assertion is obsolete, not evidence of a missing app feature. No additional RC gate credit until a new extended GitHub run passes.

**RC86:** the native Chromium test checks required widget kind coverage without a brittle fixed total, unique tool kinds and SVG icons, descriptive accessible labels, no native title tooltips, plus the existing real add/autosave/reload sequence. Added early Python regression preflight before npm. Immutable historical manifests are kept; RC86 is the new grouped-SHA current manifest. No assistant commit/push/tag/publication.

---

# Quorivio 0.1.0-dev — RC85 — secondary pointer context ownership (31 October 2026)

**RC completion: 84.75%**, 42 accepted, 17 partial gates; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Maintainer baseline commit `2d081ae95594ab79a743822476dee77336f6ea9e` (RC84). The user confirmed standard CI green. Extended CI `https://github.com/desalvo/quorivio/actions/runs/41237085040/job/124643010292` failed the real native Chromium widget menu, with background menu open, after prior Chromium checks passed. No RC acceptance points have been granted for this unverified fix; new GitHub CI is pending.

**Fix:** prevent secondary-button pointerdown from changing widget selection or initiating a gesture before the browser delivers native contextmenu. Remember the pointerdown widget only for the same native gesture, bounded by <1.5 seconds and <8 pixels, to recover from pointer retargeting. Blank canvas context requests continue to use the page background menu. The Chromium test still requires a real pointer event and now captures native target diagnostics on failure. Added four Node tests and three Python contracts, with early CI preflight. Historical SHA manifests are immutable; RC84 becomes historical and RC85 is current. No assistant commit, push, tag, release, or publication.

---

# Quorivio 0.1.0-dev — RC84 — legacy widget context-menu contract update (31 October 2026)

**RC completion: 84.75%**, 42 accepted / 17 partial gates (59 total); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Maintainer Git baseline `112d3c2a99b44b743bfc56f5137cd9781323f9fd` (RC83). Standard quality job `https://github.com/desalvo/quorivio/actions/runs/41234368553/job/124636106637` ran 1,466 Python tests, failing one stale RC37 source-string check for `positionMenu(e.currentTarget,e.clientX,e.clientY)` following the actual RC83 React canvas-capture event-routing fix. RC84 keeps real native-pointer behavior, menu positioning, body portal, touch and keyboard checks and replaces the outdated literal assertion with assertions about the current handler. Both the historical contract and the new RC84 tests run before npm in CI. All previous manifests remain immutable; RC83 becomes historical and RC84 is current. **New GitHub CI is pending.** No fake acceptance credit, commit, push, tag or publish.

---

# Quorivio RC83 handoff — real widget context routing (31 October 2026)

**RC completion: 84.75%** (42 accepted / 17 partial across 59 gates); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Last maintainer Git commit `7f73e4b2dbe7edb58fc34805e43e7d95bbabdbf1`; failing extended run `https://github.com/desalvo/quorivio/actions/runs/41232865276/job/124630494242`. Root symptom observed for three cycles: real Chromium widget right-click opens canvas background menu, despite geometry verified by Playwright. Previous RC80–RC82 pointer locator attempts did not resolve production event ownership. RC83 moves context menu dispatch to `.widget-canvas` `onContextMenuCapture`, resolves event target / saved DOM bounding rectangles, routes to the selected widget menu while preserving empty-canvas background menu, adds a shared pure TS hit-test helper and 3 Node unit tests, updates historical assertions and adds CI early contract. Native end-to-end browser test not yet green after this change; no acceptance score increase. Do not commit/push/tag from assistant. Continue from RC83 package, run standard CI and RC acceptance with one opt-in checkbox, inspect logs before promotion.

---

# Quorivio 0.1.0-dev — RC82 — deterministic GCM backup corruption CI hotfix (31 October 2026)

**Current score 84.75%**, 42 accepted / 17 partial of 59 gates; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. User-confirmed source SHA `280b1bdbffa9073460455335c01ac55dfe468491`. Standard workflow `41229380989`, job `124620158038`, failed a single backup mirror test after 1,461 Python tests: the fixed two-byte replacement may coincidentally match the original random GCM tag suffix, leaving the ciphertext unchanged. The exact random bytes from the failed run were not logged. The cryptographic implementation is correct; only the randomized test setup is faulty. RC82 replaces fixed suffix with non-identity bit-flip and adds fail-closed tests for authenticated header, ciphertext, and tag and for private scratch and destination cleanup. Initial CI preflight executes this suite before expensive browser/database acceptance. No release gate accepted on the basis of this test-only hotfix. No assistant commit/push/tag/publish. Full new GitHub workflow still required.

---

# Quorivio 0.1.0-dev — RC81 — browser right click locator-bound (31 October 2026)

**Current score 84.75%** (42 accepted 17 partial of 59); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Git baseline `d4ed14ee61a673ce6d1ea7767c790e74de79089b` (user committed RC80). Extended run 41220871348, job 124594956256 failed during real Chromium context-menu test; the previous absolute `page.mouse.click` with a snapshot coordinate could move from widget to background during layout reconciliation. RC81 uses Playwright widget locator `.click(button='right', position=offset, trial=True)` then actual locator-bound native click; asserts correct portal menu, no background menu, and diagnostic failure if needed. No bypasses, no new accepted gate. Historical manifests preserved; archive closure verified. Pending full extended campaign after commit.

---

# Quorivio 0.1.0-dev — RC80 — Chromium widget context-menu pointer target hardening (31 October 2026)

**Certified RC score: 84.75%** (42 accepted / 17 partial of 59); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Git baseline `6bfb893c27cb0bbcb2d2c6d92ca5d6b58f487544` (user committed RC79); standard CI green by user report, extended run `41218084773`, job `124586715148`, FAILED at `tools/ci_browser_editor.py:160`: right click intended for `Azioni widget text` opened `Menu contestuale sfondo canvas`. Other real Chromium rehearsal/focus/deadline tests had passed earlier in this run. RC80 changes real pointer test to choose an uncovered hit-tested widget pixel and dismiss stale background menus; React handler now stops propagation and clears pending background gestures. Four new regression tests run before npm. Historical inventories remain immutable and package closure is verified. No automatic Git commit/push/tag/publish. Pending new extended CI to validate actual React Chromium behavior.

---

# Quorivio 0.1.0-dev — RC79 — recovered historical manifest and fail-closed cumulative ZIP closure (31 October 2026)

**RC progress: 84.75%** (42 accepted, 17 partial / 59; strict blocked).

**RC79 CI root cause (run 41215310977, job 124578491540):** the RC78 ZIP and commit omitted `docs/validation/RC_CYCLE77_PACKAGE_INVENTORY_20261031.json`, although the CI workflow still references `verify_rc_cycle77_inventory.py`. Recovered the original, byte-for-byte RC77 receipt (unchanged SHA-256), included it in the current source inventory and in the ZIP. This was a packaging error, not a Chromium functional failure.

**Permanent packaging guard:** `tools/rc_inventory_closure.py` checks all verifier/manifest dependencies in both the source manifest and the actual ZIP. `tools/package_rc_cumulative.py` now includes every historical manifest and requires exact ZIP/source SHA-256 matching. RC79 runs the new closure regressions before npm. Any missing old receipt fails the archive build instead of the GitHub CI. **Operator:** extract the entire cumulative RC79 package, stage all changed and new files with `git add -A` and run `python3 tools/ci_inventory_reference_guard.py` plus `python3 tools/verify_rc_cycle79_inventory.py` before committing. A missing receipt in the Git index is deliberately rejected.

**CI status:** Latest run 41215310977 failed at the missing RC77 receipt preflight before functional tests. The previous RC78 browser fix has NOT yet passed new extended CI. **Certified gate score remains 84.75%** (42 accepted, 17 partial / 59); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag/publication.

---

# Quorivio 0.1.0-dev — RC78 — Chromium rehearsal accessible-name CI fix (31 October 2026)

**Git baseline:** `9c947b6415d1ab5c1509c3f01cbe0b5d872041df`; the maintainer reports the standard CI passed. Extended run `41212067005` proceeded through its earlier Chromium checks, but job `124568946911` timed out in `tools/ci_rehearsal_singleton_offline_chromium.py`: a stale Playwright locator expected `▣ Anteprime affiancate`, whereas the live dashboard renders a graphical icon with accessible text **Anteprime affiancate**. Aggregate job `124569421798` failed as a consequence, not an independent defect.

**RC78:** use the actual accessible name and assert a unique visible launch button before clicking. Keep real React portal isolation, focus restoration and Firefox/WebKit coverage unchanged. Add early CI regression contracts for the selector and live dashboard markup; Chromium and native Firefox/WebKit are **pending** new GitHub CI. **Certified score unchanged at 84.75%** (42 accepted, 17 partial of 59); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push, tag or publication.

---

# Quorivio 0.1.0-dev — RC77 — Campaign cannot publish or run strict release checks (31 October 2026)

- Maintainer baseline `e4f24a9fb8a36ef0b96ddb20b755a5a2f9335343`; standard CI `41209516202` passed. RC campaign `41210395340` ended early because it reported `RC_CAMPAIGN_PUBLISH=true` in the runner despite selecting only the RC checkbox. No proof of why GitHub supplied the value.
- RC77 hardcodes effective false/false for the campaign admission; publishing and strict jobs refuse campaign mode, as does shell publisher. New early CI tests enforce this policy.
- Verified score remains 84.75%, 42 accepted / 17 partial of 59. No commit by assistant; maintainer commits package then starts a fresh non-publishing RC dispatch.


**RC77 safety policy:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`; manual non-campaign publication is a separate explicitly approved operation.

---

# Quorivio 0.1.0-dev — RC76 — Python CI legacy editor contract reconciliation (31 October 2026)

**Last maintainer commit:** `39564e862a2ed431544cea22e0c0b39bd6794b34` (includes RC75). Standard CI `41208293676`, job `124557792918`, passed the frontend/backend compilation and Node tests, then ran 1439 Python tests with **five failures** from stale literal-code assertions.

**RC76 changes:** preserve actual behavior assertions for the typed persisted widget fields, merged Settings and Live monitoring, submit-time timer deadline, extended Title/Footer widget enumeration, and linked-result simulated free-text statistics. All five suites now run as an early CI preflight before npm installation. No production behavior changes, test omissions, security bypasses or historical manifest rewrites.

**RC readiness:** **84.75%** (59 gates, 42 accepted and 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Full new GitHub CI (including Gitleaks) is pending the next maintainer commit. The assistant has not committed, pushed, tagged or published.

---
# Quorivio 0.1.0-dev — RC75 — TypeScript build hotfix (31 October 2026)

**Last user-confirmed commit:** `77486c8f9b902d5e89f0f3f823d3cf496f00d5c3` (includes RC74). Standard CI `41207039782`, job `124554135225`, failed at **Compile frontend and backend** with four frontend TypeScript diagnostics before PostgreSQL integration and extended acceptance. No assistant commit, push, tag or publication.

**RC75 changes:** the editable widget's type now includes persisted `reactionIconSize`; the optional `pageNumber` is narrowed to number before comparison; statistical sources and subquestions explicitly model `answerMode`, avoiding an untyped `any[]` intersection. Existing footer bottom-right alignment, presentation appearance and free-text rehearsal behavior are preserved.

**Local evidence:** 560 API tests and 123 frontend tests passed, alongside strict TypeScript checks on the two independent affected modules and targeted RC75/footer tests. Full `npm run build` remains unverified locally because the npm registry is unreachable and dependencies could not be installed; the full Python suite timed out. Re-run GitHub CI after the user's commit to establish overall acceptance.

**RC readiness:** **84.75%** (59 gates, 42 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No new scoring credit for an as-yet-unvalidated CI hotfix. External physical and independent approvals remain open.

---
# Quorivio 0.1.0-dev — RC74 — Footer page number at bottom-right canvas corner (31 October 2026)

**Last user-confirmed Git baseline:** `487c960f09b3c9adb996d489f44b52d059da12b2` (RC65); RC66–RC74 cumulative and not yet confirmed committed. Assistant has not committed, pushed, tagged or published anything.

**Change:** default Footer is x=0%, y=94%, width=100%, height=6% of the 16:9 canvas. The session title stays centered, while page number is positioned `right:0; bottom:0` at the **bottom-right canvas corner**, rather than vertically centered in the footer strip. Page numbers continue to reflect the current page ordering. The participant view now renders the same footer within the page canvas, not in a separate block after it. Editor, rehearsal and projection reuse the anchored footer-number rule.

**PPTX:** editable right-aligned page-number textbox reaches the slide's absolute right/bottom edges, uses bottom vertical alignment and zero text insets. Existing toggles and text customization are unaffected.

**Validation:** RC74 Python regressions check CSS geometry, participant stage placement and actual exported PowerPoint dimensions; RC73 contracts remain. Pending new GitHub CI. **Certified RC score unchanged 84.75%** (42 accepted, 17 partial of 59); `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

---
# Quorivio 0.1.0-dev — RC73 — Slide master Title/Footer and page numbering (31 October 2026)

**Last user-confirmed commit:** `487c960f09b3c9adb996d489f44b52d059da12b2` (RC65). **No commits made by assistant**; cumulative package contains RC66–RC73.

**Certified RC status: 84.75%** (59 gates: 42 accepted, 17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. RC73 has no new credit pending the next CI.

Every new slide/page, including new poll/quiz pages, gets a transparent centered `title` widget from the backend with the current page title. The owner can unlink the individual widget and specify custom text. The session-level **Title slide master** in the page settings provides a live preview and global font family, font size, text color and boldness. A title can opt out to use per-widget typography.

An insertable/draggable `footer` widget defaults to full canvas width, at the bottom with one text line. It displays the session name centered and the page number at the right; either can be disabled and the center replaced with custom text. Page numbering follows current order and also appears under each sidebar thumbnail. Both types are server-validated and rendered in the editor, presenter projection, rehearsal, and audience view. PowerPoint export emits editable Title and Footer text, including slide-master typography and computed page numbers.

**Local checks:** 560 Node API tests and 121 Node frontend tests passed, plus 41 targeted Python regression tests and 2 RC73 PPTX tests. The complete Python run did not finish within the local limit. Full TypeScript/npm build is unavailable locally due to missing dependencies. RC73 has not yet passed a new GitHub CI.

**Previous green CI:** standard `41191213305` and extended `41191751069` on `487c960f09b3c9adb996d489f44b52d059da12b2`. Remaining external verification: physical RWX, real devices, independent GDPR/AGID/security approvals. No automatic publication.

---
# Quorivio RC72 — Live access, dashboard, and widget visuals (31 October 2026)

**RC readiness unchanged at 84.75%** (42 accepted and 17 partial of 59 weighted gates, total 100). No new standard or extended GitHub CI has validated RC72 yet; strict RC remains blocked and publishing disabled. Last user-confirmed Git commit `487c960f09b3c9adb996d489f44b52d059da12b2`; RC66–RC72 remain a cumulative, not-yet-confirmed-committed package; the assistant does not commit/push/tag.

Active-session transition or publishing a page now extends audience-link expiry for at least 24 hours; the displayed participant URL follows the actual browser origin. Authenticated QR GET uses a checked same-origin browser Referer/Host/Sec-Fetch-Site when available, with configured canonical origin fallback. Live WebSocket accepts the application's exact same-host browser Origin only (with existing authorization/revocation) rather than requiring an outdated server setting. Authenticated HTTP polling refreshes dashboard snapshots every 12s during WebSocket outage and labels the fallback honestly.

Dashboard Settings contains monitoring; there is no third Monitoring tab. The one-column layout has no empty grid cells. Timer restart explicitly chooses whether to preserve existing responses/attachments or erase them transactionally; the option is required. Widgets are transparent and square by default, with rounded forms explicit and presentation effects consistently applied across editor, rehearsal, and live surfaces. Connected-participant palette icon uses a gauge. Motion-reduction preferences remain honored.

**Local evidence:** 558 Node API tests and 118 web tests green, TypeScript transpile syntax clean, nine targeted Python RC71 tests green, SHA-256 archive/source validation. Full Python suite timed out locally; full bundle build and live PostgreSQL/browser tests remain CI-pending. No automatic CI gate promotion.

---
# Quorivio RC71 handoff (31 October 2026)

- Version `0.1.0-dev`, user-confirmed Git baseline `487c960f09b3c9adb996d489f44b52d059da12b2`; previous standard CI `41191213305` and extended CI `41191751069` green on this baseline, not on RC71.
- User has not declared another commit: package RC71 contains uncommitted cumulative changes RC66–RC71. No automatic commit/push/tag/publish.
- **Verified progress 84.75%, 42 accepted / 17 partial of 59 gates.** New features are provisionally implemented, NOT certified by new GitHub CI. Strict RC blocked, publication opt-in only.
- RC71: square-bracket cloud counts; colorful enlarged text tools; presenter profile optional text; 16–96px reaction icons; persistent background upload picker; real dashboard attendee and authenticated presenter QR URLs; no rehearsal buttons in active session.
- First page opening starts timer and revisit never renews it; authenticated manual restart clears page results/private uploaded files and starts new clock; full session reset to ready requires owner confirmation, clears participant data, rotates public join code, preserves design/settings.
- 554 API and 115 web tests passed locally; full Python suite timed out. TypeScript parser reports no syntax errors. CI has a new disposable PostgreSQL/HTTP session reset/timer test but it has not run. Validate standard and extended CI, real browser file picker, storage, timers and restart before accepting new gates.

---
# Quorivio RC70 handoff (31 October 2026)

- Version fixed at `0.1.0-dev`. Last user-declared Git baseline `487c960f09b3c9adb996d489f44b52d059da12b2`; prior green CI runs `41191213305` and `41191751069`.
- RC70 is cumulative from RC66; user has **not confirmed a new commit**. Assistant must not commit/push/tag.
- Readiness remains **84.75%** (42 accepted, 17 partial, 59 gates, weight 100); RC70 fixes are not yet accepted by new GitHub CI. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
- Timer duration 1–3600 s configured in widget properties, page-wide rehearsal and live-browser interaction timeout, authoritative PostgreSQL-clock mutation guard; proportional widget font scaling preserving character-specific marks; selected resize/rotation handles outside clipping; presenter private profile email and deduplicated title; presenter-only participant count with rehearsal fixtures; free-text submitted rehearsal answers visible in presenter-side results; synchronized preview modes.
- Next: full standard and opt-in extended CI on committed cumulative, browser checks and actual PostgreSQL timeout tests. Real OAuth providers, physical multi-node RWX, public TLS and independent GDPR/AGID/security signoffs remain blocked.

---
# Quorivio 0.1.0-dev — RC69 handoff (31 October 2026)

**Verified score: 84.75%** (42 accepted / 17 partial / 59 gates). Commit baseline `487c960f09b3c9adb996d489f44b52d059da12b2`, prior standard CI `41191213305` and extended `41191751069`. User has not declared a commit for RC66–RC69; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

A2-PAGE-JSON acceptance derives from already-green browser download; new `page-order-recovery.ts`, unit tests and native Playwright acceptance are **pending fresh CI**. Start from this cumulative package and run standard + extended CI after maintainer commit. Do not mark physical RWX, real providers, screen readers or external GDPR/AGID review accepted.

---
# Quorivio 0.1.0-dev — RC68 — Verified private presenter background ownership (31 ottobre 2026)

**Maintainer-committed baseline:** `487c960f09b3c9adb996d489f44b52d059da12b2`. Standard CI `41191213305` and extended RC campaign `41191751069` succeeded on the same code; publication skipped. User has not declared a new commit for RC66–RC68. No assistant commit, push or tag.

**Evidence-scoped reconciliation:** production-quality job `124509777927` ran `tools/ci_background_library_postgres.py` using authenticated HTTP and disposable PostgreSQL 18. It proved presenter PNG upload, reuse among owned sessions, non-collaborator denial, offered access to a collaborator, independent ownership on copy and original access revocation. Gate `C4-PRIVATE-BACKGROUNDS` is distinct from already-accepted `C4-PROFILE` profile photos and `C4-AV-INSTREAM` raw ClamAV scanning. Parent C4 weight shrinks 2 to 1 while new accepted gate is weight 1, adding 0.50 percentage points.

**Verified RC progress: 84.25%** (41 accepted, 17 partial of 58 gates; +0.50 over RC67). Total weight 100. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. **No claim of real multi-node CSI/NFS RWX storage, managed HTTP-upload ClamAV, assistive-device testing, independent GDPR/AGID/security approval.** New package still needs the next GitHub CI.

---
# Quorivio 0.1.0-dev — RC67 — Verified client rehearsal acceptance (31 October 2026)

**Maintainer baseline (already committed):** `487c960f09b3c9adb996d489f44b52d059da12b2`. Both standard CI `41191213305` and full non-publishing opt-in campaign `41191751069` passed on that SHA, with 11/11 mandatory jobs successful. No new commit by the assistant.

**Evidence reconciliation:** the already-green quality job `124509777927` proved actual Chromium 1440/390 offline interactive rehearsal: draft/submit, one-shot reactions, stable presenter statistics, exact timed deadline and disabled late submissions. The native Firefox/WebKit job `124511576966` proved built React desktop/mobile dual preview visibility and accessible modal restoration. This is the narrowly accepted `B2-CLIENT-REHEARSAL` gate; `B2-DB` remains unchanged for database concurrency, and A1/A4 still cover modal focus. B2 residual retains long-running multi-replica/user/physical-device acceptance.

**RC readiness: 83.75%** (40 accepted, 17 partial, 57 total); +1.00 percentage point compared with RC66. Gate weights sum to 100; partial B2 decreases from 4 to 2 and accepted client subgate adds weight 2. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. **Strict RC NOT READY**: real provider federation, public TLS, physical multi-machine RWX, independent assistive-technology accessibility and GDPR/AGID/security sign-offs remain outstanding. CI for this NEW inventory and documentation must be rerun after the maintainer commits.

---
# Quorivio 0.1.0-dev — RC66 — GitHub-verified SSO reconciliation (31 October 2026)

**Latest maintainer commit:** `487c960f09b3c9adb996d489f44b52d059da12b2`. Standard CI `41191213305` and full opt-in campaign `41191751069` PASS (11/11 required checks on the same source); no image publishing. Scoped PostgreSQL SSO link/revocation and account-scoped identity-management HTTP acceptance were both verified in job `124509777927`; this is distinct from the previously accepted protocol-only `C3-AUTO` gate. Split partial C3 weight 4→2 and accepted new `C3-PG-IDENTITY` weight 2; total gate weight remains 100.

**New verified progress: 82.75%** (39 accepted, 17 partial / 56 gates; +1.00 point from 81.75%). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. RC strict is NOT ready: real Google/GitHub/Facebook consent and redirects, public TLS, physical RWX multi-machine storage, human accessibility and independent security/GDPR/AGID sign-offs remain open. All original dated receipts are immutable. No assistant commit, tag or push. Next package uses this commit as base.

---
# Quorivio 0.1.0-dev — RC65 — Historical CI documentation regression (31 October 2026)

**Latest maintainer commit:** `0786ef2f4b064080dd49b42f41d2f04b3d5f4c8a` (includes RC64). Standard CI run `41189697040` (job `124503743950`) passed 546 API and 99 web Node tests, build, PostgreSQL integrations, Kubernetes, and integrity checks. The Python suite failed 2 of 1399 tests: historic RC57/58 tests required RC58 markers to appear within the first 1700/2000 characters of mutable status documents, which grow by prepending current-cycle sections.

**RC65 fix:** historical regression tests now validate complete documents and the dedicated RC58 evidence receipt, without fixed document prefixes. RC35's similar 4000-character cap has been removed proactively; RC63's latest-inventory test no longer hardcodes cycle 64. RC64 checksums are historical and immutable, RC65 is the current checksum inventory. No security gates or tests disabled; prior manifests remain frozen. The new package needs a new maintainer commit and green CI for acceptance.

**Certified RC:** 81.75% (55 gates: 38 accepted and 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. External provider verification, physical RWX, cross-device accessibility and independently signed privacy/security review remain pending. No assistant commit/push/tag.

---
# Quorivio 0.1.0-dev — RC64 — Gitleaks test-fixture false-positive fix (31 October 2026)

**Confirmed maintainer commit:** `118480606d97e3e32ddf92991889c7a577ebfc02` (includes RC63). Standard CI run `41188841418`, job `124501245873`, passed the 546 API / 99 web Node suites, full build, real PostgreSQL HTTP/SSO/background acceptance, multi-replica workflows, Kubernetes and Python tests, and all 50 historical/current SHA-256 checks. Final `gitleaks/gitleaks-action@v2` blocked the run on a test-only static token in `tools/tests/test_rc_cycle62_ci_rate_isolation.py` (generic-api-key). The token was a fixture, not a leaked live credential.

**RC64 resolution:** replace the literal token with a deterministic SHA-256 test fixture assembled at execution time; the real CI load token remains random and restricted to non-production loopback calls. Add early regression checks for this pattern, keep Gitleaks at full strength (no exclusions, no suppressions, no disable), preserve the historical RC63 SHA-256 inventory, and create RC64 as the new source inventory. New CI run required after user commit. **Do not treat a re-run of the old commit as repaired; the new source must be committed.**

**RC readiness:** still **81.75%** formally verified (55 gates: 38 accepted, 17 partial), strict RC blocked. Historical passing standard `41152434205` / extended `41152939003` and `41123318359` do not certify RC64. Opt-in RC acceptance needs CI standard green first; publish_image=false, publish_latest=false, rc_strict=false. External provider tests, physical RWX, independently signed GDPR/AGID/security and cross-device accessibility remain open. No assistant commit/push/tag.

---
# Quorivio 0.1.0-dev — RC63 — Historical CI manifest recovery (31 October 2026)

**RC certified:** 81.75% (38 accepted, 17 partial of 55); strict RC BLOCKED.
**RC63 controls:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no new gate credit until GitHub acceptance.


**Earlier accepted evidence (historical, not RC63):** standard CI `41152434205`, extended CI `41152939003` on commit `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`, plus prior extended run `41123318359`. These runs **do not** certify RC63.

**Last maintainer-confirmed commit:** `8e7d2df0f3badb39136f9901cd91acf2897ca453` (includes RC62). Standard GitHub CI run `41187779633`, job `124498103225`, passed the previous HTTP 429 issue, Node unit tests, full build, real PostgreSQL integrations, and npm vulnerability check. It failed in `tools/ci_inventory_reference_guard.py` because the cycle 59 source checksum receipt was absent from the committed tree. This prevented the Python/Kubernetes test step from running.

**Root cause:** the cumulative RC61 archive accidentally dropped original cycle 59 and 60 inventory receipts while retaining the workflow references and historical verifiers. RC62 did not restore them.

**Resolution:** recover the original RC59 and RC60 JSON inventory receipts byte-for-byte from their original cumulative archives, pin SHA-256 in the CI reference guard, add automatic presence/absence regression tests, and add a current RC63 inventory verification in the standard workflow. No historical manifest is rewritten.

**Limits:** Local source/ZIP verification does not substitute for the next post-commit GitHub CI. Strict RC remains blocked; certified RC score stays at 81.75% (38 accepted / 17 partial of 55). No assistant commits, pushes, tags, or publishing.

---

# Quorivio RC62 — completion handoff (31 October 2026)

**Last maintainer commit:** `5a088fc300037b5a6a98a533de36ac6700b3b765`, containing RC61. Standard GitHub run `41186895267`, job `124495541784`, **failed**: the real PostgreSQL background library CI script hit shared loopback rate limit `429` while expecting `200`, following successful Node build/tests and SSO PostgreSQL checks. **RC62 is the only uncommitted cycle since that commit.** Fix: both `ci_portable_http.py` and `ci_background_library_postgres.py` now attach the existing strong ephemeral nonproduction-only token, validated for loopback before the network; `.github/workflows/ci.yml` forwards it, regression tests cover failure modes. No change to production rate limiting, credentials, features, version, RC score or publishing controls. See `docs/RC62_CI_THROTTLE_ISOLATION.en.md`. **Certified RC 81.75% (38 accepted / 17 partial of 55), strict blocked.** Next step: maintainer manually commits RC62 and runs standard CI before extended opt-in; never publish image with this change automatically.

---

# Handoff — Quorivio RC61, 31 October 2026

**Last confirmed commit:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`. Green standard `41152434205`, extended `41152939003` only validate this earlier baseline. **Cycles 58–61 cumulative and uncommitted.** Official RC **81.75%**, 38 accepted, 17 partial of 55; strict RC not ready. `rc_strict=false`, `publish_image=false`. Added password-confirmed identity self-service list/unlink, transaction and revocation checks, shared attempt limiter, dashboard and CI-only PostgreSQL HTTP acceptance. Local **546 API** and **99 web** tests pass; npm build and new database CI acceptance pending. See `docs/RC61_FEDERATED_IDENTITY_MANAGEMENT.en.md`; maintainer commits, then standard CI and one nonpublishing acceptance campaign.

---

# Quorivio 0.1.0-dev — cycle RC60 handoff (31 October 2026)

**Maintainer baseline** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`; verified standard `41152434205` and extended `41152939003`. **Cycles 58–60 cumulative and NOT committed.** **Verified 81.75%** (55 gates, 38 accepted, 17 partial); RC strict NOT ready. No assistant git operations or publication.

Cycle 60 closes the local federated-account linking revocation gap: signature issuance checked at start, PostgreSQL stored issuance in single-use flow and conditional link at callback after password/admin revocation. Additive migration; Node and guarded PostgreSQL CI regressions. **Local 541 API Node + 99 web Node tests passed.** New PostgreSQL CI step, complete npm build and live-provider acceptance unverified. Details: `docs/RC60_FEDERATED_LINK_REVOCATION.en.md`.

Remaining gated work: real RWX CSI across physical nodes, disposable KIND HTTPS not yet run on the verified baseline, true Google/GitHub/Facebook and external SMTP, independent UX/accessibility, GDPR/AGID/security approvals. After maintainer commit: standard CI, then one `rc_acceptance_suite=true` nonpublishing dispatch with `publish_image=false`, `rc_strict=false`, `publish_latest=false`. Preserve official matrix until new evidence.

---

# Quorivio 0.1.0-dev — accelerated RC59 closure sprint (31 October 2026)

**Last maintainer-confirmed commit:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`; standard CI `41152434205`, extended CI `41152939003` PASS. **Certified 81.75% (55 gates, 38 accepted, 17 partial), RC strict blocked.** Cycles **58–59 uncommitted** and included cumulatively. This sprint implements a one-click full isolated GitHub RC campaign covering 13 optional areas plus a fail-closed 11-job final verdict; `publish_image=false`, `rc_strict=false` mandatory. Identity-provider OIDC/OAuth JSON reads are byte-bounded while streaming; docs now correctly describe PostgreSQL single-use cross-replica state. No new gate promotion without CI proof, true CSI RWX or external sign-off. See `docs/RC59_ACCELERATED_CLOSURE.en.md`. No assistant commit/push/tag/publication.

---

# Quorivio 0.1.0-dev — Cycle 58 recovery handoff (31 October 2026)

**Committed baseline `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`:** standard CI `41152434205` and extended CI `41152939003` green; real 70s idle snapshots and 500 independent global p95 proof passed in quality job `124393360139`. **Verified RC 81.75%** (55 gates, 38 accepted/17 partial), +0.50 for these distinct bounded proofs only. Uncommitted cycle 58: bound cross-session PostgreSQL refresh to 8 concurrent calls; new tests, checksum inventory and fresh CI required. KIND TLS was NOT enabled in the verified run; physical multi-node CSI RWX unverified. `publish_image=false`, `rc_strict=false`; no assistant commit/push/tag. See `docs/RC58_VERIFIED_IDLE_SLO_AND_REFRESH.en.md` and `docs/RC_GATE_MATRIX.json`.

---

# Quorivio 0.1.0-dev — RC cycle 57: shared WebSocket snapshot fanout (31 October 2026)

**Last committed baseline:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; **cycles 49–57 cumulative and uncommitted**. Standard `41120048115` and extended `41123318359` are green for the previous baseline only. **Certified RC: 81.25% (53 gates: 36 accepted, 17 partial)**. This cycle adds no unverified gate credit.

**Functional change:** a 501-client snapshot (500 audience + one presenter) now uses two shared JSON serializations instead of one per socket, with server-side view isolation, per-socket slow-consumer and transport-failure handling, and initial delivery through the ordered per-session queue rather than an independent database read/send. See `docs/RC57_LIVE_FANOUT.en.md`. Local unit/contract checks cover these properties; independent GitHub CI and sustained multi-replica load remain pending. `publish_image=false`, `rc_strict=false`. No assistant commit/push/tag/publication.

---

# Quorivio 0.1.0-dev — RC cycle 56: authoritative quiet-session snapshots (30 October 2026)

**Last committed baseline:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; **cycles 49–56 remain uncommitted and cumulative**. Last successful GitHub runs are standard `41120048115` and extended `41123318359`, which do NOT verify cycles 49–56. **Certified RC is 81.25% (53 gates: 36 accepted / 17 partial)**; new local credit: **0**. `publish_image=false`, `rc_strict=false`.

**Critical functional defect discovered:** cycle-55 browser watchdog expected periodic server snapshots, but the backend heartbeat only updated PostgreSQL presence. During a quiet session, no snapshot was sent after the opening event; after 65 seconds the client would reconnect needlessly, potentially creating a 500-client reconnection storm.

**Cycle 56 fix:** authoritative snapshots every 20 seconds for each *active session*, using the existing coalesced `broadcastLocal()` queue. This is one queued read/fanout **per session**, not per participant or per replica. No extra PostgreSQL cross-replica notification. Snapshot failure never creates a fake keepalive: the browser still times out and recovers. No new client protocol or stored data fields. Tests include 10-minute idle simulation without reconnects, 500 subscribers sharing one read, missing database snapshots, cross-session frames, overlap and retry.

**Added opt-in real acceptance:** `live_idle_test=true` runs a disposable PostgreSQL two-replica 70s quiet presenter/participant snapshot test after maintainer commit; see `docs/RC56_IDLE_SNAPSHOT_ACCEPTANCE.en.md`.

**Limits:** deterministic local tests do not certify real load, failover, public TLS, 500-client SLO, RWX CSI/NFS or external compliance review. After maintainer commit, run standard and extended GitHub acceptance including HTTPS and capacity SLO opt-ins; do not increase certified percentage before their results.

---

# Quorivio 0.1.0-dev — RC cycle 55: WebSocket snapshot freshness and stale data visibility (30 October 2026)

**Last successful GitHub CI:** standard `41120048115` and extended `41123318359` (baseline `64aa3437`); do not certify uncommitted changes.

**Required next CI options:** `rc_strict=false`, `publish_image=false` until independent gates close.

**Last confirmed commit:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; **cycles 49–55 remain uncommitted and cumulative**. **Certified RC unchanged at 81.25% (53 gates, 36 accepted / 17 partial)**; no score promotion from local changes.

**Functional change:** a 65-second snapshot-freshness watchdog for browser live WebSockets, vs server snapshots approximately every 20 seconds. Only valid matching-session snapshots renew freshness. A stale or errored socket is retired/fenced, stale events cannot replace fresh session state, reconnect uses existing bounded jittered backoff, and timers are cleaned on offline/dispose/terminal close.

**UI:** accessible connection-loss/access-revocation warnings on presenter statistics and the projection screen to mark retained data as potentially stale, without hiding it. No database protocol or stored response change.

**Evidence/limits:** 505 backend / 99 frontend Node tests PASS; 1,347 Python tests PASS in eight groups (one skipped); focused TypeScript compile PASS; deterministic new frontend Node tests, Python integration contracts, manifests. Full CI, actual multi-replica impairment, realistic 500-client latency/recovery and independent hardware/device acceptance remain required. HTTPS and SLO opt-in acceptance from earlier cycles still requires GitHub on the uncommitted cumulative.

---

# Quorivio 0.1.0-dev — RC cycle 54: live WebSocket recovery and stale-connection fencing (30 October 2026)

**Last green GitHub CI (committed baseline):** standard `41120048115`, extended `41123318359`, both on `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`. The cycle 54 implementation remains uncommitted.

**Maintainer-confirmed commit baseline:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (cycle 48). **Uncommitted cumulative changes:** cycles 49–54. **RC score remains 81.25%** (53 weighted gates, 36 accepted, 17 partial). This cycle provides *local functional improvement only*; browser/production evidence must be collected in GitHub before crediting a bounded B1 recovery subgate.

**Functional implementation:** `apps/web/src/live-connection.ts` replaces the inline WebSocket retry effect with a single-owner transport shared by presenter and participant views. It fences retired socket events so late error/close/snapshot callbacks cannot alter a newer connection; on network offline it cancels pending timers and closes the retired socket, while online reconnects exactly once. It refuses reconnect after policy/authz closes `4003` or `1008`, shows a clear live-access-denied message, and bounds a stuck connection handshake to 15 seconds. Retry backoff is exponential with 20% per-client jitter and 30-second maximum to limit recovery storms. User-selected session IDs are checked before applying snapshots. Callback refs prevent stale React callback captures across rerenders. Dispose cancels timers and closes the socket without reactivating it. The backend live socket auth, WebSocket routes and PostgreSQL data are unchanged.

**Evidence:** 9 deterministic WebSocket lifecycle tests (including the actual event-order race) and strict standalone TypeScript DOM contract; full Node backend and web unit suites, Python contract/inventory checks required. No actual GitHub/real-browser end-to-end for this uncommitted code yet. Server network fault injection, production long-running reconnection SLO and human acceptance remain open. `rc_strict=false`, `publish_image=false`.

**Next checks after maintainer commit:** standard and extended CI on cycles 49–54, including `kubernetes_tls_test=true`, `capacity_slo_test=true`, `cross_browser_test=true`, `publish_image=false` and `rc_strict=false`; validate real browser rejoin under network loss before moving B1. The assistant made no commit, push, tag, or release.

---

# Quorivio 0.1.0-dev — RC 53 — production Content Security Policy and browser permissions (30 October 2026)

**Baseline:** cycle 52 cumulative, no maintainer commit since `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`. This package includes cycles 49–53. **Certified RC remains 81.25%**: security approval requires real GitHub runtime acceptance and independent review.

## Product changes

`apps/api/src/security-headers.ts` defines an enforcing production CSP (only when `NODE_ENV=production`), disallowing inline/eval scripts and executable objects, binding WebSocket endpoints to the configured browser-facing origin, and retaining same-origin frames required for presenter/rehearsal previews. Image/media schemes preserve local uploads, QR/data images, optional HTTPS background media, PDFs and blob resources. Widget-specific React inline CSS remains explicitly allowed; no relaxation is made to script execution. `Permissions-Policy` disables camera, microphone, location, payment, USB and browsing-topics but leaves presenter fullscreen unaffected. The Vite development server does not use this production policy.

## Verification

Five Node tests enforce policy boundaries and URL validation; four Python contracts cover API integration, unsafe-script denial, media compatibility, and real-container smoke checks. Both `ci_oci_runtime_smoke.sh` and `ci_rootless_podman_smoke.sh` now **fail closed** unless a running production container actually serves both headers. Existing backend/frontend Node tests must remain green; GitHub container gates, real browser integration and external security sign-off **have not yet been run** for this change.

The `81.25%` certified RC score is unchanged; B4 HTTPS KIND, B4 global 500-user SLO, external RWX and D4/D6 independent approvals remain pending. Recommend standard CI first, extended OCI+Podman+browser tests next, with `publish_image=false` and `rc_strict=false`.

---

# Quorivio 0.1.0-dev — RC cycle 52: global 500-client latency SLO evidence (30 October 2026)

**Last verified standard/extended GitHub runs:** `41120048115` / `41123318359` (green on cycle-48 baseline). **Maintainer-confirmed baseline:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (cycle 48); cycles **49–52 are all uncommitted** and included cumulatively. Verified RC remains **81.25%**, 53 weighted gates (36 accepted, 17 partial). `rc_strict=false` until the independent residual gates pass; this patch carries no unverified percentage credit.

**B4 capacity improvement:** `capacity_slo_test` is a separate manual opt-in running 500 independent participants against disposable CI PostgreSQL, 40s ramp and 90s hold. Numeric-only per-client join and first-WebSocket-snapshot samples allow the aggregator to calculate *true global p95 across shards* rather than misleading averages of shard p95s. Strict mode requires complete sample coverage, a single presenter observer with peak >=95%, no errors, consistent reported quantiles, sufficient hold, and default p95 bounds of 5000ms join / 8000ms first snapshot. The historical bounded `capacity_test` is unchanged. No participant names, responses or IDs are included in new sample arrays.

**Evidence/limits:** new Python simulated multisource contracts and Node backend/web suites exercised locally. Actual GitHub 500/90s sustained acceptance is NOT run and is NOT a real distributed-host load SLO. No independent physical-device, public TLS, CSI RWX, network faults or audit sign-off is claimed. Documentation: `docs/RC52_SUSTAINED_500_SLO.en.md`.

**Next maintainer CI:** first standard, then extended with `capacity_slo_test=true`, `kubernetes_tls_test=true`, `publish_image=false`, `rc_strict=false`. Credit a narrow new B4 SLO scope only after real opt-in success and review; do not re-credit existing `B4-LOAD`. Assistant does not commit, push, tag, or publish.

---

# Quorivio 0.1.0-dev — cycle 51 continuation handoff

**Confirmed maintainer baseline:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`. Cycles **49 + 50 + 51** uncommitted and cumulatively included. Current verified RC **81.25%**, 53 gates, 36 accepted/17 partial. CI standard and extended were green at the committed cycle-48 baseline. No assistant commit, push, tag or release.

**Cycle 51 fix:** two-worker HTTPS opt-in test had an invalid positional second argument for a keyword-only `https_ingress_probe`. Fixed this and narrowed expected untrusted-chain TLS errors so invalid hostnames or expired certs cannot falsely pass. Added AST keyword-only call-site contract plus fully mocked KIND `main()` tests for *both* NGINX and HAProxy Technologies, covering bad Host, untrusted chain, two pod origins, pod deletion and recovery probe. Prior real Node loopback TLS tests still PASS. See `docs/RC51_HTTPS_ACCEPTANCE.it.md` for scope, commands and remaining risks. New Kubernetes HTTPS jobs have **not yet passed on GitHub**; do not grant further RC credit yet.

**Next steps:** maintainer commits cycles 49–51 together; run standard CI then manual extended opt-in `kubernetes_tls_test=true`, `publish_image=false`, `rc_strict=false`. Inspect both HTTPS job logs. Only then reconsider a bounded +0.25 point B4 TLS split (target 81.50%) if evidence is independent of already credited HTTP and OCI tests. Continue RWX verification using independent CSI/NFS hardware and independent security/accessibility reviews. Keep only the most recent Quorivio cumulative archives per user retention preferences, but never remove service tools/docs.

---

# Quorivio 0.1.0-dev — RC cycle 50 — live HTTPS ingress with disposable trust tests (30 October 2026)

**Last user-confirmed commit:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (cycle 48). **Cycle 49 not yet committed** and included here. Official RC **81.25%**, 53 gates (36 accepted, 17 partial): no unverified percentage promotion. The opt-in `kubernetes_tls_test=true` launches **NGINX and HAProxy Technologies** on separate ephemeral two-worker KIND tests. Each uses a short-lived self-signed leaf with a valid SAN, a trust-pinned Node HTTPS client with strict TLS/SNI, wrong HTTP Host rejection, untrusted-certificate rejection, and a live HTTPS check after an application pod replacement. TLS keys are not printed, and the workflow never targets external Kubernetes clusters or publishes images. Independent physical hosts, public-CA TLS, real CSI/NFS RWX, degraded network testing and independent operator/security reviews remain open.

**Local evidence:** focused Python and a real Node client against a disposable local TLS server pass; GitHub/KIND execution of the new optional matrix still pending. A narrowly scoped subset of residual B4 may be reconciled only after both live HTTPS CI jobs pass, without re-crediting existing HTTP ingress tests.

---

# Quorivio 0.1.0-dev — RC cycle 49 — verified HAProxy and real RWX data-path probe (30 October 2026)

**Maintainer baseline:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (cycle 48). Standard run `41120048115` and extended run `41123318359` are green; all 11 extended jobs succeeded. Confirmed HAProxy Technologies two-worker KIND job `124297991439` earns an independent, bounded B4 subgate. RC matrix now **81.25% — 53 gates: 36 accepted, 17 partial**. This credit excludes preexisting NGINX, OCI, Firefox/WebKit and ClamAV evidence. Strict RC still **NOT READY** (`rc_strict=false`).

**Cycle 49 work not yet GitHub validated:** added an explicit Kubernetes cross-node RWX verification tool. Read-only checks require exact kubectl context and a bound, network-capable RWX volume mounted by two ready pods on distinct nodes. A separate `--confirm-write` performs two-way real data transfer in random temporary files under the mounted assets path; best-effort cleanup runs in both pods. Tests validate dangerous negative conditions, command scoping, and cleanup. This tool has **not** been run on an actual user cluster and adds no RC credit. Full operational guide: `docs/RC49_HAPROXY_CROSS_NODE_RWX.en.md` and `.it.md`.

**Open:** independent physical host/CSI RWX, fault-injected storage and network loss, TLS public chain, sustained capacity/SLO, real assistive devices and independent GDPR/AGID/security review. CI standard and extended to be rerun after maintainer commit, with no automatic commit/push/tag.

---

# Quorivio 0.1.0-dev — RC cycle 48 — historical SHA-256 integrity recovery (30 October 2026)

**Last confirmed maintainer commit:** `40e42964063e93aed6cc4a4f7a5fc9e5feebaa15` (through cycle 47). **Formal RC remains 80.75%**, 52 gates (35 accepted, 17 partial); cycle-48 code has not been verified on GitHub.

**Two CI failures, same root cause:** standard run `41117244123` (job `124274549345`) and extended run `41117884354` (job `124276729019`) both stopped in the SHA-256 inventory verification because `RC_CYCLE42_PACKAGE_INVENTORY_20261030.json` was absent. The cycle-43 manifest was also missing and would have failed next. Previous historical verifiers in the same logs passed. Neither failure establishes a Vite, PostgreSQL, Chromium, or ClamAV regression; the fatal error is `FileNotFoundError` for the historical manifest.

**Fix:** restored original cycle-42 and cycle-43 manifest bytes, without regenerating history, from the respective cumulative ZIPs. Frozen SHA-256 values are `dcb77af5 59e66a61 d950ce37 77aabcc4 2a4de61f 5db1af18 1d9b9c44 07a78950` and `109cfa85 3e83d2e8 32fbf975 495ff6f6 97a36d2e f7e89d71 6579a6ef 4b4030a3`. CI now checks every referenced manifest file and whether required evidence is Git-tracked (when a repository checkout exists), before expensive Python tests and the checksum verification step. Cycle 47 becomes historical and cycle 48 is the current checksum inventory. New regression tests guard against missing historical receipts.

**Limits:** prior build and runtime evidence does not certify new changes. A new maintainer commit and complete standard CI are still required before promotion. Do not commit/push/tag/publish automatically. Run standard CI with `publish_image=false`, `rc_strict=false`, then extended CI when green.

---

# Quorivio 0.1.0-dev — RC cycle 47 — PostgreSQL editor portal selector hotfix (30 October 2026)

**Last maintainer commit:** `5163e5a5b4685348810ef24067538967a1bbb536`. Cycles **46 and 47 are still uncommitted** and must be delivered cumulatively. **Formal RC remains 80.75%**: 35 accepted gates and 17 partial; `rc_strict=false`. No credit for local code.

**Extended CI evidence:** run `41115332748`, quality job `124267958170`, ran on the previous committed source, not the pending cycle 46. It passed real PostgreSQL background-library collaborator ownership, editor CAS, audience Chromium and isolated title-menu checks. It failed in `tools/ci_browser_editor_postgres.py` because the test searched beneath `.widget-canvas-item` for a context menu which production React deliberately portals to `document.body` to avoid widget clipping.

**Change:** right-click the widget as before, then locate the exact accessible menu at page scope. Assert exactly one menu, visible actions, successful title edit, menu dismissal, and transition out of editing. Preserve all existing real PostgreSQL autosave, CAS, three-way merge, explicit same-field resolution and layout export assertions. New Python contracts prevent reintroducing the wrong nested locator; no production UI behavior was altered.

**Not yet GitHub-certified:** real PostgreSQL/Chromium full editor acceptance on the patched script; subsequent container gate was skipped. This run does not certify cycles 46–47. No assistant commit, push, tag or publication.

---

# Quorivio 0.1.0-dev — RC cycle 46 — Python quality-gate regression fix (30 October 2026)

**Verified RC unchanged: 80.75% (52 gates: 35 accepted, 17 partial).** Latest GitHub commit observed: `5163e5a5b4685348810ef24067538967a1bbb536` (cycle 45). Run `41114355433`, quality job `124264578469`, executed 1,278 Python tests with **two outdated contract checks** failing in `test_canvas_context_menu.py` and `test_rc_cycle35_verified_bootstrap.py`. The other 1,276 tests passed, but the job failed before the compiled-frontend Chromium acceptance and container gate could run.

**New, not yet CI-certified:** the canvas test now checks current `WidgetCanvas` media and collaborator-background props even when JSX is wrapped across lines, and verifies the background-library callbacks remain wired. The immutable cycle-35 GitHub evidence receipt continues proving the original commit. Current status documents instead must expose the latest CI run, committed baseline, known unaccepted gates and `rc_strict=false`; a historic commit hash no longer needs to appear in the first 4,000 characters of every current handoff.

**Remaining risks and limitations:** this hotfix changes tests and documentation, not application runtime behavior. Full Python regression, standard CI, real compiled-frontend Chromium startup and the container gate for the new package are still pending maintainer CI. The 17 partial gates remain open (including production RWX, HAProxy, public TLS, device/accessibility and independent GDPR/AGID/security reviews). **No image publication; `publish_image=false`, `rc_strict=false`.** No assistant commit/push/tag/release.

---

# Quorivio 0.1.0-dev — RC cycle 45 — Chromium on compiled frontend assets (30 October 2026)

**Verified RC remains 80.75% (52 gates: 35 accepted, 17 partial).** GitHub run `41110214420`, job `124250386166`, on commit `383c273deb53d368d6b8a1d57ab5c623591bcc7a` completed TypeScript/Vite builds, 500 backend and 84 frontend Node tests and the real ClamAV runtime test. The full Chromium editor acceptance failed with `root_children=0, page_error_count=0` before authenticated navigation, meaning React never mounted. The dependent container build was skipped.

**New change (not yet GitHub certified):** the full editor CI now serves the immutable compiled distribution through `vite preview` rather than Vite's development optimizer and HMR server. `tools/ci_built_frontend_asset_probe.py` verifies the built HTML, fingerprinted JavaScript response and React mount before the existing editor suite. Logs expose only safe asset-type/status counts, not private cookies, requests, tokens or stack traces. The editor still verifies reload-based autosave restoration but no longer reloads to disguise an optimizer startup failure.

**Verification and limits:** local Node suites, focused Python tests, Python and YAML parsing were exercised. Local Chromium is explicitly blocked from loopback HTTP by this environment (`ERR_BLOCKED_BY_ADMINISTRATOR`), preventing an actual browser end-to-end run here. The exact reason for the previous blank DOM has not been definitively proven; switching to prebuilt assets removes one plausible source of variability and makes the next run more diagnostic. No score credit or assistant commit/push/tag/publish.

**After committing:** standard CI with `browser_test=true`, `publish_image=false`, `rc_strict=false`; require `PASS Chromium built frontend` and `PASS Chromium editor mock fidelity`. Extended tests can follow after the standard gate turns green.

---

# Quorivio 0.1.0-dev — RC cycle 44 — Chromium initial mount and cookie top-layer CI hotfix (30 October 2026)

**Last maintainer commit:** `1857ebb22560d0ddcc1fec439dfe865eb0183e98` (cycle 43). Standard workflow `41103165554` passed 500 API and 84 web Node tests, TypeScript/Vite production build, and the independent real ClamAV job. The quality gate failed in `tools/ci_browser_editor.py` waiting for the `Apri sessione` button; the attached failure screenshot is fully white, so the frontend had not visibly mounted when the test timed out. The exact underlying JavaScript or cold Vite startup fault was not recorded in this run and must not be guessed.

**Cycle 44 changes (not yet CI-verified):** mock Chromium editor now explicitly waits for React `#root .app` and retries once after a full navigation to absorb a Vite cold dependency-optimizer reload, otherwise failing with a precise frontend-mount diagnostic. The native modal cookie notice is acknowledged *before* querying navigation controls on desktop and mobile. The real PostgreSQL editor acceptance similarly handles the modal before querying the page, with a cookie-aware readiness check. Added contract tests and a self-contained real-Chromium regression proving modal pointer interception and manual acknowledgement; no production cookie bypass or force-click was introduced. Do not claim that the full browser editor acceptance passes until the next GitHub run.

**RC score unchanged: 80.75%** (52 gates, 35 accepted, 17 partial). `rc_strict=false`, `publish_image=false`. Commit only after review; no assistant commit, push, tag or publication.

---

# Quorivio 0.1.0-dev — RC cycle 43 — frontend TypeScript CI hotfix (30 October 2026)

**Baseline committed by maintainer:** `55b5ab70dcc3ee772b47c5acd498b47d58874441` (cycle 42). Standard Actions run `41099464679` fails only on `Production quality gate` / `Compile frontend and backend`: frontend TS2339 on `main.tsx` for missing `allowAnswerChange` and `showEmail` in the editor's local widget-history draft type. Backend and frontend Node tests passed (500/500 and 84/84) before the compile step; downstream container build was skipped, not independently failing.

**Hotfix (uncommitted):** the editor draft now derives `allowAnswerChange` and `showEmail` from the server-validated `PageDesign` widget type through `Pick<>` instead of duplicating these permissions. A type-level parity contract and regression tests cover both saved fields. The historical cycle-42 inventory remains immutable; cycle-43 replaces the current CI catalog. No changes were made to the response/privacy business rules.

**Verification limits:** targeted Python contracts pass; the standard GitHub TypeScript/Vite build has not been re-run on this hotfix. Local npm installation is unavailable in the environment (offline cache misses / npm installer failure). Do not claim that the compile gate passes until GitHub confirms it. Formal RC completion stays **80.75%** (52 gates, 35 accepted, 17 partial); `rc_strict=false` and `publish_image=false`.

**Next maintainer action:** commit/push the cumulative cycle-43 package, rerun standard CI; optional browser/HAProxy checks after the production quality gate succeeds. Assistant made no commit, push, tag or release.

---

# Quorivio 0.1.0-dev — cycle 42: selectable timer faces and custom-fill precedence — 30 October 2026

**Formal RC completion: 80.75%** (52 gates: 35 accepted, 17 partial), unchanged. Cycles 34–42 remain cumulative and uncommitted relative to confirmed commit `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`.

**Changes:** introduce three persisted, server-validated timer faces (`hourglass`, `dial`, `digital`) for Timer and Timed Quiz widgets; they use the same actual countdown on editor, rehearsal, presenter and participant surfaces. The digital face has a dedicated progress bar. Restore author control of transparent/opaque fills: `fillNone`, `fillOpacity` and explicit solid fill suppress decorative background images, including fully transparent opacity. Motion effects respect reduced-motion preferences.

**Testing:** 500/500 API Node tests; 84/84 web Node tests; targeted persisted-schema, input-allowlist, style and surface parity regressions. Full TypeScript/Vite build and live-browser acceptance remain pending. Historical cycle-41 receipt remains immutable; cycle-42 current inventory and CI verification required before committing. Assistant performed no commit, tag, push or publication.

---

# Quorivio 0.1.0-dev — RC cycle 41 — 30 October 2026 — per-widget artistic themes

**Formal RC score remains 80.75% (52 gates: 35 accepted / 17 partial).** Latest confirmed maintainer commit: `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`; cycles 34–41 are cumulative, not yet committed. Implemented server-validated per-widget themes (`studio`, `glass`, `playful`, `minimal`) and optional effects (`none`, `float`, `glow`, `tilt`), with four-surface render parity and precedence for authored fill/images/transparency. Static timer artwork is visible in the editor while timer countdown remains live in presentations. The CSS provides per-kind visual accents and honours reduced-motion settings. Historical source inventory for cycle 39 preserved, new cycle 41 manifest introduced for CI. Validation: 500 API Node and 81 frontend Node tests passed; 4 new Node and 4 Python contract tests passed. Full browser production build and cross-browser manual acceptance still pending. See `docs/RC_WIDGET_ART_THEMES_CYCLE41.en.md`. No commit/push/release/publish by assistant.

---

# Quorivio 0.1.0-dev — RC cycle 40 — artistic widget styling (30 October 2026)

**Formal completion unchanged: 80.75%** (52 gates: 35 accepted, 17 partial). This cycle has not yet been verified by a new GitHub CI run or by the user's real-browser acceptance checks. Last confirmed commit: `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`; cycles 34–40 remain cumulative and uncommitted.

**Implemented:** widgets on the editor canvas, rehearsal panes, presenter page and participant page now use a richer per-kind visual language: card-like surfaces with depth, highlights, chromatic accents and semantic decorations for timers, questions, quizzes, reactions, results, presenter profile, QR, media, text, sticky notes, participant counters and audience questions. The timer was redesigned with a progress ring, hourglass motif and high-contrast digits, plus an urgent state near expiry. Result clouds and tracks were also refreshed for better readability and stronger visual appeal. The same skins are visible inside the editor canvas so presenters preview the look while composing slides.

**Local verification:** shared render points were checked for the new `data-widget-kind` attributes and no obvious serialization regressions were introduced. Full TypeScript/Vite build, real-browser tests, full Node suites and user confirmation still need to run after commit. No new RC points assigned.

**After commit:** run standard CI with browser coverage (`browser_test=true`, preferably `cross_browser_test=true`) and manually validate timer, question/quiz, results, profile and QR widgets in editor, presenter preview, participant preview and live pages.

---

# Quorivio 0.1.0-dev — RC cycle 38 — Presenter/participant state isolation (30 October 2026)

**Verified formal RC score remains 80.75%** (52 gates: 35 accepted, 17 partial). Latest confirmed maintainer commit `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`; cycles 34–38 cumulative and uncommitted. The new implementation is not credited until independent CI/browser acceptance.

**Implemented:** presenter-side interactive questions/quiz/reactions/rating are neutral; only the associated Results widgets show confirmed, aggregate rehearsal responses, with stable seeded background counts. One participant's reaction can replace their previous choice in the local preview and actual PostgreSQL reaction API; a repeat vote never counts twice. Questions and quizzes reject repeat answers by default, while an explicit per-question option allows updates, serialized by row locks and bounded by the timed quiz deadline. Checkbox/radio selectors appear left of their labels. Profile widgets show display name, optional photo and *opt-in published email* only; email is disclosed for the chosen presenter on the active session page and not for all collaborators. The editor and rehearsal can preview authenticated profile details before public activation.

**Limits:** local Node/Python unit and contract tests only; no actual PostgreSQL, Chromium, full TypeScript/Vite production build, native mobile or real HAProxy acceptance on this code yet. Reaction storage is page-scoped, not independently per reaction widget. Keep `publish_image=false`, `rc_strict=false`. No assistant commit, push, tag or publish.

**CI:** standard quality plus `browser_test=true` and `cross_browser_test=true`, optional `kubernetes_haproxy_test=true`. Verify manually side-by-side rehearsal votes/results, reaction change, default immutable and explicitly editable answers, profile consent, and radio/checkbox placement on desktop/mobile.

---

# Quorivio 0.1.0-dev — RC cycle 37 — Editor interaction and page-save hotfix (30 October 2026)

**Formal RC completion remains 80.75% (52 gates: 35 accepted, 17 partial).** No independent CI or live browser acceptance exists yet for the new editor changes. Maintainer-confirmed commit baseline remains `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (cycle 33); cycles 34–37 are cumulative and uncommitted. No assistant commit, push, tag, publication or release.

**Four reported problems, with screenshots:** (1) editor widgets were inheriting pale foreground from the dark shell; the unconfigured text color is now explicitly black in the shared widget typography model and editor CSS, preserving user-selected colors; (2) widget contextual menus were rendered in a clipped widget, now portaled to `document.body` and positioned inside the viewport for right click, touch hold and keyboard; (3) presenter/participant/dual preview potentially trapped the editor, now has a closable React error boundary, escape/background dismissal, stable remount avoidance and a 1-second refresh cadence; (4) changing a question to multiple choice auto-seeds two valid options, with authoring-side validation against the same `validPageDesign` contract used by the API before autosave. Both the original two-choice model and new default options pass the backend validator.

**Local evidence:** Node's TypeScript strip-mode tests for five new cases pass; 180 Python editor regression contracts pass, plus 20 targeted portal/rehearsal contracts. TSX parser reports no syntax errors. The Chromium acceptance script now checks default black text and an unclipped body-portal context menu, while retaining existing preview/keyboard tests; this browser run has NOT been executed locally (no npm/Playwright dependencies). No remote POST/real PostgreSQL acceptance or full production Vite/TypeScript build was performed for this cycle. The error boundary and local prevention are protective changes, not a substitute for actual user retesting. New code uncredited in the RC score.

**CI after the user's commit:** quality gate with `browser_test=true`, preferably alongside `cross_browser_test=true`, `publish_image=false`, `rc_strict=false`; run the existing full backend/database tests and repeat the four manual workflows in the editor. HAProxy opt-in remains pending on actual KIND until separately executed. Retain all prior SHA-256 evidence catalogs immutably and use cycle37 current-source integrity gate.

---

# Quorivio 0.1.0-dev — RC cycle 36 — HAProxy Technologies multi-worker ingress acceptance (30 October 2026)

**Formal RC completion: 80.75% (35 accepted, 17 partial of 52 gates), unchanged.**
The most recent maintainer-confirmed commit is `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (cycle 33). Cycles 34–36 are **cumulative and uncommitted**. The independent successful GitHub run `41048187760` established the accepted bounded ClamAV, NGINX ingress, PostgreSQL bootstrap and graceful-drain evidence credited by cycles 34 and 35; **no new CI evidence** exists for cycle 36.

**Functional implementation:** The existing two-worker KIND smoke now supports `--controller nginx` (unchanged default) or `--controller haproxytech`. The HAProxy mode installs official HAProxy Technologies Kubernetes Ingress Controller chart version `1.54.3` via Helm, bound to a private ClusterIP Service and `haproxy` IngressClass, then generates Quorivio ingress manifests using the real wizard's HAProxy Technologies mode. The runtime acceptance verifies strict two-worker distribution, PostgreSQL 18 readiness, disposable runner-only cross-worker bind visibility, real HTTP virtual-host routing, rejection of unknown hosts, API pod replacement, surviving ingress and asset visibility after recovery. This test is opt-in through `kubernetes_haproxy_test=true`, never publishes an image and does not require access to any real cluster. Sanitized failure diagnostics contain only Kubernetes resource status. The existing NGINX acceptance remains unchanged.

**Local proof:** Python source compiles, workflow YAML parses and 38 focused tests cover the wizard-generated HAProxy class/legacy annotation, private Service selection, pinned official Helm chart and default NGINX compatibility. The monolithic Python regression and the attempted parallel per-module replay did not complete cleanly in this environment; do not treat them as a full-suite pass. The actual HAProxy controller is **not** available locally and must pass GitHub CI before receiving gate credit. Running two KIND worker containers on the same physical host with a shared bind mount is not a real NFS/CSI RWX or multi-machine disaster recovery test. Public TLS, the separate HAProxy community controller, sustained SLO, real devices, independent AGID/GDPR, penetration testing and operator approvals remain open. **RC strict and image publishing stay disabled.**

**CI after user commit:** first the standard quality/container gates, then manual `kubernetes_haproxy_test=true`, optionally alongside `kubernetes_multinode_test=true` and `clamav_runtime_test=true`; set `publish_image=false` and `rc_strict=false`. The new job may need CI environment iteration, which is not counted as a pass in this local package.

---

# Quorivio 0.1.0-dev — RC cycle 35 — 30 October 2026 — 80.75% (+0.50pp)

**Maintainer-committed baseline:** `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (cycle 33); cycle 34 and 35 remain uncommitted. GitHub Actions `41048187760` quality job `124037870206` passed *actual* PostgreSQL 18 simultaneous bootstrap with a single administrator and two ready API replicas, plus rolling `SIGTERM` readiness `503`, WebSocket `1012` and a healthy surviving replica. These distinct verified checks had not been credited separately. They are not the same as B1-WS/B1-RECONNECT or B4-KIND-INGRESS-RECOVERY.

**Verified RC score:** **80.25 → 80.75%**. Keep the original B1 weight of 2 split into B1 residual 1 (partial), `B1-BOOTSTRAP-PG18` 0.5 (accepted) and `B1-GRACEFUL-DRAIN` 0.5 (accepted). 52 gates total: 35 accepted, 17 partial; all weights total 100. This counts *only* the proven prior commit, not cycle34 or cycle35 code.

**New uncommitted code (not scored):** `withBootstrapLock` permanently removes a connection from the pool if lock acquisition or session setup fails; this avoids recycling an uncertain PostgreSQL session retaining `lock_timeout=120s` or an indeterminate advisory lock state. Additional Node regressions cover acquire timeout, setup failure, post-lock reset failure and false unlock acknowledgements. Tests on actual PostgreSQL 18 must be rerun in CI after user commit. No code or CI change is accepted merely because it was written locally.

**Local validation cycle35:** 18 nonoverlapping Python groups, 1,251 executed, no failed groups; 8 Node bootstrap-lock cases pass. Full Node workspace suites and TypeScript/Vite build not executed locally because npm dependencies are unavailable. Cycle35 source and ZIP hash catalog must be verified before shipping.

**Outstanding:** independent multi-machine CSI/NFS RWX and failover, production TLS and HAProxy, real ARM hardware, sustained SLO with faults, browser/device and screen reader reviews, independent GDPR/AGID and security checks. Strict RC remains blocked; no image publish, push or tag. **CI after commit:** run standard quality (including PostgreSQL two-process bootstrap) and opt-in extended `kubernetes_multinode_test=true`, `clamav_runtime_test=true` with `publish_image=false`, `rc_strict=false`.

---

# Quorivio 0.1.0-dev — ciclo 34 — 30 ottobre 2026 — RC 80,25% (+1,00 pp)

**Baseline committata:** `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`. Il workflow esteso https://github.com/desalvo/quorivio/actions/runs/41048187760 è verde (quality, container, ClamAV, Kubernetes multiworker NGINX), pubblicazione disattivata. **RC formale: 80,25%, 50 gate (33 accettati, 17 parziali). NON RC READY.**

**Riconciliazione basata esclusivamente su GitHub:** `C4-AV-INSTREAM` (peso 1 accettato) separato da C4 parziale (peso da 3 a 2); job `124037870523` verifica `PING/PONG`, scansione INSTREAM ClamAV effettiva, file pulito ed EICAR attraverso il client applicativo. `B4-KIND-INGRESS-RECOVERY` (peso 1 accettato) separato da B4 parziale (peso da 3 a 2); job `124038997005` verifica due worker KIND distinti, PostgreSQL 18, condivisione di file tramite bind temporaneo, NGINX reale con Host, recupero dopo sostituzione di un pod. Risultato 79,25 → 80,25, conservando il peso totale 100; i 17 gate residui non sono promossi.

**Nuovo sviluppo NON conteggiato nel punteggio:** scanner ClamAV con handle `O_NOFOLLOW | O_NONBLOCK`, solo file regolari, streaming dall'handle aperto, controllo `size/mtimeNs/ctimeNs` dopo scansione per rifiutare link simbolici e modifiche in-place prima del risultato pulito; nuovi test Node e regressioni Python. Non certificato da nuova CI sul codice del ciclo 34.

**Limiti espliciti:** non ancora verificati cluster multi-macchina con storage CSI/NFS RWX di produzione, HAProxy reale, TLS pubblico, macchine ARM64 fisiche, upload HTTP concorrenziali al ClamAV gestito, collaudo dispositivo fisico, revisione GDPR/AGID e sicurezza indipendente. Il test KIND è su singolo host, il test ClamAV su server temporaneo. Non attivare `rc_strict` o pubblicare immagini. Nessun commit/push/tag/release a cura dell'assistente.

**Commit suggerito (solo ciclo 34):** `feat(rc): reconcile verified ClamAV and ingress failover gates and harden antivirus file scanning`

**Verifiche locali ciclo 34:** 12/12 test scanner mirati, 492/492 backend Node, 65/65 frontend Node, 1.243 test Python eseguiti in otto gruppi disgiunti (1 saltato, 0 falliti). Inventario corrente SHA-256 e ZIP validati. Build TypeScript/Vite sul nuovo codice non verificata localmente (dipendenze npm mancanti); nuova Full CI dopo commit necessaria. I test ClamAV e multiworker reali che accreditano il punteggio sono quelli del commit precedente, non del codice modificato nel ciclo 34.

---

# Quorivio 0.1.0-dev — RC cycle 32 — 30 October 2026 — production antivirus/Kubernetes parity

**RC formal 79.25%** (48 gates: 31 accepted, 17 partial). Last maintainer-confirmed Git commit `016beea25d5e2d2fab21b0730aa15baf0b573e12` (cycle 28); cycles 29–32 remain cumulative and uncommitted. No independent GitHub CI is yet available for these changes, therefore no score increment is justified.

**Implemented:** `malware-scan.ts` requires an antivirus on *every production upload* even with an omitted or explicitly false flag; explicit opt-out is reserved for non-production. The clamd INSTREAM client rejects premature clean results, midstream disconnects, excessive replies and overall deadlines, with no unobserved response rejection. Managed Kubernetes wizard now creates private ClamAV Deployment/ClusterIP/NetworkPolicy and configures mandatory `QUORIVIO_AV_REQUIRED` by default; external mode requires a validated private hostname and removes previous managed resources when switching. Helm's managed ClamAV memory limit is raised to 4Gi and operator instructions updated. CI discovers the new Node and Python protocol/configuration contracts automatically.

**Limits:** local mock scanner and rendered manifests are NOT a real ClamAV/signature database acceptance, live external scanner validation, multi-node RWX/HAProxy/TLS acceptance or independent security audit. The managed antivirus Deployment runs one replica and can be temporarily unavailable while updating signatures; during downtime uploads are refused, not accepted. The official container requires sufficient resources; production Pod Security compatibility must be tested. `StreamMaxLength` must be configured in real clamd to match accepted upload policy. New opt-in `clamav_runtime_test=true` starts a disposable real ClamAV image, scans a clean file and confirms refusal of the harmless EICAR test signature; this job has not run yet. CI workflow `kubernetes_multinode_test` intentionally uses an unconfigured *external* mock scanner hostname because it tests topology/Ingress, not AV; it must not be represented as antivirus acceptance.

**Next action:** after the maintainer commits, run standard Full CI (including new AV protocol tests), plus opt-in Kubernetes multiworker KIND. To credit operational C4/D4 requirements, also execute a genuine ClamAV upload/detection test and independent multi-replica shared storage security acceptance. Keep `rc_strict=false` and `publish_image=false`. No commit, push, tag or publication by assistant.

---

# CURRENT HANDOFF — cycle 31 (2026-10-30)

**Source:** cumulative cycle-30 package + cycle-31 PostgreSQL bootstrap serialization and CI acceptance. User will commit later. Last explicitly confirmed Git commit `016beea25d5e2d2fab21b0730aa15baf0b573e12` (cycle 28).

**Formal RC** 79.25% (48 gates, 31 accepted and 17 partial), unchanged until independent acceptance. Run the normal production quality gate after commit: it now includes simultaneous fresh PostgreSQL 18 schema/bootstrap from two compiled API processes (atomic one-admin check). Cycle29 multiworker KIND + NGINX still requires opt-in `kubernetes_multinode_test=true`. Use `publish_image=false`, `rc_strict=false`. No external CI for cycles 29–31 has been claimed. Do not increment scoring or sign off external audit from local fixtures.

**Work completed:** `apps/api/src/bootstrap-lock.ts`, protected `initialize` in `server.ts`, atomic first-admin provisioning, `tools/ci_concurrent_bootstrap_postgres.py`, Node/Python contracts, CI workflow and bilingual docs. Tested local lock logic and source contracts; PostgreSQL CI check still pending on remote runner.

**Limits:** no real CI of fresh two-process PostgreSQL, native ARM, production RWX/NFS/CSI, true PostgreSQL failover, HAProxy/TLS or independent accessibility/GDPR/security approval. Strict RC not ready. No assistant commit/push/tag/publication.

---

# CURRENT HANDOFF — cycle 30 (2026-10-30)

**Source base**: cumulative cycle-29 zip, plus cycle-30 operational HA additions. Last explicitly user-confirmed Git commit is `016beea25d5e2d2fab21b0730aa15baf0b573e12` (cycle 28). No cycle-29 or cycle-30 commit made by assistant.

**Local regression**: Python 1,218 tests, 1 skipped, zero failures; 22 focused cycle-30 tests PASS. Node build and Kubernetes runtime not run locally.

**Formal RC readiness**: 79.25%, 48 gates (31 accepted/17 partial). Do not increase on local-only tests. Live 2-worker KIND NGINX CI path introduced in cycle 29 has not yet been GitHub verified. Must execute `kubernetes_multinode_test=true`, `publish_image=false`, `rc_strict=false` after maintainer commits cumulative changes. Cycle30 `k8s_operational_gate.py` checks live real-cluster API but has not run against a production cluster. PostgreSQL bundled StatefulSet is single-replica, not database HA. See `docs/K8S_OPERATIONAL_PREFLIGHT_RC30.en.md` and latest development status.

**Next**: monitor CI for KIND multiworker first; if green, validate real ingress, independent RWX CSI and data persistence on two independent machines, HAProxy, database HA, TLS, ClamAV and operator reviews. Do not create arbitrary narrow gate splits for a higher score.

---

# Quorivio 0.1.0-dev handoff — RC cycle 29 (30 October 2026)

**Last maintainer-confirmed commit:** `016beea25d5e2d2fab21b0730aa15baf0b573e12` (cycle 28). Cycle-29 ZIP has NOT been committed, tagged, pushed or published by the assistant.

**Measured RC readiness: 79.25%** (+0.25 percentage points from 79.00%), strictly from newly recognized successful CI evidence for the scoped D3-OCI-ROOTLESS-RUNTIME subgate: run `40980312270` / job `123820527902` (OCI AMD64 + emulated ARM64), run `40982728705` / job `123827805762` (rootless Podman/PostgreSQL 18). 48 gates: 31 accepted, 17 partial. Strict RC remains blocked.

**New cumulative uncommitted work:** correct HTTP PUBLIC_BASE_URL when TLS disabled; opt-in `enforce_node_diversity` with strict separate-node scheduling and RWX guard; Helm rolling update/PDB/RWX validation and `enforceNodeDiversity`; opt-in `kubernetes_multinode_test` with 2-worker KIND, PostgreSQL 18, real NGINX ingress, cross-worker file visibility and pod replacement. Test RWX uses a shared single-runner bind mount, NOT actual CSI/NFS. Physical ARM64, HAProxy, real TLS, independent multi-machine CSI, GDPR/AGID/security/accessibility reviews remain pending.

**Local evidence:** 1,193 Python unit tests executed (one skipped), no failures; current source and cumulative ZIP SHA-256 verified. TypeScript/Vite and live multiworker KIND have not been executed locally due missing npm runtime dependencies and container toolchain.

**Next manual GitHub run:** `kubernetes_multinode_test=true`, `publish_image=false`, `rc_strict=false`; other opt-in gates if helpful. Do not credit a new multiworker gate before a passing real CI run. Assistant never commits or publishes. Suggested next commit: `feat(k8s): add strict multi-node scheduling, live NGINX ingress CI and Helm HA guards`.

---

# Software completion handoff (2026-10-24)

Source baseline: `quorivio-0.1.0-dev-accessibility-integration-cumulative.zip`.

## Verified in this local cycle
- PPTX media content-type/signature consistency and importer/report parity.
- `python -m unittest discover -s tools/tests -q`: 218 tests passed.
- `npm run test -w @quorivio/api`: 116 tests passed.

## Do not mark complete without implementation and evidence
- PPTX grouped elements, charts, tables, SmartArt, complex theme preservation, unsupported OOXML round-trip.
- Browser-based mobile editor interactions and adapted audience widgets; full visual accessibility acceptance.
- MFA independent method enrollment and top-level enable/disable semantics.
- Live widget publish/answer/result end-to-end and multi-pod synchronization and 500 users.
- Portable bundle cross-instance import with real PostgreSQL and private asset storage.
- Reproducible clean frontend/backend build and the security/license/GDPR gate review on this revision.
- Full documentation/manual reconciliation and user's Kubernetes acceptance.

The last RC matrix remains 37.5% pending verified gate closure. `0.1.0-dev` is unchanged. No GitHub or Kubernetes operations were performed.


## RC89 handoff — editor feedback, verified base 2026-10-31

Repository `desalvo/quorivio`, branch default; `0.1.0-dev`. Maintainer-confirmed green standard/extended workflows 41243609282 / 41244919887, commit `4d0901d8805f99f696e85414038ff543d694272a`. RC89 cumulative archive should overlay this commit, not make a second commit automatically. Changes: front-end editor palette/answer fields/context and schema controls, backend strict `answerFillColor` validator, CI regression tests/inventory. Real browser acceptance after RC89 is not yet proved. RC score remains 84.75%; not an approved production publication. Full inventory available `docs/validation/RC_CYCLE89_PACKAGE_INVENTORY_20261031.json`; verify with `python tools/verify_rc_cycle89_inventory.py` before git commit, then standard and extended GitHub Actions.

## 2026-10-31 — RC90 session sidebar, global slide schemes and editor cleanup (uncommitted)

**Upstream:** maintainer-confirmed standard and extended CI green on `4d0901d8805f99f696e85414038ff543d694272a`. RC89 is not yet committed; RC90 is cumulative from RC89. Version `0.1.0-dev`, EUPL-1.2 unchanged.

**Session sidebar:** in an open session, a dedicated action panel offers leave view (without ending the live session), terminate session (confirmation), duplicate as a clean draft (existing guarded endpoint), rename (inline form, authorized metadata PATCH, 1–160 chars), delete (owner-only, confirmation), and open the dedicated master editor. Permission is taken from authenticated `GET /sessions/:id`, not the live/public snapshot. The dashboard section previously named “Anteprima presentatore” is now “Schermo presentatore”.

**Presentation master:** session-level Title/Footer templates use the same interactive `WidgetCanvas` drag/resize/rotate UI and are saved through the validated session theme. Presenter screen, participant screen, rehearsal and PowerPoint export inherit missing Title/Footer widgets automatically; local page widgets override the corresponding master kind. Explicit “Applica schema…” adopts the template on a page while preserving unrelated widgets. Dynamic page number is 10 CSS px from the canvas bottom/right; default footer moved inside the canvas to avoid clipping. The export worker uses the same 10 px-equivalent inset.

**Legacy cleanup:** removed the duplicated dashboard page/quiz/poll management and historic activity edit forms, leaving live rating/reaction reporting; the editor remains the supported widget-first authoring route. Removed exposed legacy JSON import/export buttons, retaining reading/migration capability and server data paths to avoid destructive changes. **Pending:** database migration audit before removing any persisted legacy columns or historical import compatibility; full browser/PowerPoint/Kubernetes CI after commit; explicit manual validation of canvas manipulation and schema inheritance.

**Readiness:** keep the externally certified score at **84.75%** (42 accepted and 17 partial gates). The new functionality is awaiting a fresh standard/extended GitHub acceptance run; do not claim it has passed on RC90.

**Final local regression evidence:** Node API 565/565, Node frontend 134/134; 15 focused Python contract/PPTX tests passed. Full Python and complete conversion/infrastructure runs not certified locally due to execution timeout. Browser semantics and visual slide-master UX must be accepted in maintainer-triggered GitHub CI after the next commit.


## 2026-11-01 — RC99: full-Python CI compatibility and native PowerPoint outline round-trip

**Upstream confirmed by maintainer:** RC95 was committed. RC96–RC99 form a cumulative uncommitted set after that commit; do not push, tag, release, or commit automatically. Version `0.1.0-dev` and EUPL-1.2 are unchanged.

**Diagnosis:** GitHub standard run supplied as `logs_111821227952.zip` passes RC98 TypeScript compilation, Node units, PostgreSQL integration, and reaches the final `Kubernetes wizard and worker integration tests` phase. Its 1,527 Python tests return 7 contract failures and 1 native PowerPoint error. The historic source tests asserted literal JSX snippets removed by later valid features (e.g. joinCode inserted among WidgetCanvas props, guarded sidebar navigation, dedicated PresenterLiveScreen useLive, enabling footer rich-text editing, selected text style helper). Every one was updated to test the current semantic contract, without skipping tests or reverting new functionality. Full JSON/media callbacks, live subscriptions, dirty-schema confirmation and selected-text behavior remain asserted.

**Actual export defect:** a PPTX shape can encode an explicit RGB stroke without positive line width (theme-inherited width). On import, `strokeColor` was retained but `strokeWidth` was not, so the new borderless-by-default export silently removed the outline. Native PPTX import now promotes the inherited theme stroke to 1 pt, without changing Quorivio's default border 0 or borderless native export. Added explicit visible-outline and borderless-outline round-trip tests.

**Local evidence:** all 55 focused Python tests pass, including eight previously failing CI tests and the new borderless regression. Full local Python suite exceeded execution limit; full npm build could not run reproducibly due to incomplete offline npm dependency tree; both remain unverified on this revision. Build successfully completed in the supplied RC98 GitHub CI logs before failing downstream. Current RC99 requires GitHub standard and extended acceptance. Certified RC score unchanged **84.75% (42 accepted, 17 partial)**.
