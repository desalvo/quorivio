## K8s wizard credentials — 2026-10-23
2026-10-23: il wizard Kubernetes genera credenziali PostgreSQL interne, admin e AUTH_SECRET riutilizzabili, salva override/Secret con permessi 0600 e richiede una password nota per DB esterno. Vedi K8S_SECRETS.it.md. Collaudo reale ancora aperto.

## 2026-10-23 — Kubernetes test deployment and image correction (uncommitted after latest confirmed green CI)
- Default application image corrected to `desalvo/quorivio:latest` in Compose/Kustomize/Helm/CI; Helm converter image reference renamed to `desalvo/quorivio-converter:0.1.0-dev` (registry availability not confirmed).
- Wizard supports TLS termination without a named ingress TLS secret (controller default certificate required), explicit TLS disable, and independent app/PostgreSQL pod node selectors. Helm supports optional TLS secret and shared pod nodeSelector.
- Verifiche: 111/111 Python, 107/107 Node.js, build di produzione backend/frontend PASS e parsing YAML Kustomize. Helm non disponibile; cluster Kubernetes reale e pubblicazione registry non verificati. See `K8S_TEST_DEPLOYMENT.en.md` / `.it.md`. GitHub not changed; new maintainer commit and CI required before deploying. Version unchanged 0.1.0-dev.


## 2026-10-23 — Verifica editor con Chromium: blocco di accesso al server locale
- Chromium 144 e Python Playwright disponibili e avviabili; il browser gestito dall'ambiente blocca le navigazioni verso il server Vite su 127.0.0.1 (`ERR_BLOCKED_BY_ADMINISTRATOR`). Non è stato eseguito alcun E2E browser né PostgreSQL (server non disponibile).
- Correzione: i campi input dentro i widget non avviano più trascinamenti accidentali; la perdita della cattura del puntatore annulla il gesto e ripristina la geometria precedente. Aggiornati i test di regressione.
- Build backend/frontend superate; Node 107/107, Python 104/104. I gate RC rimangono al 37,5% secondo matrice, senza promuovere test sorgente ad accettazione browser.

## 2026-10-23 — Stabilizzazione gesti editor (ciclo 3, parziale)
Rotazione incrementale con orientamento preservato, rollback della geometria su pointercancel, cleanup su perdita pointer capture, touch-action dei widget. Build backend/frontend superate; Node suite e 102 test Python superati. Collaudi browser, touch, PostgreSQL e accessibilità assistiva non eseguiti. RC 37,5% invariato secondo matrice; editor non ancora validato E2E. Vedi EDITOR_STABILIZATION.it.md.


## 2026-10-23 — Editor responsive e controlli accessibili (ciclo 2)
- Aggiunto pannello alternativo ai gesti del canvas per ogni widget: spostamento del 5% sui due assi, duplicazione e gestione dei livelli con controlli touch da almeno 44px e nomi accessibili.
- Layout adattivo e focus visibile. Persistenza tramite i metodi widget già esistenti, senza modifiche al database.
- Build backend e frontend superate, 107 test Node e 99 Python superati. Non verificati: dispositivi fisici, screen reader, PostgreSQL E2E. Il gate RC resta 37,5% e l'editor non è ancora accettato end-to-end.

## 23/10/2026 — Ciclo accorpato composizione editor (non committato)
- Aggiunti griglia opzionale 5%, duplicazione widget con nuovo ID e gestione livelli avanti/dietro nel canvas 16:9; salvataggio e tastiera esistenti preservati.
- Node 107/107, Python 99/99 con tre test statici, build TypeScript/Vite PASS; browser/DB E2E non eseguiti. Nessun gate RC chiuso: matrice ponderata **37,5%** invariata. Vedere `EDITOR_COMPOSITION.it.md`.
- Ultimo commit confermato: baseline CI verde prima dei risultati configurabili. Nessuna operazione git.

## 2026-10-23 — Correzione sincronizzazione slide partecipanti (parziale)
La pagina attiva ricevuta via WebSocket viene scelta usando `current_activity_id` dal server e lo stato open, non più la prima attività. Build di produzione PASS, Node 107/107 e Python 96/96. E2E browser/PostgreSQL ancora aperti; RC invariata al 37,5%. Vedere `AUDIENCE_PAGE_SYNC.it.md`.

## 2026-10-23 — Nuvola dei risultati per widget (parziale)

Aggiunta vista Nuvola per le frequenze delle opzioni di ogni widget domanda, con conteggi espliciti e revisioni distinte. Non è una nuvola delle parole delle risposte libere. Build backend/frontend e test Node PASS. Collaudi browser/PostgreSQL non eseguiti. Gate RC **37,5%** invariati; vedere `RESULT_WORD_CLOUD.it.md`.

## 2026-10-23 — Fondamenta per MFA email (NON ATTIVA)

Codici casuali a sei cifre, digest HMAC separati per utente/sfida, controllo a tempo costante, helper invio SMTP TLS e tre test. Il login non cambia: restano necessari challenge PostgreSQL monouso, scadenza, limitazione tentativi e interfaccia. **MFA email ancora APERTA**, punteggio RC invariato. Vedere `EMAIL_MFA_FOUNDATION.it.md`.

## 2026-10-23 — Verifica rigorosa Origin in scrittura

Confronto completo schema/host/porta per le API che modificano dati; compatibilità con i client senza Origin invariata. 97/97 test Node e 95/95 Python PASS; build backend TypeScript e frontend Vite PASS. E2E con browser/reverse proxy non eseguito. Vedere `docs/ORIGIN_POLICY_HARDENING.it.md`. Punteggio ponderato di accettazione RC **37,5%**, vedere `docs/RC_GATE_MATRIX.json`.

## 2026-10-23 — Ricalcolo dei gate RC (autorevole)

**RC 37,5% su evidenze ponderate, non 67%.** Vedere `docs/RC_GATE_AUDIT.it.md` e `docs/RC_GATE_MATRIX.json`. I valori precedenti del 67% sotto sono soltanto cronologia, superati da questo ricalcolo. Nessuna nuova validazione end-to-end dichiarata.

## 2026-10-23 — Verifica revoche WebSocket dei presentatori già connessi

