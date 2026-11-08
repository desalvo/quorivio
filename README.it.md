> **RC269 — Autenticazione e gestione sessioni:** login automatico alla scadenza, pulizia conservativa ogni 12 ore, trasferimento proprietà, LDAP/LDAPS opzionale e correzioni sidebar/risposte smartphone. [Note RC269](docs/RC_CYCLE269_LDAP_OWNERSHIP_HOUSEKEEPING.it.md).

> **RC267 — Hotfix CI Node:** risolve l’errore shell 126 nel preflight RC266 e verifica l’esatta invocazione dei test. Funzionalità di finestre flottanti RC266 e importazione full-bleed RC265 invariate. [`Note RC267`](docs/RC_CYCLE267_CI_NODE_RUNNER_CONTINUATION.it.md).

> **RC266 — Hotfix CI partecipante:** adeguato il contratto RC173/RC227 al canvas full-bleed RC265, senza modificare il runtime. [`Note RC266`](docs/RC_CYCLE266_PARTICIPANT_BACKGROUND_CI_FIX.it.md). **Aggiornamento editor:** finestre flottanti spostabili fino ai bordi e ridimensionabili (mouse/touch/tastiera). Corrette anche le coordinate con zoom UI al 70–120%.

> **RC265 — PDF/PPTX full canvas:** importazione come immagini con `cover` predefinito, `contain` o `fill` forzato; schema, titoli, footer e numero pagina nascosti di default; miniature reali. [`Documentazione RC265`](docs/RC_CYCLE265_PDF_FULL_BLEED_IMPORT.it.md).

> **RC264 — Correzione CI Pillow:** la suite pre-npm non richiede Pillow né Poppler per i test sintetici di pubblicazione PDF; la verifica dei PNG reali rimane obbligatoria. Vedi [`docs/RC_CYCLE264_PILLOW_CI_FIX.it.md`](docs/RC_CYCLE264_PILLOW_CI_FIX.it.md).

> **RC263 — Correzione CI e wizard PostgreSQL:** I test PDF simulano Poppler anche sui runner senza binari; il wizard accetta solo i due valori predefiniti di Kubernetes nella sonda DB, senza allentare i controlli su sicurezza o volumi. Per un rollout già completato usare `--sync-disk-monitor` senza riavviare PostgreSQL. Vedi [`docs/RC_CYCLE263_CI_KUBERNETES_DEFAULTS.it.md`](docs/RC_CYCLE263_CI_KUBERNETES_DEFAULTS.it.md).

> **RC262 — Monitoraggio spazio disco:** Configurazione server mostra occupazione dei volumi allegati, conversioni e dati PostgreSQL. Al 90% avvisa via SMTP gli amministratori di piattaforma; riarmo all’85%. Il wizard Kubernetes standalone offre un piano controllato per aggiungere la sonda PostgreSQL, con conferma esplicita del riavvio del database. Vedi [`docs/RC_CYCLE262_DISK_CAPACITY_MONITORING.it.md`](docs/RC_CYCLE262_DISK_CAPACITY_MONITORING.it.md).

> **RC261 — Converter Kubernetes:** corretta la pubblicazione PDF/PPTX tra `/tmp` e `/conversions` su mount differenti (`EXDEV`), aggiornamento obbligatorio `zlib1g` per il gate Trivy e sincronizzazione dell’immagine nel wizard. Pubblicare manualmente la nuova immagine dopo full CI verde. Vedi [`docs/RC_CYCLE261_CONVERTER_CROSS_MOUNT_AND_ZLIB_CI.it.md`](docs/RC_CYCLE261_CONVERTER_CROSS_MOUNT_AND_ZLIB_CI.it.md).

> **RC260 — Kubernetes:** il wizard sincronizza i manifest originari in `generated` dopo un upgrade del converter; per converter esistente usare `--sync-generated --generated-dir ./generated`. Vedi [`docs/RC_CYCLE260_KUBERNETES_GENERATED_RECONCILIATION.it.md`](docs/RC_CYCLE260_KUBERNETES_GENERATED_RECONCILIATION.it.md).

