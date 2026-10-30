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