Implementata verifica PostgreSQL ogni dieci secondi per i WebSocket già aperti dei presentatori, con chiusura per revoca, account non approvato e indisponibilità del database (fail-closed). Build API + Vite PASS, test Node 95/95, Python 93/93. E2E PostgreSQL/multi-replica NON eseguiti; MFA email e restanti gate RC aperti. Baseline gate RC invariata al 67%. Vedere `docs/LIVE_WEBSOCKET_REVOCATION.it.md`.

## 23 ottobre 2026 — Protezione quiz a tempo attivi (parziale)
- Bloccate con HTTP 409 le modifiche a risposte, durata e rimozione mentre la pagina è aperta; la geometria resta modificabile. Le modifiche successive creano una revisione. 91/91 test Node superati. Build Vite avviata ma non confermata (timeout ambiente). PostgreSQL/browser E2E da verificare. RC invariata 67%. Vedi `TIMED_WIDGET_LIVE_LOCK.it.md`.

## 23 ottobre 2026 — Quiz a tempo indipendenti per widget (parziale)
- Risposte e classifiche separate per widget, configurazione e paginazione presentatore. Build locali superate; test PostgreSQL/browser E2E mancanti. RC **67%** invariato. Vedi `TIMED_WIDGET_INDEPENDENCE.it.md`.

## 23/10/2026 — Risultati per widget domanda (parziale)
- Pannello Risultati del presentatore: aggregazioni autonome per ogni widget domanda, separate per revisione e visualizzazione scelta nell’editor (barre, torta, tabella). Build TypeScript/Vite e 90 test Node superati. Quiz a tempo multipli indipendenti ancora mancanti. Gate RC **67% invariati**. Vedere `WIDGET_RESULTS_PER_WIDGET.it.md`.

## 23/10/2026 — Quiz a tempo e Risultati per il presentatore (parziale)
- Vedi `TIMED_QUIZ_RESULTS.it.md`: attività separata e cronometro dal server, classifica protetta, nuovi widget palette e pulsante Risultati del presentatore, build frontend/backend e 90 test Node superati. **Macroarea non conclusa.** 67% invariato. Le funzioni precedenti non committate rimangono incluse nel cumulativo.

## 2026-10-23 — Recupero MFA amministrativo per utente
- Introdotto reset MFA TOTP per utente con verifica password/TOTP amministratore, protezione account principale e reset proprio, cancellazione transazionale dei segreti/codici, chiusura WebSocket, indicatore MFA e controllo UI. Il cookie di login preesistente **non è revocato**: gate sicurezza produzione aperto.
- Build sorgenti, TypeScript e Vite eseguite; 87 verifiche Node e 91 Python. Nessun test E2E PostgreSQL/browser. Vedere `ADMIN_MFA_RESET.it.md`. Gate RC ancora al **67%**.

## Stato dei gate aggiornato — 23 ottobre 2026 (ultimo cumulativo)
- **Gate RC chiusi: 67% (invariato).** La nuova anteprima geometrica e il riordino via tastiera non hanno ancora superato build/collaudo browser; la stima non è percentuale di test né idoneità alla produzione.
- Implementate miniature con fino a 24 widget, posizioni e rotazioni salvate, sfondo facoltativo; riordino Alt+frecce tramite API transazionale già esistente. Media rappresentati con simboli e non con veri fotogrammi.
- Verifiche locali: 85/85 test Node.js e 88/88 Python, inclusi 2 nuovi test statici. `npm install --offline` non riesce per assenza di `@types/bcryptjs` nella cache: build TypeScript/Vite **non eseguita** e CI recente non confermata.
- Restano aperti i gate PostgreSQL/browser/container/Kubernetes/SSO/MFA via email e amministrativa/accessibilità/sicurezza/HA. I manuali PDF sono edizioni precedenti e **non** descrivono integralmente l'interfaccia attuale. Dettagli in `SLIDE_THUMBNAILS_KEYBOARD.it.md`.
- Nessuna modifica del repository remoto; gli sviluppi successivi all'ultima CI confermata sono cumulativamente non committati.


## RC editor grouped cycle 2026-10-23 — see docs/RC_EDITOR_BATCH.en.md and .it.md
## 2026-10-23 — Phase 2 field-validation follow-up

See `docs/VALIDATION_PHASE2_ISSUES.it.md` / `.en.md` for completed work, unverified UI, and pending calendar/editor work.

# Stato sviluppo (IT) — 2026-10-22
Versione `0.1.0-dev`. Realizzati nei sorgenti: backend/frontend, sessioni, sondaggi/quiz iniziali, QR code, risultati WebSocket, CSV, documentazione bilingue, wizard Kubernetes con output Kustomize, workflow GitHub CI/Docker Hub. I PDF e gli asset grafici sono inclusi e consultabili nell'interfaccia. Non sono ancora verificate build npm, runtime Docker/Podman/Kubernetes, provider social/generic OIDC, cluster reali e test end-to-end. I gate di produzione sono **configurati**, non ancora eseguiti con successo sulla CI reale. Evitare di dichiarare il prodotto pronto per il traffico pubblico prima di risolvere i blocchi e verificare sicurezza, disaster recovery e carico. Si veda il file `DEVELOPMENT_STATUS.md` per il dettaglio tecnico.

**Aggiornamento:** quattro test wizard superati; generati i quattro PDF, logo, grafica copertina e relativi link applicativi. Bloccata la generazione lockfile npm nell'ambiente offline. CI di produzione configurata ma non eseguita. Testo integrale ufficiale EUPL-1.2 da incorporare prima del rilascio pubblico.

## Terzo ciclo — PostgreSQL, Ingress e GDPR (22/10/2026)

- Compose aggiornato a PostgreSQL 18.6 con percorso dati `/var/lib/postgresql`; gli upgrade major richiedono migrazione reale.
- Wizard: database interno StatefulSet/PVC o esterno senza risorse DB; cambio modalità idempotente, annotazioni ingress NGINX/HAProxy per varianti community/haproxytech.
- Deployment con Secret DATABASE_URL; credenziali e certificati devono essere forniti dall'amministratore.
- Creati registri tecnici GDPR IT/EN con lacune aperte; nessuna dichiarazione di conformità.
- Test Python wizard ampliati; build npm, test reali PostgreSQL/Kubernetes e deployment non verificati. PDF precedenti non rigenerati in questo ciclo.

## Ciclo gestione dati e partecipanti (22 ottobre 2026)