> **RC259 — Wizard Kubernetes standalone auto-aggiornante.** `python3 k8s_wizard.py --version` mostra la versione installata; ogni comando operativo controlla l’ultima versione su GitHub `desalvo/quorivio`, aggiorna atomicamente lo script e riavvia automaticamente gli argomenti originali. `--no-self-update` abilita esplicitamente la manutenzione offline. Non serve il repository. Dettagli: [`docs/RC_CYCLE259_WIZARD_GITHUB_AUTOUPDATE_AND_PPTX_CI.it.md`](docs/RC_CYCLE259_WIZARD_GITHUB_AUTOUPDATE_AND_PPTX_CI.it.md).

# Quorivio 0.1.0-dev

> **RC220:** La RC219 è la baseline full CI verde (run `42197607753`). In RC220 è disponibile **Configurazione server → Convertitore PDF / PowerPoint** per amministratori. Le opzioni dei risultati collegati per titolo e risposte sono indipendenti. Vedi `docs/RC_CYCLE220_PDF_WORKER_AND_LINKED_RESULTS.it.md`. La nuova RC220 necessita ancora della CI.

> **Stato RC (2 novembre 2026):** RC135 ha superato la CI completa GitHub (run 41437489546). La RC formale **non è ancora approvata**: 43/60 gate accettati, 17 parziali; certificato 85,25%. Procedura per i fascicoli di prova privati e la revisione indipendente: [`docs/RC136_EXTERNAL_ACCEPTANCE_IT.md`](docs/RC136_EXTERNAL_ACCEPTANCE_IT.md). Non caricare in Git le evidenze private e non confondere CI verde con certificazioni legali o su dispositivi reali.

## Cronologia dello sviluppo

**Checkpoint RC (26/10/2026):** Baseline committata e verde, GitHub Actions 40335963980. Da questo nuovo batch non committato, Docker Hub pubblica **solo con `workflow_dispatch` e `publish_image=true`**; i push e i tag non aggiornano più `latest`. Aggiunti test MFA email su SMTP TLS/PG effimeri, nuova CI ancora necessaria. Avanzamento RC verificabile **48,0%** (D6 partial, non un’approvazione AGID/GDPR). Consulta [resoconto batch](docs/RC_MANUAL_PUBLICATION_MFA_BATCH.it.md) e [guida Docker Hub](docs/GITHUB_DOCKERHUB.it.md).

**Ultimo ciclo profili (26 ottobre 2026, non committato):** Foto presentatore accessibili nelle sessioni pubbliche tramite URL limitati alla sessione; nickname e nome salvati atomicamente con un unico pulsante e caricamento automatico. La CI estesa precedente `40304413948` è verde e committata. Localmente 317 test Node, 660 Python e build API/web PASS; collaudo PostgreSQL/browser del nuovo ciclo ancora da eseguire. Vedi `docs/DEVELOPMENT_STATUS.it.md`.

**Hotfix CI Chromium PostgreSQL: modifica titoli (26/10/2026):** Il collaudo editor reale utilizza il menu contestuale accessibile del widget (`Menu contestuale text` → `Modifica titolo`) anziché fare doppio clic sull’input `readonly` che non riceve eventi del puntatore. Un test isolato Chromium precede il collaudo con database; CI estesa ancora da confermare. Dettagli in `docs/DEVELOPMENT_STATUS.it.md`.

**Hotfix CI full Chromium (25 ottobre 2026):** l’informativa sui cookie funzionali usa un portale React sul `document.body` per evitare che la dashboard intercetti il clic di conferma. La CI standard 40213703957 è verde; la CI full Chromium deve essere rieseguita.

**Hotfix CI Chromium (25/10/2026):** Il collaudo browser dell’editor conferma ora il dialogo accessibile dei cookie funzionali nei contesti desktop/mobile e PostgreSQL reale prima dei clic sui controlli. Nessun clic forzato o cookie iniettato; dettagli in `docs/DEVELOPMENT_STATUS.it.md`.


