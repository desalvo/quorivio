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

Per backup/verifica/ripristino PostgreSQL + asset utilizzare `tools/instance_backup.py` seguendo `docs/INSTANCE_BACKUP.it.md`. Il wizard Kubernetes permette di configurare il PVC degli asset con `asset_storage_size`, `asset_storage_class` e `asset_access_mode`. Non è ancora disponibile un workflow da interfaccia admin né una procedura di disaster recovery validata in produzione.

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
Il presentatore può caricare PDF/PPTX tramite `/api/sessions/:id/presentation-import` (massimo 100 MiB, 200 pagine). La funzione è disabilitata per default: richiede `QUORIVIO_ENABLE_CONVERTER=true`, Python/Poppler e LibreOffice per PPTX. **Il subprocess attuale non è isolato in un container dedicato e non deve essere abilitato in produzione prima dei collaudi di sicurezza.** Le nuove slide vengono salvate nella medesima transazione database.

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