- L'utente conferma CI precedente completamente verde e commit del cumulativo precedente; queste modifiche **non sono state committate**.
- Implementati cancellazione della sessione autorizzata al proprietario, revoca con rotazione dei link e chiusura WebSocket, retention configurabile (1–3650 giorni, predefinita a 90).
- Aggiunto cleanup orario delle sessioni chiuse/scadute oltre la retention, con cancellazione PostgreSQL a cascata; riconnessione del partecipante con cookie valido senza crearne uno nuovo.
- Esportazione CSV protetta contro formula injection e nuovi test dedicati.
- Verifiche: **6/6 test Node superati**, **11/11 test wizard Kubernetes superati**. API/database reali, migrazioni, CI, Docker e conformità GDPR ancora **non verificati** in questo ciclo.
- Prossimi passi: test API PostgreSQL, sicurezza sessioni/CSRF/TLS, policy backup, eventi multi-replica, SSO e nuove attività.
- Verifica libreria: presenti 6 ZIP Quorivio, inferiori al limite di 10; nessun archivio da eliminare.

## Avanzamento — stime basate sulle evidenze (2026-10-22)

These are **engineering estimates**, NOT CI pass percentages or certifications. Each category counts toward a fixed equal-weight functional rubric (10 items) or operational-readiness rubric (10 items). Recalculate every cycle from verified functionality; do not silently promote source implementation to tested release capability.

**Completamento funzionale: 34%** (scores / 10). Rubric: core architecture 80, session lifecycle 65, participant UX 40, polls/quizzes 30, results and exports 25, advanced activity types 0, integrated presentations 0, IAM/SSO/tenancy 45, documentation 35, operations tooling 20 = 340 / 10. Documentation 35 refers to completeness across all required deliverables, not quality of the new manuals alone.

**Prontezza alla produzione: 36%** (355 / 10, rounded). Rubric: baseline CI 80, basic Docker runtime 70, database integration 30, Kubernetes deployment 40, auth hardening 30, GDPR controls 20, multi-replica 0, operational docs 55, disaster-recovery verification 10, production E2E/load/security verification 20. CI success was reported by the user for the **previous** cumulative archive; this new artifact has not run in GitHub Actions.

Progress bars (10 blocks):

- Features: **34%** `███░░░░░░░`
- Prontezza alla produzione: **36%** `████░░░░░░`

## Consegna corrente — UI GDPR e manuali illustrati

- Added presenter UI for editing session retention (on blur), revoking access and deleting a session with confirmation. The backend handlers already existed. UI/browser integration **not tested**.
- Added third documentation navigation link for the dedicated presenter manual (IT/EN).
- Added reproducible `tools/generate_manuals.py` PDF generator: six role-specific PDF manuals (participant, presenter, administrator × IT/EN), cover imagery, navigable table of contents, total page numbering, illustrated UI/workflow diagrams, results chart, procedures, troubleshooting, and appendices. Contents distinguish implemented vs planned features.
- Copied manuals to `apps/web/public/docs/manuals/` for delivery by web UI; frontend build not run locally (npm packages unavailable).
- Local automated regressions: 6/6 Node domain tests and 11/11 Kubernetes wizard tests passed. PDF generation and PDF page geometry inspected. User-reported previous CI green remains separate.
- Next priorities: executable CI for current package, PostgreSQL integration and frontend E2E, GDPR audit/rights workflows, SSO, activity breadth, load and Kubernetes cluster verification.


## Ciclo identità, contenuti e governance (22 ottobre 2026)

Aggiunte migrazioni additive per approvazioni, cambio password obbligatorio, pseudonimi, accesso anonimo per sessione, temi pagine, impostazioni amministrative e retention predefinita di 60 giorni dalla chiusura. Realizzati API e controlli UI preliminari per approvazione utenti, impostazioni admin e risorse media HTTPS. Ingresso autenticato, MFA, SMTP, SSO, upload asset, editor visivo e risultati personalizzati restano aperti. Credenziali admin demo 000000 solo con opt-in in sviluppo e cambio obbligatorio; non consentite in produzione. Test locali: 8/8 dominio, 11/11 wizard. Build integrale/CI/PostgreSQL reale non verificati. **Funzionalità 39%, readiness 34%** (stime; CI verde solo per commit precedente).

Ulteriori sviluppi: registrazione web, creazione/eliminazione utenti da UI admin, verifica ruolo owner WebSocket, pubblicazione opzionale dei risultati aggregati e sfondi/loghi delle sessioni. Servono test reali PostgreSQL/API/browser.

## 2026-10-22 — Collaboration, portable sessions and ingress sizes
Implementazione parziale API: collaboratori, import/export delle sole definizioni JSON, duplicazione in bozza, invalidazione con audit, modifica live e limiti ingress. 8/8 test Node, 14/14 test wizard. Backup completo DB, upload e UI ancora pendenti. CI non verificata. Stima funzionalità 43%; readiness 33%.

## 2026-10-22 — Backup offline e storage Kubernetes

- Introdotto `tools/instance_backup.py`: dump PostgreSQL + file, manifest con SHA-256, verifica e ripristino su destinazioni vuote con conferma esplicita.
- Guide operative bilingui `INSTANCE_BACKUP.it.md` e `.en.md`.
- Wizard Kubernetes: PVC asset, montaggio `/app/assets`, dimensione/access mode/StorageClass configurabili.
- Test locali: 11/11 Node, 19/19 Python. **Non eseguiti**: backup/ripristino PostgreSQL reale, build CI, browser e cluster Kubernetes.
- **Aperti**: backup da interfaccia admin, pianificazione e cifratura integrata, test disaster recovery reale, storage condiviso e validazioni di produzione.
- Le precedenti percentuali 53% e 33% restano stime storiche. Questo ciclo non dimostra un aumento verificato di almeno 10 punti percentuali.

## 22 ottobre 2026 — Immagini, layout e risposte invalidate
- Default Compose/Podman/Kubernetes: `desalvo/quorivio:latest`; pubblicazione Docker Hub aggiornata, mantenendo GitHub `desalvo/quorivio`.
- Data di riferimento persistita e modifica dei metadati durante la sessione.
- Editor dei layout specifici domanda e risultati; ancora da verificare il rendering completo in browser.
- Risposte invalidate mantenute per audit; indice univoco parziale sulle sole risposte attive per consentire un nuovo voto. Applicare prima la migrazione.
- Manuali PDF rigenerati. Test locali: 11 Node, 23 Python; verifiche PostgreSQL reali/CI/browser ancora aperte.
- Copertura funzionale precedente 55%, readiness 35%; incremento di 10 punti non verificato.