### Ultimo ciclo di sviluppo — Editing concorrente

Dopo la CI verde 40192172978 (qualità, build container e pubblicazione), questo batch introduce la protezione PostgreSQL contro salvataggi concorrenti della stessa pagina, recupero esplicito delle bozze in conflitto, correzione del rilevamento degli sfondi modificati e nuovi test reali PostgreSQL/Chromium. Il nuovo batch **non è ancora validato dalla CI**; vedere `docs/RC_EDITOR_NINTH_30_CYCLES.it.md`.

**Checkpoint sviluppo (25 ottobre 2026):** Otto lotti di conversione non committati, 240 interventi/scenari cumulativi dopo la baseline Audience 20 Cycles con CI verde; nuova fedeltà di riempimenti e contorni PowerPoint modificabili. Locale: 583 Python + 232 Node PASS, build API/web PASS. Nuova CI GitHub da eseguire; RC 45,5%. Vedi `docs/RC_CONVERSION_EIGHTH_30_CYCLES.it.md`.

> **Ultimo ciclo (22/10/2026):** Aggiunti riordino transazionale delle pagine e duplicazione delle definizioni senza voti. Vedere `docs/PAGE_SEQUENCE.it.md`. Test unitari locali superati; integrazione PostgreSQL/browser ancora da verificare. Funzionalità stimate **80%**, readiness **35%**.

# Quorivio — 0.1.0-dev

**Autore:** Alessandro De Salvo <braket71@gmail.com>  
**Sorgenti:** https://github.com/desalvo/quorivio  
**Licenza:** EUPL-1.2 (vedere LICENSE; inclusione del testo integrale ufficiale ancora da completare)  
**Docker:** `desalvo/quorivio`

Quorivio è una piattaforma web autonoma per presentazioni interattive, sondaggi, quiz e risultati in diretta. Supporta sessioni indipendenti dalle presentazioni esterne e QR code riutilizzabili. Questa è una **versione iniziale di sviluppo, non ancora validata per produzione**.