## Quiz e reazioni (22 ottobre 2026)
Modalità risposte e obbligatorietà, reazioni uniche e statistiche, controlli web iniziali. Test locali: 17 Node, 23 Python superati. PostgreSQL e browser E2E non verificati. Funzionalità 63%, readiness 35%.

2026-10-22: widget composer question-page ordering, rating 0–10 endpoints, PostgreSQL uniqueness and aggregate stats; no full browser/DB CI yet. Timer/QR placeholders. Docs build dev-20261022.

## Widget runtime e portabilità quiz — 22 ottobre 2026
- Definizioni sessione: modalità, obbligatorietà e risposte corrette multiple conservate in export/import/duplicazione.
- Widget timer con countdown e QR SVG pubblico senza privilegi.
- Test locali: 20/20 Node e 23/23 Python. Build browser e PostgreSQL reali non verificati. L'incremento richiesto del 10% non è attestabile.

### 2026-10-22 — Widget domanda indipendenti
Aggiunti endpoint di risposta per widget, tabella `widget_answers`, statistiche aggregate per il presentatore e UI partecipante con risposte singole/multiple/testo/allegato. Mancano test integrati PostgreSQL/browser, caricamento file anonimo e versionamento delle domande modificate. Funzionalità stimate 83% (da 80%); readiness invariata 35%.

## 22 ottobre 2026 — Preparazione importazione presentazioni offline
- Aggiunto `tools/import_presentation.py`: conversione PDF/PPTX in PNG con limiti e manifest SHA-256.
- Corretto un errore di quoting TypeScript nella query per l'elenco delle sessioni.
- Verifiche: 46 test Node e 27 test Python superati. Build completa e conversione PPTX reale non verificate.
- Aperti: importazione via browser, associazione alle sessioni, worker isolato, migrazioni, collaudi end-to-end.
- Copertura funzionale stimata: 89% (+1 punto); readiness produzione: 35%.


## Ciclo pagine slide — 2026-10-22

Pagine slide integrate: aggiunta di singole immagini o più PNG/JPEG/WebP dalla UI come pagine della sessione; accesso pubblico limitato alla slide corrente. Conversione PDF/PPTX ancora offline, worker isolato da realizzare. Collaudi PostgreSQL/browser pendenti. Stima funzionalità 90% (prima 89%); readiness 35%.

## 22 ottobre 2026 — Base per MFA TOTP e SMTPS
- Implementati: attivazione e conferma MFA con autenticatore, verifica al login, disattivazione con due fattori, cifratura AES-256-GCM dei segreti e interfaccia web.
- Implementati: validazione SMTP su variabili d'ambiente, controllo configurazione senza password ed email di prova su TLS con verifica del certificato.
- Test locali aggiunti su TOTP RFC 6238, finestre temporali, cifratura e configurazione email. Build npm completa, server SMTP reale, PostgreSQL e browser da verificare.
- Aperti: SSO social/generic OIDC, codici di recupero MFA, protezione contro replay e tentativi di accesso distribuiti, integrazioni produttive.

## 22/10/2026 — Recupero password
Implementati token monouso con hash SHA-256 e scadenza 20 minuti, risposta generica anti-enumerazione, invio SMTPS, limitazione richieste per IP/account, UI di recupero e revoca dei cookie preesistenti nel middleware API. TOTP rimane obbligatorio. Test superati: 57/57 Node e 27/27 Python. Mancano prove con SMTP/PostgreSQL/browser reali e sistemi multinodo. SSO ancora aperto.

## Codici di recupero MFA — 2026-10-22
Implementati dieci codici monouso con hash HMAC, consumo atomico al login, rigenerazione protetta, interfaccia web e revoca in caso di disattivazione MFA. Test locali: 60/60 Node, 27/27 Python. Da verificare: migrazione PostgreSQL, browser, SSO e sicurezza in produzione.

## 2026-10-22 — Prima integrazione SSO OpenID Connect
- Implementati OIDC configurabile Google/generic OIDC/custom, Authorization Code con PKCE, state/nonce, JWKS RS256, associazione esplicita all'account e nuovi controlli UI.
- Non si associano utenti per semplice coincidenza dell'email; l'MFA TOTP locale non viene aggirato da OIDC.
- Verifica: 64/64 test Node e 27/27 test Python. Non verificati login con provider reali, migrazioni PostgreSQL e browser.
- Aperti: GitHub e Facebook OAuth, broker OIDC/SAML, stato distribuito e step-up MFA per OIDC. Non abilitare per produzione senza collaudi.
- Stima completamento funzionale 96% (+1); production readiness 35% invariata.

## 2026-10-22 — GitHub/Facebook OAuth2
**Implementato:** avvio/callback OAuth2, cookie di stato, recupero ID immutabile, collegamento esplicito, prevenzione bypass TOTP, link UI e cinque test. **Verificato:** 69 test Node, 27 Python. **Aperto:** provider reali, stato multi-replica, PostgreSQL, build frontend e test end-to-end.

## 2026-10-22 — Riordino grafico delle pagine
- Introdotto drag-and-drop HTML5 delle pagine con API transazionale esistente; gli ID e le risposte storiche restano invariati, e rimangono i pulsanti Su/Giù da tastiera.
- Quattro nuovi test automatici sul riordino, guide `PAGE_STORYBOARD.it.md` e `.en.md` e manuali bilingui aggiornati.
- Corretto il testo obsoleto sull'importazione PDF/PPTX diretta, sperimentale e subordinata alla configurazione.
- Da collaudare: build npm, browser, PostgreSQL, concorrenza, provider OAuth reali e worker di conversione isolato.
- Stima di copertura funzionale 98% (prima 97%), readiness 35%; non equivalgono a certificazione.


## 2026-10-22 — Canvas libero dei widget (sperimentale)
- Realizzato il posizionamento percentuale, trascinamento, editing del titolo nel blocco, larghezza modificabile e rimozione individuale, con salvataggio nel layout.
- Validazione server delle coordinate e due nuovi test; regressione 71/71 Node e 27/27 Python. Parsing TS/TSX senza errori.
- Non verificati build completa, browser e PostgreSQL; assenti rilevazione collisioni, storage distribuito e worker isolato.
- Stima copertura funzionale 98% invariata, readiness 35% invariata; non dichiarare completamento totale.

## Scansione antivirus — 22 ottobre 2026
Nuovo client ClamAV INSTREAM con esito fail-closed configurabile per upload e importazioni. Test locali: 75/75 Node e 27/27 Python; scanner reale non ancora installato né collaudato. Copertura funzionale stimata 98%, prontezza produzione 35%, invariate. Per l’attivazione è necessario predisporre ClamAV e impostare QUORIVIO_AV_REQUIRED=true, CLAMAV_HOST; vedere docs/ANTIVIRUS_UPLOADS.it.md. Restano worker conversione isolato, coordinamento multi-replica, storage condiviso e collaudi integrati.

## Configurazione OIDC generica (2026-10-22)
Rimossi il precedente preset istituzionale e ogni riferimento al suo nome. Nuovi provider OIDC configurabili tramite OIDC_PROVIDERS_JSON, fino a 32, con controlli stretti e due test dedicati. Nessun provider esterno collaudato. Restano aperti worker documentale isolato, WebSocket/stato autenticazione distribuiti, storage condiviso e collaudi end-to-end. Non dichiarare completo il prodotto o pronto per la produzione.


## Managed antivirus and SSO defaults (2026-10-22)

Docker/Podman Compose now bundles a private ClamAV service and persists its signatures. Helm includes a ClamAV sidecar with fail-closed scanning. Public provider endpoints are documented for Google, GitHub and Facebook; client registrations and secrets remain operator tasks. Offline source-level tests do not constitute deployment validation. Multi-replica synchronization and isolated document conversion are still outstanding.

## 2026-10-22 — Sincronizzazione WebSocket multi-replica e persistenza asset Helm

**Implementato:** PostgreSQL LISTEN/NOTIFY per distribuire gli aggiornamenti delle sessioni, listener con riconnessione, payload UUID, PVC Helm persistente con opzione di claim esterno e wizard Kustomize con 2–20 repliche solo in presenza di storage RWX. Guide `MULTI_REPLICA_SYNC.it.md` ed `.en.md`.

**Verificato localmente:** 79 test Node, 33 test Python e controlli statici Helm. **Non verificato:** PostgreSQL reale, cluster Kubernetes, browser, build frontend completa e accesso concorrente ai media. Lo stato OAuth/OIDC e il rate limiting sono ancora locali al processo, quindi l'autenticazione multi-replica non è pronta per la produzione. Completamento funzionale stimato **98%**, readiness **35%** invariati in mancanza di prove integrate.

**Ancora da sviluppare autonomamente:** worker isolato PDF/PPTX, stato OAuth condiviso, limitazione distribuita, test E2E e rifiniture canvas. **Richiede ambiente/credenziali dell'operatore:** SSO reali, consegna SMTP e prove Docker/Kubernetes.

## 22 ottobre 2026 — Autenticazione federata e limitazione richieste distribuite

**Implementato:** gli stati temporanei SSO OIDC/GitHub/Facebook sono ora conservati in PostgreSQL e consumati atomicamente con `DELETE ... RETURNING`; callback protetti da cookie, provider e scadenza. Il rate limiting API utilizza contatori a finestra temporale condivisi in PostgreSQL (UPSERT atomico), con errore 503 se il database non è disponibile. Pulizia periodica inclusa.

**Test:** 82/82 Node e 33/33 Python superati. **Non ancora verificati:** build npm completa, migrazioni PostgreSQL reali, login con provider esterni, cluster multi-replica e conversione isolata di presentazioni.

**Restano da sviluppare:** worker isolato delle conversioni, test end-to-end e rifiniture del canvas e della gestione degli upload. Per i test finali sarà necessario predisporre servizi e credenziali nell'ambiente dell'utente. Nessuna certificazione di production readiness.

## 2026-10-22 — Worker isolato per la conversione
- Introdotto servizio container dedicato non privilegiato, dispatch interno autenticato, volume temporaneo privato, stack Compose e sidecar Helm. L’API non esegue più direttamente il convertitore.
- Test: 82 Node, 37 Python. Da collaudare container reali, PostgreSQL, browser, build completa e sicurezza; altre attività software ancora aperte.

## 22 ottobre 2026 — Verifica CI su PostgreSQL e build convertitore
- Limite recupero password migrato da mappa in memoria a contatore PostgreSQL atomico, condiviso fra repliche.
- CI: servizio temporaneo PostgreSQL 18, avvio API compilata, verifica health e pagina web, account iniziale e tabelle, rifiuto dell'accesso non autenticato.
- Aggiunta build dell'immagine convertitore in CI; scansione Trivy bloccante presente sull'immagine principale, scansione dedicata del convertitore ancora da includere.
- Nuovi test di contratto e guide `CI_INTEGRATION.it.md` e `.en.md`.
- Mancano nell'ambiente corrente le dipendenze npm e Docker: compilazione completa, test Postgres reale e pipeline remota **non sono verificati**. Il proprietario può eseguire la CI e fornire il primo log di errore. Non dichiarare il 100% né la readiness per produzione.
- Stime invariate: **98% funzionale**, **35% readiness**.


## CI 107927415489: correzione dipendenza vulnerabile (22/10/2026)
- PASS confermati: test unitari (82), compilazione frontend/backend, avvio su PostgreSQL 18, endpoint di salute, bootstrap e autorizzazioni di base.
- FAIL confermato: `npm audit` sulle dipendenze di produzione; Nodemailer 6 vulnerabile HIGH.
- Modifica: `nodemailer: ^10.2.1` e rimozione di `@types/nodemailer`, non più necessario.
- PENDENTE: nuova installazione npm, compilazione/audit in GitHub Actions e build container. **Non dichiarare la CI verde prima della riesecuzione.**
- Baseline commit: l'utente ha confermato il commit precedente; il prossimo messaggio di commit riguarda solo questa correzione e documentazione.

## Segnalazione GitGuardian sul test TOTP (22/10/2026)
- Eliminata la stringa Base32 letterale del vettore pubblico RFC 6238 dal test; vettore ricostruito a runtime e altri segreti di test generati casualmente.
- Test locali superati: 82/82 Node, 40/40 Python.
- Altri errori CI non ancora analizzati in assenza dei relativi log.
- Nessun commit o push effettuato.