- Manuali: `docs/manuals/user-guide.it.pdf`, `docs/manuals/admin-guide.it.pdf` (disponibili anche nell'interfaccia).
- Configurazione GitHub/Docker Hub: `docs/GITHUB_DOCKERHUB.it.md`.
- Wizard Kubernetes Kustomize: `docs/KUBERNETES.it.md`.
- Stato effettivo: `docs/DEVELOPMENT_STATUS.it.md`, dettaglio `docs/DEVELOPMENT_STATUS.md`.

Per avviare l'ambiente locale, leggere anche il [README inglese](README.md) e configurare il file di esempio `.env.compose.example`; verificare `PUBLIC_BASE_URL`, credenziali e policy prima di ogni esposizione Internet.

### Kubernetes e GDPR (lavori in corso)

Il wizard supporta NGINX, due annotazioni HAProxy legacy, PostgreSQL 18 interno o PostgreSQL esterno con TLS. Vedi [Kubernetes](docs/KUBERNETES.it.md) e [registro GDPR](docs/GDPR.it.md). Nessuna prova su cluster reale o attestazione di conformità GDPR.

### API ciclo di vita dei dati (sviluppo)

Il proprietario autenticato può revocare una sessione (`POST /api/sessions/:id/revoke`), cancellarla con i dati collegati (`DELETE /api/sessions/:id`) o configurare la retention (`PATCH /api/sessions/:id/retention`, JSON `{ "retention_days": 90 }`). Una procedura periodica elimina le sessioni chiuse/scadute oltre il periodo impostato. Servono ancora test PostgreSQL e revisione privacy prima dell'uso in produzione; vedere `docs/GDPR.it.md`.


## Avanzamento del progetto

Completamento funzionale **34%** (`███░░░░░░░`), production readiness **36%** (`████░░░░░░`). Sono stime e non certificazioni. Consultare `docs/DEVELOPMENT_STATUS.it.md`.

Manuali partecipante, presentatore e amministratore IT/EN nella directory `docs/manuals/` e nella UI. Rigenerare con `python3 tools/generate_manuals.py`.

### Identità e contenuti multimediali (0.1.0-dev)

Introdotti nei sorgenti: registrazione con approvazione, gestione utenti e ruoli admin, cambio obbligatorio password iniziale, anonimato con pseudonimo e cookie tecnico, URL esterna configurabile, contenuti per pagina e controllo visibilità risultati live. **Funzioni non ancora collaudate per produzione**. SSO, MFA, SMTP/SMTPS, upload sicuro, editor risultati e XLSX sono ancora incompleti; vedere `docs/REQUIREMENTS_IDENTITY_MEDIA.it.md`. Password admin demo `000000` disponibile solo con `ALLOW_INSECURE_DEV_BOOTSTRAP=true` fuori dalla produzione.

### Sessioni collaborative e upload
Vedi [documentazione](docs/COLLABORATION_BACKUPS_UPLOADS.it.md). Il wizard `--set max_upload_mb=100` aggiorna il manifest Ingress; modificare il valore dalla UI amministrativa non aggiorna automaticamente Kubernetes. Non è ancora disponibile un servizio di upload file né il backup/ripristino completo dalla UI.

I manuali dettagliati IT/EN sono rigenerabili con `python3 tools/generate_manuals.py` (richiede reportlab e Pillow). Includono procedure operative e limiti delle funzionalità ancora non verificate.


Note sul caricamento binario delle sessioni: [docs/ASSET_UPLOADS.it.md](docs/ASSET_UPLOADS.it.md).

### Allegati e report di sessione (sviluppo)

Caricamento, elenco, apertura autenticata ed eliminazione degli allegati e report JSON aggregati sono descritti in [Procedure allegati](docs/ASSET_WORKFLOWS.it.md). Gli amministratori possono impostare il limite upload (100 MB predefiniti) e devono rigenerare i manifest Ingress Kubernetes in caso di modifica. Non è un backup integrale.

### Manutenzione offline dell'istanza

Per backup/verifica/ripristino PostgreSQL + asset utilizzare `tools/instance_backup.py` seguendo `docs/INSTANCE_BACKUP.it.md`. Prima di esportare gli archivi, proteggerli con cifratura autenticata AES-256-GCM e rotazione delle chiavi secondo `docs/DR_ENCRYPTED_BACKUPS.it.md`; il `tar.gz` originale non è cifrato automaticamente. Il wizard Kubernetes permette di configurare il PVC degli asset con `asset_storage_size`, `asset_storage_class` e `asset_access_mode`. Non è ancora disponibile un workflow da interfaccia admin né una procedura di disaster recovery validata in produzione.

Quiz e reazioni: [guida italiana](docs/QUIZ_REACTIONS.it.md).

Compositore widget: gradimento 0–10, reazioni, testo, divisore, segnaposto timer/QR; riordino drag & drop. Vedi docs/WIDGETS.it.md.

## Strumenti per il pubblico (sviluppo)
La versione 0.1.0-dev include parole frequenti e Q&A moderato con voto univoco dei partecipanti. Vedi `docs/AUDIENCE_TOOLS.it.md`. Mancano ancora i test reali di integrazione con PostgreSQL e browser.

### Widget avanzati (sviluppo)
I gradimenti richiedono un titolo e accettano un commento facoltativo del partecipante (fino a 1000 caratteri). Editor di stili, animazioni e widget domanda parzialmente disponibile. Canvas libero e risposte indipendenti per widget non ancora completati. Vedi `docs/PAGE_WIDGET_EDITOR.it.md`.

### Widget domanda indipendenti
Il presentatore può aggiungere più domande indipendenti nella stessa pagina. Ognuna riceve una risposta distinta (scelta singola/multipla, testo o riferimento a file già caricato). Consultare `docs/INDEPENDENT_QUESTION_WIDGETS.it.md`. Mancano collaudi PostgreSQL/browser.

Revisioni delle domande-widget e statistiche distinte per revisione: vedere [guida](docs/WIDGET_REVISIONS.it.md).

Upload dei partecipanti per widget file: vedere `docs/PARTICIPANT_UPLOADS.it.md`; ancora da validare per la produzione.

Upload in streaming: gli allegati di presentatori e partecipanti sono scritti su file temporanei privati e limitati; vedere `docs/STREAMING_UPLOADS.it.md`. Non ancora validati per la produzione.

### Conversione offline presentazioni (anteprima sviluppo)

`python3 tools/import_presentation.py slides.pdf ./slides-rendered` converte PDF e PPTX in pagine PNG e un manifest di integrità. Vedi [guida all'importazione](docs/PRESENTATION_IMPORT.it.md). **Non è ancora integrata** nell'interfaccia/API delle sessioni; in produzione servirà un worker isolato.


### Integrated slide pages / Pagine slide integrate

Slide integrate: carica un gruppo di immagini PNG/JPEG/WebP dal workspace del presentatore per inserirle come pagine; i PDF/PPTX devono ancora essere convertiti offline con tools/import_presentation.py.

### Import PDF/PPTX da browser (sperimentale)
Il presentatore può importare PDF/PPTX in pagine-immagine (massimo 100 MiB e 200 pagine) tramite `/api/sessions/:id/presentation-import`. La conversione viene eseguita esclusivamente nel **worker isolato** del deployment, mai in un subprocess dell'API. L'amministratore verifica e attiva la disponibilità da **Configurazione server → Convertitore PDF / PowerPoint**; la pagina indica i prerequisiti mancanti. Servono `QUORIVIO_ENABLE_CONVERTER=true`, URL interno del worker e token segreto valido. Compose e Helm includono il worker, ma occorre configurarne il Secret/ambiente e verificarne lo stato. Vedi [`docs/ISOLATED_CONVERTER.it.md`](docs/ISOLATED_CONVERTER.it.md) e [`docs/RC_CYCLE220_PDF_WORKER_AND_LINKED_RESULTS.it.md`](docs/RC_CYCLE220_PDF_WORKER_AND_LINKED_RESULTS.it.md).

### MFA e SMTP (0.1.0-dev)

Il login locale supporta ora MFA TOTP facoltativo, attivabile dal profilo dopo la conferma con un codice autenticatore. SMTP/SMTPS può essere configurato via variabili d'ambiente, con verifica configurazione e invio di prova dall'amministrazione. Consultare `docs/AUTHENTICATION_SERVICES.it.md` per prerequisiti, limiti e sicurezza. SSO social e generic OIDC restano da implementare.

### Recupero password (sviluppo)
La schermata di login consente di richiedere link monouso via SMTPS. Configurare `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` e `PUBLIC_BASE_URL` HTTPS. Vedere `docs/PASSWORD_RECOVERY.it.md`. L'MFA rimane attivo dopo il reset. Sono ancora necessari collaudi reali di integrazione e sicurezza.

MFA include dieci codici di recupero monouso mostrati all’attivazione TOTP; vedere `docs/MFA_RECOVERY_CODES.it.md`. Test reali PostgreSQL/browser ancora da eseguire.

### Autenticazione federata (sviluppo)

Sono disponibili un primo login OpenID Connect e il collegamento esplicito degli account con provider Google, generic OIDC o custom configurati (vedere `docs/OIDC_SSO.it.md`). GitHub/Facebook OAuth e SAML non sono ancora implementati. La federazione non è collaudata con provider reali né su più repliche: non abilitarla in produzione senza i necessari test.

### OAuth sociale (sviluppo)
Collegamento e accesso OAuth2 con GitHub e Facebook implementati come flussi opzionali HTTPS. Richiedono client registrati, non sono ancora collaudati con provider reali e non sono pronti per repliche multiple. Vedere `docs/SOCIAL_OAUTH.it.md`.

### Antivirus degli allegati (nuova integrazione opzionale)

Gli allegati dei partecipanti e dei presentatori e i documenti importati possono essere verificati da un servizio ClamAV privato tramite `INSTREAM`. Impostare `QUORIVIO_AV_REQUIRED=true`, `CLAMAV_HOST` ed eventualmente `CLAMAV_PORT=3310`; l'impostazione predefinita non è sicura per la produzione. Il servizio incluso in Compose o nel pod Helm viene avviato con Quorivio; verificarlo con un runtime container reale. Dettagli: [Scansione antivirus](docs/ANTIVIRUS_UPLOADS.it.md).


Custom OIDC SSO provider registration: `OIDC_PROVIDERS_JSON` (see `docs/OIDC_PROVIDERS.it.md`).


## Antivirus gestito e configurazione SSO

Il deployment avvia automaticamente ClamAV in una rete privata e rifiuta gli upload non verificati. Gli endpoint standard Google, GitHub e Facebook sono preconfigurati; aggiungere credenziali e callback registrate. Consultare [la guida](docs/MANAGED_ANTIVIRUS_AND_SSO.it.md).


Convertitore presentazioni isolato: vedere [le istruzioni di distribuzione](docs/ISOLATED_CONVERTER.it.md). Configurare `QUORIVIO_WORKER_TOKEN` prima di abilitare le conversioni.

### Checkpoint sviluppo — settimo lotto conversione senza commit (25 ottobre 2026)

Il package cumulativo include **sette lotti di conversione ancora non committati (210 interventi/scenari)** successivi all'ultimo commit Audience 20 Cycles con CI verde. Il lotto più recente preserva il ritaglio nativo modificabile delle immagini PowerPoint durante importazione, editor, proiezione/anteprima ed esportazione PPTX. Inventario e verifiche: [`docs/RC_CONVERSION_SEVENTH_30_CYCLES.it.md`](docs/RC_CONVERSION_SEVENTH_30_CYCLES.it.md). **La CI GitHub dei sette lotti non è stata ancora eseguita**; nessun gate RC promosso.


### Chromium native top-layer hotfix (2026-10-25)
La CI full 40215782964 falliva perché la dashboard intercettava il clic di conferma dei cookie, nonostante il portal nel body. L’informativa usa ora il dialog HTML nativo showModal() nel top layer del browser; i test opt-in verificano :modal ed eseguono il clic reale. Localmente Node 314/314, Python 630/630 e build API/web PASS; serve rieseguire Chromium end-to-end.


## CI controllata dal commit (RC102)

Un push su `main` con commit ordinario avvia la CI standard; `[full-ci]` avvia direttamente tutti i gate automatici estesi, senza pubblicare. Il marker esplicito `[publish-docker]` avvia la stessa campagna estesa e **solo quando tutti i gate risultano verdi** pubblica `desalvo/quorivio:sha-<12>` e `desalvo/quorivio:latest` nell'environment protetto `production`. Non usare questo marker se non vuoi aggiornare `latest`. La pubblicazione manuale `workflow_dispatch` rimane separata; mai pubblicazione da PR, branch diversi da `main` o test falliti. Configura la variabile `DOCKERHUB_USERNAME` e il segreto `DOCKERHUB_TOKEN`, più eventuali revisori richiesti nell'environment `production`.
**Novità RC221:** scegliere prima dell’import PDF/PPTX tra **immagini fedeli** nella sessione corrente e **elementi modificabili parzialmente** in una nuova sessione, con estrazione di testo nativo e immagini tramite worker isolato. Nei risultati: switch privato per risposte vere e formattazione autonoma di domande, risposte e righe statistiche. Vedi `docs/RC_CYCLE221_RESULTS_GRADING_AND_PDF_IMPORT.it.md`.


## RC270 — Backup, LDAP, audit, risultati

Le impostazioni per backup completi di istanza, destinazioni POSIX/NFS/S3/WebDAV, pianificazione, registro audit e retention sono in **Dashboard amministratore → Configurazione server**. L’approvazione delle registrazioni LDAP e la ricerca utenti directory sono nella sezione Utenti. Per Helm e wizard Kubernetes, e per i controlli richiesti prima di un restore, leggere `docs/RC_CYCLE270_FULL_BACKUP_LDAP_AUDIT_RESULTS.it.md`.