## Pulizia cache Python (2026-10-22)
- Aggiunte le regole .gitignore per __pycache__/, *.py[cod], .pytest_cache/, .mypy_cache/, .ruff_cache/.
- Escluse cache e bytecode Python dal pacchetto cumulativo, mantenendo sorgenti e test.
- Le cache già tracciate da Git richiedono la rimozione dall'indice da parte del manutentore (`git rm --cached`); non serve riscrivere la cronologia.
- Ultimo commit confermato: hotfix di sicurezza Nodemailer. Modifiche successive: fixture TOTP e pulizia cache Python. Nessun commit eseguito.
- Stime invariati: 98% funzionale e 35% readiness; CI reale ancora da verificare.

## Baseline CI verde e sicurezza delle conversioni (2026-10-22)
- L'utente ha confermato commit della pulizia delle cache Python e CI verde: questa è la nuova baseline dei futuri messaggi di commit; sostituisce gli esiti CI storici riportati sopra.
- Worker isolato: rifiuto di output preesistenti e symlink, protezione da conversioni simultanee dello stesso job nella singola istanza, rilascio della prenotazione anche in caso di errore; HTTP 413 per richieste eccessive.
- CI: aggiunta scansione Trivy HIGH/CRITICAL anche per l'immagine `quorivio-converter:gate`, senza indebolire gli altri controlli.
- 3 nuovi test di regressione. Verifiche locali: 82/82 Node, 43/43 Python, eseguiti senza scrittura bytecode Python.
- Ancora da verificare nella CI reale il nuovo gate Trivy; non eseguiti collaudi browser/conversione reale/multi-pod. Il blocco anti-duplicazione è locale al worker, non un lock distribuito.
- Nessun commit, push, tag o release eseguito.

## 2026-10-22 — Prenotazione delle conversioni fra processi (non committata)
- Aggiunta prenotazione atomica `.conversion-lock` per ogni lavoro sul volume temporaneo condiviso. Impedisce doppie conversioni simultanee anche su processi/worker differenti che usano lo stesso filesystem.
- In caso di arresto improvviso il blocco rimane: verificare il job prima della rimozione manuale, evitando recuperi automatici rischiosi.
- Test di regressione su prenotazione già presente, ciclo di vita e pulizia su errore. Esito locale: 82/82 Node e 46/46 Python.
- Baseline ultimo commit confermato con CI verde (pulizia cache Python); nel package rimangono cumulativamente hardening worker e scansione Trivy. Non effettuati commit o push.
- Da verificare: nuova CI, test multi-worker su volume reale e collaudi end-to-end/deployment.

## Recupero amministrativo delle conversioni interrotte (2026-10-22, non committato)

- Aggiunto `tools/recover_conversion_lock.py`: ispezione non distruttiva predefinita e recupero esplicito solo con `--recover --workers-stopped`, dopo l'arresto di tutti i worker che montano lo stesso volume.
- Rifiuta identificativi non validi, percorsi o blocchi simbolici, prenotazioni non vuote, sorgenti ambigue e output già esistenti. Non effettua mai recuperi automatici potenzialmente concorrenti.
- Aggiunte guide operative IT/EN e sette test. Verifiche locali: **82/82 Node** e **53/53 Python**; restano i collaudi end-to-end in container, multi-worker reale, database e browser.
- Versione `0.1.0-dev`, nessun commit. Il prossimo messaggio di commit deve includere tutte le modifiche dall'ultimo commit confermato: hardening converter, Trivy, locking distribuito e recupero manuale.

## 2026-10-22 — Integrità della pubblicazione e sorgenti ambigue (non committato)
- Reject ambiguous PDF/PPTX jobs with two valid sources; require exactly one.
- Generate page manifest in private staging before atomically renaming the completed page directory into place, avoiding partially published output.
- Unit tests: 82/82 Node, 55/55 Python pass. Real image builds, multi-worker NFS/PVC semantics and browser import remain to be confirmed in CI/deployment.
- Last confirmed commit: Python cache cleanup with green CI. All converter/Trivy/recovery changes since then remain uncommitted. Version unchanged: 0.1.0-dev.

## 2026-10-22 — Ciclo integrato per verifiche release candidate (non committato)
- Aggiunti test HTTP reali del worker privato: autenticazione, conversione, rifiuto richieste errate, limite 413, stato 503 e rilascio lock.
- Rafforzato l'import PDF/PPTX: l'API verifica formato/versione manifest, tipo e SHA-256 del sorgente, ordine e posizione delle pagine, firma PNG e checksum prima della registrazione.
- CI: prerequisiti Poppler/ReportLab espliciti, con rendering PDF obbligatorio anziché test opzionalmente saltato.
- Nuove checklist di consegna `docs/RELEASE_CANDIDATE_READINESS.{it,en}.md`.
- Test locali: 82/82 Node, 60/60 Python. Baseline ultimo commit utente: pulizia cache e CI verde. Rimangono cumulativamente non committati: hardening converter, Trivy, lock condivisi, recupero manuale, pubblicazione atomica e questo ciclo.
- **RC BLOCCATA** fino a nuova CI e collaudi reali Docker/Podman/browser/HA. Versione invariata 0.1.0-dev; nessun commit, tag o rilascio effettuato.

## 2026-10-22 — Field validation (phases 1–2) corrections, pending CI (uncommitted)
- ARM64 Compose: managed ClamAV default changed to `clamav/clamav:stable-debian` based on maintainer deployment feedback; image existence/build must still be validated in CI or real deployment.
- Authentication: the mandatory initial password change now signs out client-side and shows the login screen rather than attempting to reuse a revoked cookie. Login accepts either email or the optional globally unique, case-insensitive nickname. Primary administrator has the reserved, immutable nickname `admin` but may change email via a separate audited-by-API administration action. Existing databases migrate primary identity at startup when absent.
- User administration: principal administrator can never be demoted, unapproved or deleted; current-user self-demotion protection remains. User approval toggles immediately and visibly between red and green states. Admin account identity may change its email without changing the stable login identifier.
- Web UI: functional navigation routes to main-area panels for Users, Server Settings, SSO, MFA, Presenter Profile and Workspace. Workspace distinguishes owner/collaborator roles by color. Each session may have zero or several explicit schedule dates via new API and date-selection controls. Session creation still retains legacy reference_date defaults for compatibility.
- Server SMTP/SMTPS settings: admin configuration can now persist with AES-256-GCM encryption under `AUTH_SECRET` and never returns the password. Existing environment configuration remains as fallback. MFA enrollment requires a configured SMTP transport. MFA provides both otpauth URI and authenticated, no-store PNG QR code; actual notification/email fallback behavior is not yet implemented or validated.
- Added additive SQL migrations for primary admin identity, nickname uniqueness, session schedule dates, encrypted SMTP settings. For production, back up the database and test migrations on a clone; avoid changing `AUTH_SECRET` without migrating encrypted settings.
- Validation: Node and Python offline suites, TypeScript/TSX syntax checks; full npm CI, PostgreSQL migration, browser interactions and real SMTPS connectivity remain **unverified** for this cycle. Version remains `0.1.0-dev`, RC acceptance blocked.
- Last user-confirmed commit: RC-readiness-integration cumulative with green CI. All the changes above are subsequent, uncommitted work.
- Next priorities: operational end-to-end verification, UX polishing, MFA notification path, SSO configuration UI, full calendar presentation, and validation that the database migration works against existing installations.

## Correzione CI TypeScript navigazione (2026-10-23)
- **Errore osservato nella CI:** `apps/web/src/main.tsx`, TS2345 nella navigazione admin: le voci condizionali venivano inferite come `string[][]`, perdendo il tipo letterale accettato da `setDashboardPage`.
- **Correzione:** tuple letterali (`as const`) nelle sole voci riservate agli admin, preservando il controllo statico TypeScript senza cast del parametro o ampliamento del tipo dello stato.
- **Regressione:** aggiunto `tools/tests/test_dashboard_navigation_types.py`. Resta necessaria una nuova build npm completa tramite GitHub Actions per confermare la compilazione.
- Restano inclusi gli interventi del precedente collaudo; versione invariata, nessun commit effettuato.

## Ciclo 2026-10-23 — paginazione server, calendario e ciclo di vita (non ancora committato)
- Ricerca e paginazione server-side di utenti e sessioni (1–100 voci/pagina), rispettando i ruoli owner/collaboratore; mantenuta la compatibilità delle risposte legacy.
- Nuova tabella `session_appointments` con data, ora HH:MM, durata di 5–1440 minuti e fuso IANA, API del calendario globale filtrata per permessi e appuntamenti per singola sessione, vista mensile e editor appuntamenti.
- Stato sessione `paused`, con pausa e ripresa; l'invio delle risposte rimane limitato alle sessioni attive.
- Navigazione iniziale a tab per l'editor e adattamento responsive del calendario.
- Verifiche locali: 82 test Node e 75 test Python superati. Build TS completa, migrazione PostgreSQL con dati esistenti e collaudi reali browser/container ancora obbligatori.
- **Da completare**: MFA amministrativa completa, secondo fattore email, gestione completa SSO dalla UI, audit accessibilità/responsive, conversione globale dei controlli sì/no a toggle e test end-to-end. RC non ancora validata.

## Aggiornamento post-collaudo UI e profili (23 ottobre 2026)
- Foto profilo caricate direttamente con streaming privato (PNG/JPEG/WebP, massimo 5 MB), scansione antivirus, sostituzione ed eliminazione; accesso pubblico alle foto dei presentatori vincolato alla sessione.
- Nickname inizializzato dal profilo corrente; rimosso l'inserimento di URL esterni per la foto.
- Toolbox con drag & drop nel canvas esistente; widget spostabili e rimovibili.
- Notifiche chiudibili con clic, pulsante e tasto Escape; migliorata la sovrapposizione visiva.
- Test di regressione aggiunti. **Ancora aperti**: esperienza completa tipo PowerPoint (widget immagine/video dedicati, catalogo integrale, miniature pagine e navigazione), verifica responsive nel browser, compilazione completa in CI e test operativi.


### 2026-10-23: Prova sessione nel browser e widget post-it
Aggiunto alla dashboard un dialogo di prova come partecipante con risposte locali, navigazione pagine e reset: non invia risposte all’API e non equivale a un collaudo E2E con partecipanti veri. Aggiunto il post-it al canvas e alla validazione condivisa. Rimangono da completare widget media con accesso sicuro, rifiniture dell’editor, MFA amministrativa, SSO via web e prove browser/CI.

Widget media, navigazione pagine e toggle implementati nei sorgenti; chiusura stimata gate RC 63%, collaudi E2E aperti.

## 2026-10-23 — Canvas slide a tutto schermo e riordino visuale
- L'editor usa un canvas 16:9, spostamento trascinando il corpo del widget e ridimensionamento da otto bordi/angoli. Le dimensioni sono salvate in percentuale; `height` è opzionale per compatibilità con le vecchie pagine.
- Rimossi i pulsanti di larghezza `+`/`−`; mantenuto il piccolo controllo di rimozione sul bordo.
- Aggiunto il comando di editor a schermo intero e riordino drag & drop nella barra delle slide, tramite l'API transazionale esistente.
- La simulazione partecipante rispetta le altezze salvate; aggiunti test delle geometrie.
- Test locali Node e Python eseguiti. La build TypeScript completa, il comportamento browser e i collaudi E2E devono essere verificati in CI e su un'installazione reale; restano aperti i flussi SSO/MFA e altri gate RC.

## 2026-10-23 — Righelli, rotazione, reflow mobile, domande per argomento e anteprima presentatore

- Editor bianco 16:9 con righelli percentuali; movimento dal corpo del widget, ridimensionamento ai bordi e rotazione arbitraria da maniglia dedicata (angolo salvato). Restano modalità fullscreen e riordino delle slide.
- Layout live su mobile adattato in blocchi verticali per la leggibilità; la rotazione salvata viene ignorata solo sul piccolo schermo.
- La dashboard espone anteprima incorporata e collegamento alla schermata pubblica di presentazione/risultati.
- Nuovo widget `topic-question` ripetibile: invii indipendenti per argomento in PostgreSQL, elenco del presentatore paginato a 10 domande, pseudonimo facoltativo disattivato per impostazione predefinita, aggiornamento periodico; dieci invii per partecipante/widget.
- Test mirati completati. **Da validare in CI/browser/PostgreSQL reali:** compilazione integrale, trascinamenti, responsive e migrazione dati. Consulta `docs/SLIDE_RULERS_ROTATION_TOPICS.it.md`.
- Stima di chiusura gate RC **67%** (prima 65%); non equivale a certificazione production-ready.

## 2026-10-23 — Geometria dei widget accessibile da tastiera (non committato)
- I widget del canvas sono selezionabili con Tab: frecce per spostamento (1 punto percentuale), Maiusc+frecce per ridimensionamento, Alt+frecce per rotazione (5 gradi). Ctrl abilita regolazioni fini (0,1 punti percentuali o 1 grado). Le operazioni rispettano i limiti del canvas e sfruttano il normale percorso di persistenza della geometria. I controlli di inserimento testo e i pulsanti non sono intercettati. Aggiunti indicatori di focus e istruzioni accessibili.
- Verifiche del ciclo: compilazione backend TypeScript **SUPERATA** e frontend TypeScript/Vite **SUPERATA** (1.579 moduli); Node **85/85 SUPERATI**; Python **91/91 SUPERATI**, compresi tre nuovi controlli contrattuali. Mancano prove su browser reale e tecnologie assistive; il gate accessibilità non è chiuso.
- Stima gate RC invariata al **67%**; restano verifiche reali browser, database, CI, multi-replica e deployment. Nessun commit/push/tag/release effettuato. Le modifiche dopo l'ultimo commit con CI verde dichiarato dall'utente restano non committate.

## 2026-10-23 — Posizionamento dei Risultati e domande per argomento (non committato)
- Il pulsante `results-button` nella proiezione segue ora l'intero rettangolo e la rotazione salvati; resta un pulsante di riserva per le pagine precedenti. I risultati sono visibili soltanto al presentatore tramite un pannello espandibile accessibile.
- Il pannello mostra statistiche dell'attività, classifica quiz a tempo se applicabile ed elenchi paginati (10/pagina) per ciascun widget di domande per argomento.
- Verifiche locali: build backend TypeScript e frontend Vite PASS; Node 90/90 PASS; Python 93/93 PASS, inclusi due nuovi test contrattuali. Test E2E con browser e PostgreSQL non eseguiti.
- **Chiusura gate RC confermata al 67%**. Mancano grafici configurabili per singolo widget, quiz a tempo indipendenti e verifiche reali di sincronizzazione/deployment. Nessuna nuova CI confermata, commit o release.

## Current cycle (2026-10-23)
2026-10-23 — Scelta visualizzazione risultati sul widget `results-button`: barre, torta, tabella; persistenza tramite layout. Build backend/frontend e test 90 Node + 93 Python PASS. **Ancora aperti** configurazione per singolo widget, quiz a tempo multipli indipendenti, E2E browser/PostgreSQL, allineamento manuali PDF. CI verde precedente confermata dall’utente (baseline prima di questo ciclo); nessun commit eseguito in questo ciclo. Gate RC 67% invariati.

## 23 ottobre 2026 — Paginazione della classifica quiz a tempo (dopo il commit, CI utente da eseguire)
- L'utente ha confermato **commit e CI verde** per `quorivio-0.1.0-dev-presenter-results-canvas-cumulative.zip`: questo è il riferimento dell'ultimo commit. I cicli relativi ai grafici dei risultati e alla paginazione non sono ancora committati. Le annotazioni storiche precedenti rimangono tali.
- La classifica riservata ai presentatori è paginata a 20 risposte corrette per pagina; ordinamento stabile per tempo registrato dal server, timestamp di invio e ID. La posizione in classifica continua tra le pagine; navigazione nel pannello Risultati con aggiornamento ogni due secondi.
- Build di produzione backend/frontend **PASS**; test Node **90/90 PASS**, Python **93/93 PASS**. Non eseguiti collaudi E2E con browser e database per questa funzione.
- **Avanzamento RC invariato al 67%**. Ancora aperti quiz indipendenti multipli, grafici per singolo widget, MFA email, invalidazione cookie dopo reset MFA e collaudi infrastrutturali. La RC non è raggiunta.

## 2026-10-23 — Revoca delle sessioni dopo reset MFA (non committato)
- Il reset MFA amministrativo aggiorna transazionalmente `users.auth_revoked_at`: i cookie emessi in precedenza sono respinti dalle API protette e dalle nuove connessioni WebSocket del presentatore. Rimane la chiusura delle connessioni locali già presente.
- Aggiunti migrazione SQL incrementale, due regressioni e note tecniche IT/EN. **Restano aperti i collaudi PostgreSQL e la chiusura proattiva dei WebSocket sulle altre repliche.**
- Ultimo commit/CI verde confermato dall'utente: `presenter-results-canvas`. Gli interventi successivi non risultano committati. Chiusura gate RC invariata: **67%**.

## 23 ottobre 2026 — Interventi accorpati di sicurezza (successivi all'ultimo commit confermato)
- L'upgrade WebSocket verifica ora l'origine completa dell'URL pubblico (schema, host e porta), invece del solo host, coerentemente con la protezione delle API HTTP che modificano dati. Restano supportati i client non-browser autenticati senza header Origin.
- Entrambi gli endpoint delle classifiche rifiutano paginazioni ambigue, frazionarie o fuori limite con HTTP 400, senza più forzare silenziosamente il valore. Dimensione e ordinamento delle classifiche rimangono invariati.
- Verifiche: build backend TypeScript PASS; build produzione frontend Vite PASS (1579 moduli); 99/99 test Node.js PASS; 95/95 test Python PASS. Collaudi E2E PostgreSQL, browser, SSO reale e Kubernetes ancora mancanti.
- Audit RC **37,5%** (37,5/100), invariato in assenza di nuove evidenze di accettazione. Non è una percentuale di righe di codice implementate.
- Tutti gli interventi dal commit `presenter-results-canvas` restano non committati; nessun commit, push, tag o release.


## 2026-10-23 — Email MFA flow
MFA email: aggiunti challenge PostgreSQL monouso, verifica login, UI e impostazione; build e test di contratto superati; collaudi E2E ancora necessari.
RC weighted gate score unchanged at 37.5%; email MFA is partial until PostgreSQL/SMTP/browser integration passes.


### 2026-10-23 – Protezione emissione MFA email
Limite condiviso tra repliche (3/account/minuto), una sola sfida attiva atomica, pulizia migrazione e indice univoco. Dettagli in `docs/EMAIL_MFA_ISSUANCE_HARDENING.it.md`. Gate RC invariati in attesa di prove di integrazione.
