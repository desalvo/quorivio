# Quorivio 0.1.0-dev — RC65 — CI historical documentation regression (31 ottobre 2026)

**Baseline committata dal manutentore:** `0786ef2f4b064080dd49b42f41d2f04b3d5f4c8a` (include RC64). La CI standard `41189697040` (job `124503743950`) ha superato 546 test API, 99 test web, build, integrazioni PostgreSQL, Kubernetes, verifiche di inventario prima della suite Python; il job si è fermato in `PYTHONPATH=tools python3 -m unittest discover -s tools/tests -v` con 2 failure su 1399 test, perché due regressioni storiche cercano ricevute RC58 solo nei primi 1700/2000 caratteri di documenti ai quali vengono prepese nuove sezioni.

**Correzione RC65:** contratti di regressione RC57/58 ricondotti a documenti completi e ricevute RC58 dedicate, senza tagli di prefisso; corretto anche il controllo RC35 con limitazione a 4000 caratteri e il test RC63 che richiedeva un inventario RC64 come sempre-current. L'inventario RC64 diventa storico immutato e RC65 è nuovo inventario sorgente corrente. Gli hash dei cicli precedenti non vengono riscritti. Non vengono disabilitati test, Gitleaks o limiti di sicurezza. Nessun nuovo credito RC finché non esiste una CI verde sul nuovo commit.

**RC ufficiale:** 81,75% (55 gate: 38 accettati/17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. La nuova CI deve eseguire prima suite Python completa, test Node, checksum e Gitleaks; le prove su veri provider e l'approvazione esterna restano aperte. Nessun commit, push o tag dell'assistente.

---
# Quorivio 0.1.0-dev — RC64 — Falso positivo Gitleaks nei test (31 ottobre 2026)

**Ultimo commit del manutentore:** `118480606d97e3e32ddf92991889c7a577ebfc02` (include RC63). La CI standard `41188841418`, job `124501245873`, ha superato 546 test API, 99 test web, build, integrazioni PostgreSQL, Kubernetes, Python e 50 verificatori d'inventario. Si è fermata all'ultimo controllo Gitleaks: la stringa fittizia statica nel test del rate limit RC62 viene interpretata come `generic-api-key`. Non è una credenziale reale trapelata.

**Correzione RC64:** sostituita la stringa con un valore di prova SHA-256 deterministico calcolato in esecuzione. In CI il vero token resta casuale, solo in ambienti non di produzione e per richieste loopback. Aggiunti controlli preventivi prima di npm; Gitleaks rimane obbligatorio senza allowlist o bypass, inventario RC63 mantenuto immutabile, nuovo inventario RC64 corrente. Per verificare il risultato occorre un nuovo commit dell'utente e una nuova esecuzione CI; rilanciare la CI sul vecchio commit non basta.

**Stato RC ufficiale:** **81,75%** (55 gate: 38 accettati e 17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Le precedenti CI verdi `41152434205`, `41152939003` e `41123318359` non certificano RC64. Restano collaudi su provider reali, RWX fisico multi-nodo, approvazioni indipendenti GDPR/AGID/sicurezza, accessibilità multi-dispositivo. Nessun commit/push/tag dall'assistente.

---
# Quorivio 0.1.0-dev — RC63 — Correzione manifest storici della CI standard (31 ottobre 2026)

**RC certified:** 81,75% (38 accepted, 17 partial of 55); strict RC BLOCKED.
**RC63 controls:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no new gate credit until GitHub acceptance.


**Storico verificato:** CI standard `41152434205` e CI estesa `41152939003` sul commit `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`; precedenti prove CI estese `41123318359`. Sono prove precedenti, **non** una certificazione del nuovo RC63.

**Baseline dell'ultimo commit utente:** `8e7d2df0f3badb39136f9901cd91acf2897ca453` (include RC62). La CI standard `41187779633`, job `124498103225`, ha superato la precedente anomalia HTTP 429, test Node, build, collaudi PostgreSQL, vulnerability gate. Si è arrestata in `tools/ci_inventory_reference_guard.py` con `ValueError: workflow referenced missing inventory manifest: docs/validation/RC_CYCLE59_PACKAGE_INVENTORY_20261031.json` durante i test Kubernetes/Python.

**Causa:** RC61 aveva escluso dal package cumulativo due ricevute storiche RC59 e RC60, pur conservando gli script e i riferimenti nella CI; RC62 non le aveva ripristinate. Non era una regressione del backend o della sicurezza SSO.

**Correzione:** ripristinate dai pacchetti originari, senza rigenerazione né modifica, le due ricevute `RC_CYCLE59_PACKAGE_INVENTORY_20261031.json` (SHA-256 `1b8249a51936669090377ca1d170576ad9fc01a0c94197e18a14ce4324f69121`) e `RC_CYCLE60_PACKAGE_INVENTORY_20261031.json` (SHA-256 `0fb86a1049a8c84512d4b5991c05f939ac2473621a014be2ffe83e6055732e5d`). Guard con ricevute immutable pin-nate, regressioni automatiche per presenza e assenza, verificatore RC63 in CI e inventario cumulativo RC63 da verificare prima del commit.

**Consegna:** RC63 cumulativo 0.1.0-dev, nessun commit/push/tag dal modello. CI standard deve essere rieseguita sul commit manuale successivo. La percentuale RC certificata resta **81,75%**, 38 gate accettati e 17 parziali su 55, RC strict bloccata. `publish_image=false`, `rc_strict=false`, `publish_latest=false`.

---

# Handoff — Quorivio RC62 (31 ottobre 2026)

**Ultimo commit dell'utente:** `5a088fc300037b5a6a98a533de36ac6700b3b765` (include RC61). CI standard `41186895267`, job `124495541784`, **fallita** per superamento rate limit PostgreSQL su loopback (risposta HTTP 429 al test sfondi; atteso 200), dopo test Node, build e suite SSO reali superate. **RC62 è l'unico ciclo non committato** dopo quella baseline. Correzione: i due test HTTP portable/sfondi inoltrano il token random temporaneo già presente in CI; guardia fail-closed vincolata a host loopback; nessun cambiamento al backend production. Aggiornati workflow, test, handoff, inventario. Vedere `docs/RC62_CI_THROTTLE_ISOLATION.it.md`. **RC 81,75% verificato (38 accepted/17 partial su 55), strict bloccata.** Fare commit manuale RC62 e verificare prima la CI standard, poi eventuale estesa, senza pubblicazione.

---

# Handoff — Quorivio RC61, 31 ottobre 2026

**Ultimo commit confermato:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`; CI standard `41152434205`, estesa `41152939003` relative soltanto a questa baseline. **Cicli 58–61 non ancora committati.** RC certificata **81,75%**, 38 gate accepted, 17 partial su 55, strict RC NO. `rc_strict=false`, `publish_image=false`. Nuovo scope: SSO elenco privato e scollegamento confermato con password, lock+revoca transazionali, limite distribuito, UI e prova PostgreSQL HTTP in CI; verifiche locali **546 API**, **99 frontend**. Build npm e prova DB in CI non confermate. Dettagli `docs/RC61_FEDERATED_IDENTITY_MANAGEMENT.it.md`. Fare commit manualmente, poi CI standard e campagna RC non pubblicante; non forzare la percentuale.

---

# Quorivio 0.1.0-dev — handoff ciclo RC60 (31 ottobre 2026)

**Baseline confermata** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0` (CI standard `41152434205` ed estesa `41152939003` superate). **Cicli 58–60 cumulativi NON committati.** Gate RC **81,75%**, 38 accettati e 17 parziali su 55; strict RC NON pronta. Nessun publish/commit/tag/push dall'assistente.

Nuovo ciclo 60: revoca sicura del collegamento account OAuth/OIDC, sessione valida al start e al callback dopo reset password/revoca MFA, PostgreSQL `link_auth_issued_at_ms`, prove Node e CI database; dettagli `docs/RC60_FEDERATED_LINK_REVOCATION.it.md`. Passati localmente **541 test API**, **99 web Node**. Nuova CI PostgreSQL e build completa non verificate localmente. Restano gate fisici RWX, provider/SMTP reali, HTTPS KIND (non eseguito nella CI di riferimento) e approvazioni GDPR/AGID/manuali/UX indipendenti.

**Prossimo passo:** dopo il commit del manutentore eseguire prima CI standard, poi una singola campagna `rc_acceptance_suite=true`, `publish_image=false`, `rc_strict=false`, `publish_latest=false`; non lanciare campagne concorrenti sulla stessa ref. Mantenere il file `docs/RC_GATE_MATRIX.json` invariato finché non c'è nuova evidenza. 

---

# Quorivio 0.1.0-dev — sprint RC59 per macroaree (31 ottobre 2026)

**Ultimo commit confermato:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`; CI standard `41152434205`, estesa `41152939003` superate. **RC certificata 81,75% (55 gate, 38 accettati, 17 parziali); RC strict NON PRONTA.** Cicli **58–59 non ancora committati**, cumulativi. Campagna GitHub completa con un solo input per 13 gruppi di prove CI e verdetto finale obbligatorio su 11 job; `publish_image=false`, `rc_strict=false`. Le risposte OAuth/OIDC ora hanno limite di byte effettivo durante lo streaming; lo stato è già archiviato su PostgreSQL tra repliche. Nessun aumento da prove non eseguite, KIND host-bind non è vero storage RWX e le approvazioni esterne rimangono necessarie. Vedere `docs/RC59_ACCELERATED_CLOSURE.it.md`. Nessun commit/push/tag da parte dell'assistente.

---

# Quorivio 0.1.0-dev — Handoff ciclo 58 (31 ottobre 2026)

**Baseline committata `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`:** CI standard `41152434205` / estesa `41152939003` verdi, inclusa prova reale idle 70s e 500 partecipanti global p95 nel job `124393360139`. **Completamento RC 81,75%** (55 gate, 38 accettati/17 parziali), credito +0,50 solo alle due prove nuove. Ciclo 58 non committato: limitazione a 8 refresh PostgreSQL simultanei fra sessioni distinte, regressioni locali e catena SHA-256 da validare dopo il commit. TLS KIND non abilitato nella CI verificata, nessuna certificazione CSI RWX fisica. `publish_image=false`, `rc_strict=false`; mai commit/push/tag dell'assistente. Documenti: `docs/RC58_VERIFIED_IDLE_SLO_AND_REFRESH.it.md`, `docs/RC_GATE_MATRIX.json`.

---

# Quorivio 0.1.0-dev — Ciclo RC 57: invio WebSocket condiviso (31 ottobre 2026)

**Ultimo commit confermato:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; **cicli 49–57 cumulativi e non ancora committati**. CI standard `41120048115` ed estesa `41123318359` verdi solo per la baseline precedente. **RC certificata: 81,25% (53 gate: 36 accettati, 17 parziali)**; nessun credito non verificato.

**Sviluppo funzionale:** uno snapshot per 500 partecipanti e un presentatore richiede ora due sole serializzazioni JSON condivise, con separazione lato server dei dati, gestione individuale di socket lenti e guasti di trasporto e primo snapshot nella stessa coda ordinata delle notifiche. Vedere `docs/RC57_LIVE_FANOUT.it.md`. Test unitari e contrattuali locali disponibili, ma restano da completare collaudi GitHub, PostgreSQL e carico reale multi-replica. `publish_image=false`, `rc_strict=false`. Nessun commit/push/tag/pubblicazione dell'assistente.

---

# Quorivio 0.1.0-dev — Ciclo RC 56: snapshot autorevoli nelle sessioni inattive (30 ottobre 2026)

**Ultimo commit confermato:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; **cicli 49–56 cumulativi non ancora committati**. Ultime CI verdi: standard `41120048115` ed estesa `41123318359`, che NON validano i cicli 49–56. **RC certificata: 81,25% (53 gate, 36 accettati / 17 parziali)**, credito nuovo locale **0**. `publish_image=false`, `rc_strict=false`.

**Difetto funzionale risolto:** il watchdog del ciclo 55 si aspettava snapshot periodici, ma il server aggiornava soltanto la presenza in PostgreSQL. Una sessione senza nuove risposte non produceva snapshot dopo quello iniziale: trascorsi 65 secondi il browser avrebbe riconnesso inutilmente i client, causando possibili tempeste di riconnessione con 500 partecipanti.

**Correzione ciclo 56:** invio di snapshot autorevoli ogni 20 secondi **per sessione attiva**, sfruttando la coda già coalescente `broadcastLocal()`. Una sola lettura/fanout per sessione, non una lettura per partecipante; nessuna notifica cross-replica duplicata. Se la lettura dal database fallisce non viene simulato un heartbeat valido: il watchdog del client rileva l'interruzione. Nessuna modifica al protocollo lato browser né ai dati memorizzati. Test deterministici di 10 minuti inattivi, 500 iscritti, database non disponibile, isolamento delle sessioni e sovrapposizioni.

**Nuova prova reale opzionale:** `live_idle_test=true` esegue 70 secondi di snapshot inattivi con due repliche PostgreSQL temporanee dopo il commit; vedere `docs/RC56_IDLE_SNAPSHOT_ACCEPTANCE.it.md`.

**Limiti:** i test locali non certificano una vera infrastruttura a due worker, carico SLO 500 utenti, TLS pubblico, RWX CSI/NFS o conformità indipendente. Dopo il commit eseguire CI standard ed estesa con i collaudi HTTPS e SLO opzionali; nessuna promozione RC prima dell'esito.

---

# Quorivio 0.1.0-dev — Ciclo RC 55: freschezza snapshot WebSocket e visibilità dei dati obsoleti (30 ottobre 2026)

**Ultime CI GitHub verificate:** standard `41120048115`, estesa `41123318359` (baseline `64aa3437`); non certificano le modifiche non committate.

**Opzioni CI richieste:** `rc_strict=false`, `publish_image=false` finché restano gate esterni aperti.

**Ultima baseline committata:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; **cicli 49–55 cumulativi non ancora committati**. **RC certificata invariata: 81,25% (53 gate: 36 accettati, 17 parziali)**. Non attribuire punti ai test locali prima dei collaudi su GitHub e senza confondere l'implementazione con una certificazione di disponibilità.

**Sviluppo reale:** `apps/web/src/live-connection.ts` sorveglia la freschezza degli snapshot dopo l'apertura di ogni WebSocket (65 secondi predefiniti rispetto a snapshot server periodici ~20 secondi). Solo gli snapshot validi e della sessione giusta riarmano il watchdog; uno stream bloccato viene dismesso in modo atomico, il vecchio socket non può più aggiornare dati o stato, e un nuovo tentativo usa il backoff esistente. Anche `onerror` senza `onclose` forza un recupero delimitato. Timer annullati su offline, dispose, close e revoca.

**Interfaccia:** avviso accessibile per statistiche presenter e schermo pubblico con connessione persa o revocata; il contenuto precedente rimane visibile ma è dichiarato potenzialmente obsoleto. Nessuna modifica alle risposte o ai dati di sessione nel database.

**Evidenze locali:** 505 test backend e 99 frontend Node PASS; 1.347 Python PASS (1 saltato) in 8 gruppi, oltre al controllo TypeScript del transport; nuovi test Node deterministici su timeout senza snapshot, reset su snapshot validi, rifiuto di quelli di altra sessione, perdita rete, errori senza evento di close e annullamento timer; contratti Python e inventario. **Non dimostrato:** vera perdita di rete su due nodi indipendenti, 500 client sostenuti, tempi di recovery rappresentativi; CI standard ed estesa da eseguire dopo il commit. Gli input `kubernetes_tls_test` e `capacity_slo_test` dei cicli 50–52 restano opzionali e non ancora eseguiti sul nuovo cumulativo.

---

# Quorivio 0.1.0-dev — Ciclo RC 54: recupero live WebSocket (30 ottobre 2026)

**Baseline committata:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`. **Cumulativo ancora non committato:** cicli 49–54. **RC certificata 81,25%**, 53 gate (36 accettati, 17 parziali). Nessun punto aggiunto senza collaudo indipendente.

**Sviluppo funzionale:** il nuovo client live WebSocket evita che messaggi/errori di connessioni sostituite sovrascrivano lo stato corrente. Alla perdita di rete cancella timer e chiude il vecchio socket; al ritorno online apre una sola connessione. Gestisce handshake che non terminano entro 15 secondi, retry esponenziali con jitter individuale e limite di 30 secondi, terminazione per codici 4003/1008 senza reconnessione non autorizzata, messaggio dedicato per accesso revocato e callback React aggiornati. Presenter e partecipanti usano la stessa logica. Il protocollo server/PostgreSQL rimane invariato.

**Evidenze e limiti:** nove test deterministici e controllo TypeScript stretto; le prove di carico/resilienza su browser reale e la CI GitHub rimangono necessarie. Test infrastrutturali HTTPS, SLO 500 partecipanti e CSP dei cicli 49–53 non ancora confermati su GitHub. Nessuna pubblicazione/commit dell'assistente.

---

# Quorivio 0.1.0-dev — RC 53 — Content Security Policy di produzione e permessi del browser (30 ottobre 2026)

**Baseline:** cumulativo ciclo 52; nessun nuovo commit dall'hash `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`. Il package conserva i cicli 49–53. **RC certificata sempre all'81,25%**: mancano il collaudo del runtime GitHub e la revisione indipendente di sicurezza.

## Sviluppi applicativi

`apps/api/src/security-headers.ts` introduce una CSP **effettivamente applicata in produzione** quando `NODE_ENV=production`: nega script inline ed eval, blocca oggetti eseguibili, vincola WebSocket all'origine pubblica configurata e preserva gli iframe dello stesso dominio per anteprima e presentazione. Immagini/media mantengono il supporto a upload, QR/data image, sfondi HTTPS opzionali, PDF e blob. Il CSS inline necessario a posizionamento, animazioni e personalizzazioni dei widget resta autorizzato, senza estendere l'esecuzione JavaScript. `Permissions-Policy` nega camera, microfono, posizione, pagamenti, USB e browsing-topics; lo schermo intero del presentatore rimane utilizzabile. La modalità di sviluppo Vite non applica la CSP di produzione.

## Verifiche e limiti

Cinque nuovi test Node verificano i vincoli CSP, quattro contratti Python verificano l'integrazione API e i test di runtime. I collaudi OCI AMD64/ARM64 e Podman rootless ora rifiutano un container che non restituisce i due header HTTP. **Il nuovo codice non è ancora stato provato in GitHub né su browser con questo aggiornamento**, e non sostituisce penetration test o certificazioni AGID/GDPR.

L'81,25% non aumenta: i collaudi HTTPS KIND, SLO globale 500 utenti, RWX esterno e approvazioni indipendenti D4/D6 sono ancora aperti. Eseguire CI standard e successivamente estesa con runtime OCI/Podman e browser, `publish_image=false`, `rc_strict=false`.

---

# Quorivio 0.1.0-dev — Ciclo 52: SLO globali su 500 partecipanti (30 ottobre 2026)

**Ultima CI standard/estesa verificata:** `41120048115` / `41123318359` (verde sulla baseline del ciclo 48). **Baseline confermata:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (ciclo 48). I cicli **49–52 non sono ancora stati committati**, quindi questo package rimane cumulativo. **RC certificata: 81,25%, 53 gate (36 accettati e 17 parziali)**. Nessun aumento ufficiale prima dei nuovi collaudi CI e della riconciliazione. Il punteggio `rc_strict` rimane bloccato.

**Macroarea B4:** aggiunto `capacity_slo_test` come prova manuale opt-in contro PostgreSQL *temporaneo* della CI. Esegue 500 connessioni indipendenti con ramp-up di 40 secondi e mantenimento di 90 secondi, osservatore WebSocket unico e latenza di ingresso/prima risposta per ogni client. I campioni sono **soltanto numerici, senza pseudonimi, risposte o identificatori**. Il verificatore rifiuta campioni mancanti o non finiti, percentili di shard contraddittori, hold breve, observer mancante, numero incompleto e errori di connessione; calcola i p95 sull'unione di **tutti i campioni individuali** (non sulla media dei p95 dei singoli shard), con soglie opt-in di 5000 ms login/ingresso e 8000 ms primo snapshot. Il vecchio `capacity_test` continua a funzionare invariato.

**Verifiche locali:** contratti Python, esempi multisorgente e suite Node. Il vero test 500 utenti/90 secondi nel job GitHub è ANCORA PENDENTE. Non dimostra hardware fisico, cali di rete reali, server SLO esterno né verifica dei dispositivi. Aggiornati inventory e procedura `docs/RC52_SUSTAINED_500_SLO.it.md`.

**Dopo il commit**: CI standard, poi CI estesa con `capacity_slo_test=true`, `kubernetes_tls_test=true`, `publish_image=false`, `rc_strict=false`. Promuovere B4 solo dopo risultati GitHub e senza doppio conteggio di B4-LOAD già accettato. Nessun commit, push, tag o pubblicazione eseguito dall'assistente.

---

# Quorivio 0.1.0-dev — handoff ciclo 51

**Baseline ultimo commit confermato:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; i cicli **49, 50 e 51 sono ancora da committare** e sono inclusi nel cumulativo. RC certificata **81,25%**, 53 gate: 36 accettati, 17 parziali. CI standard ed estesa verdi per la baseline del ciclo 48. Non effettuare commit/push/tag/release automaticamente.

**Sviluppi ciclo 51:** corretta la chiamata HTTPS che passava un argomento posizionale non ammesso; aggiunti test AST ed esecuzione simulata dell'intero percorso KIND per NGINX e HAProxy, incluso host errato, certificato non attendibile, due pod, sostituzione e recovery. Il client HTTPS Node reale continua a essere esercitato con server TLS temporaneo. La verifica negativa non deve promuovere errori di nome TLS o certificato scaduto a prova della catena non attendibile. Nessun test KIND TLS vero completato nella nuova CI, quindi nessun nuovo credito ufficiale.

**Procedura:** commit manuale cumulativo 49–51, CI standard, poi estesa con `kubernetes_tls_test=true`, `publish_image=false` e `rc_strict=false`. Entrambi i job HTTPS verdi possono autorizzare una successiva riconciliazione ristretta del B4 (obiettivo condizionale **81,50%**); non dichiarare produzione HA/TLS pubblici o RWX CSI/NFS su hardware separato. Dettagli in `docs/RC51_HTTPS_ACCEPTANCE.it.md`.

---

# Quorivio 0.1.0-dev — RC ciclo 50 — collaudo HTTPS reale e certificati temporanei (30 ottobre 2026)

**Baseline utente confermata:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (ciclo 48). **Ciclo 49 non ancora committato**, incluso nel presente cumulativo. RC ufficiale **81,25%**, 53 gate (36 accettati, 17 parziali): nessun incremento senza CI. Il nuovo collaudo opt-in con `kubernetes_tls_test=true` prova **NGINX e HAProxy Technologies** in KIND a 2 worker con certificato TLS autofirmato temporaneo, validazione del trust/SNI nel client Node reale, host virtuale errato, rifiuto del certificato non fidato e recupero dopo sostituzione pod. Il certificato privato non viene stampato; contesto Kubernetes usa esclusivamente il cluster effimero e nessun cluster esterno. Le prove reali su 2 host fisici, TLS pubblico, CSI/NFS RWX, continuità sotto rete degradata e audit indipendenti restano aperte.

**Evidenza locale:** test Python mirati compreso HTTPS Node con vero server TLS locale; CI GitHub/KIND della nuova opzione ancora da eseguire. Non pubblicare immagini, né avviare RC strict, senza accettazione completa. La meta potenziale è uno scorporo circoscritto di parte del gate B4 dopo successo dei due job Kubernetes HTTPS, senza duplicare il precedente HTTP.

---

# Quorivio 0.1.0-dev — RC ciclo 49 — HAProxy verificato e verifica RWX tra nodi (30 ottobre 2026)

**Baseline dell'ultimo commit confermato:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (ciclo 48). Run standard `41120048115` e run estesa `41123318359` entrambe verdi; gli 11 job della estesa hanno superato i controlli. Il job HAProxy Technologies `124297991439` accredita il nuovo sottogate autonomo B4. **RC 81,25% — 53 gate: 36 accettati, 17 parziali**. I collaudi NGINX, OCI, Firefox/WebKit e ClamAV già conteggiati non vengono ripagati. **RC strict non pronta** (`rc_strict=false`).

**Sviluppo ciclo 49 non ancora confermato da una nuova CI:** verificatore Kubernetes RWX tra due pod su nodi distinti, con context `kubectl` esplicito, PVC Bound RWX di tipo CSI/NFS/CephFS, mount valido, verifica incrociata con `--confirm-write` esplicito e pulizia di file temporanei. Default solo lettura; nessun accesso ai Secret o ad asset preesistenti. Test negativi e di cleanup aggiunti. Nessuna esecuzione su cluster reale dell'utente e nessun ulteriore credito RC. Manuale in `docs/RC49_HAPROXY_CROSS_NODE_RWX.it.md`.

**Residui:** storage CSI/NFS RWX su host fisici indipendenti, guasti di rete/storage, TLS pubblico, carico 500 utenti sostenuto e SLO, dispositivi/lettori di schermo reali e verifiche GDPR/AGID/sicurezza indipendenti. Dopo commit manuale, CI standard ed estesa; niente commit/push/tag assistente.

---

# Quorivio 0.1.0-dev — RC ciclo 48 — ripristino storico SHA-256 (30 ottobre 2026)

**Baseline del commit confermato:** `40e42964063e93aed6cc4a4f7a5fc9e5feebaa15` (cicli fino al 47). **Punteggio RC ufficiale invariato: 80,75%**, 52 gate (35 accettati, 17 parziali). Nuove modifiche del ciclo 48 non ancora verificate su GitHub.

**Diagnosi di due CI fallite:** le run standard `41117244123` (job `124274549345`) ed estesa `41117884354` (job `124276729019`) sono fallite nello stesso step dell'inventario SHA-256: il verificatore storico del ciclo 42 trova assente `RC_CYCLE42_PACKAGE_INVENTORY_20261030.json`. Il successivo verificatore del ciclo 43 avrebbe fallito a sua volta per lo stesso difetto. Tutti i controlli storici precedenti al 42 nel log passano. Non attribuire il fallimento a PostgreSQL, Chromium, ClamAV o Vite: l'errore conclusivo è `FileNotFoundError` del manifest.

**Correzione:** ripristinati *senza ricostruzione* i manifest 42 e 43, recuperando i byte originali dagli ZIP cumulativi di quei cicli; SHA-256 immutabili `dcb77af5 59e66a61 d950ce37 77aabcc4 2a4de61f 5db1af18 1d9b9c44 07a78950` e `109cfa85 3e83d2e8 32fbf975 495ff6f6 97a36d2e f7e89d71 6579a6ef 4b4030a3`. La CI esegue ora un controllo preventivo di tutti i file referenziati dai verificatori d'inventario e dei file tracciati da Git (quando disponibile) prima della suite Python e prima del gate checksum. Il ciclo 47 resta un'evidenza storica e il 48 diventa l'inventario corrente. Aggiunti test che assicurano l'assenza di regressioni future.

**Limiti:** compilazione applicativa e test infrastrutturali precedentemente superati non sono ripetuti come prove del nuovo codice, e la nuova CI deve verificare l'intero workflow dopo il commit. Niente commit/push/tag/publish dall'assistente. Eseguire dapprima la CI standard con `publish_image=false`, `rc_strict=false`; la CI estesa dopo che la standard è verde.

---

# Quorivio 0.1.0-dev — RC ciclo 47 — hotfix collaudo editor PostgreSQL e portal (30 ottobre 2026)

**Baseline committata:** `5163e5a5b4685348810ef24067538967a1bbb536`. I cicli **46 e 47 non sono committati** e devono essere distribuiti insieme. **RC formale: 80,75%**, 35 gate accettati, 17 parziali, `rc_strict=false`; nessun punto aggiunto.

**CI estesa precedente:** run `41115332748`, job `124267958170`, eseguita sul commit precedente al ciclo 46. Supera PostgreSQL background library e ownership collaboratori, test editor CAS, test browser partecipanti e test contestuale isolato. Fallisce solo la prova editor PostgreSQL quando `tools/ci_browser_editor_postgres.py` cerca il menu `Azioni widget text` sotto `.widget-canvas-item`: la vera applicazione utilizza React `createPortal` verso `document.body`.

**Modifica:** il test apre il menu con clic destro sul widget ma lo localizza nell'intero documento, impone una sola istanza, ne verifica la visibilità, la modifica del titolo, la chiusura e il ripristino del `contenteditable=false`. Lasciati immutati i controlli PostgreSQL reali per autosave, revisione, merge, conflitto dello stesso campo ed export. Aggiunti contratti Python contro future regressioni del selettore. Il codice applicativo non viene cambiato.

**Non ancora certificato:** il test PostgreSQL/Chromium end-to-end con il nuovo selettore deve passare in una nuova CI. La precedente run non verifica gli hotfix non committati 46–47. Resta da superare il gate Container, saltato per dipendenza. Nessun commit, push, tag o pubblicazione dell'assistente.

---

# Quorivio 0.1.0-dev — RC ciclo 46 — ripristino gate qualità Python (30 ottobre 2026)

**Completamento RC invariato: 80,75% (52 gate: 35 accettati, 17 parziali).** Ultimo commit osservato su GitHub: `5163e5a5b4685348810ef24067538967a1bbb536` (ciclo 45). Il workflow `41114355433`, job qualità `124264578469`, ha eseguito 1.278 test Python, con **due regressioni obsolete** in `test_canvas_context_menu.py` e `test_rc_cycle35_verified_bootstrap.py`. Gli altri 1.276 test hanno superato il gate, ma il job è fallito e non ha ancora raggiunto le prove Chromium sul frontend compilato, né il container gate.

**Hotfix non ancora verificato nella CI:** il test del menu contestuale controlla ora le proprietà effettivamente passate a `WidgetCanvas` (`assets`, libreria sfondi collaboratori, sessione, callback upload, busy) anche quando sono su più righe; conferma inoltre che il selettore sfondi conserva i callback di libreria. Il test di documentazione utilizza la ricevuta immutabile del ciclo 35 per verificare il commit storico, mentre i documenti correnti devono dichiarare la run recente, la baseline, le limitazioni e `rc_strict=false`. Il vecchio riferimento storico non è più richiesto nei primi 4.000 caratteri dell'handoff.

**Limiti e rischio residuo:** l'hotfix riguarda test e documentazione, non modifica il comportamento dell'app. La suite Python completa, la CI standard, la prova Chromium reale sul build di produzione e l'immagine container sul nuovo pacchetto restano da confermare dopo il commit. I 17 gate parziali, incluso storage RWX reale, HAProxy, TLS, dispositivi/accessibilità e verifiche GDPR/AGID indipendenti, rimangono aperti. **Non pubblicare immagini; `publish_image=false`, `rc_strict=false`.** Nessun commit, push, tag o pubblicazione eseguiti dall'assistente.

---

# Quorivio 0.1.0-dev — RC ciclo 45 — collaudo Chromium sugli asset compilati (30 ottobre 2026)

**RC verificata invariata: 80,75% (52 gate: 35 accettati e 17 parziali).** La run GitHub `41110214420`, job `124250386166`, sul commit `383c273deb53d368d6b8a1d57ab5c623591bcc7a` ha compilato correttamente TypeScript/Vite e superato 500 test Node backend, 84 frontend e il test ClamAV reale, ma il collaudo Chromium completo ha fallito con `root_children=0, page_error_count=0`. Il test non ha ottenuto alcun DOM React nell'app, prima della navigazione autenticata. Il container gate è stato saltato a causa del quality gate fallito.

**Intervento nuovo (non ancora certificato da CI):** per evitare la dipendenza del collaudo editor dall'ottimizzatore di dipendenze e dall'HMR del server Vite in modalità sviluppo, il workflow avvia `vite preview` dal `dist` già prodotto da `npm run build`. La nuova prova `tools/ci_built_frontend_asset_probe.py` verifica che la pagina provenga dal build, che il JS fingerprinted sia scaricato con HTTP 200 e che React monti `#root .app` prima dei test editor. I log non espongono URL con token, cookie, payload o stacktrace contenenti dati. Il test editor mantiene la prova di ricaricamento per l'autosave ma non ripete più il bootstrap per tentare di compensare l'optimizer.

**Verifiche e limiti:** contratti Python, sintassi Python/YAML e suite Node locali eseguiti; il browser di questo ambiente blocca esplicitamente il loopback HTTP (`ERR_BLOCKED_BY_ADMINISTRATOR`) e non permette una verifica end-to-end dell'avvio React. La causa tecnica esatta del mancato montaggio nella run precedente non è stata dimostrata; l'intervento rimuove una sorgente plausibile di instabilità e rende la successiva run molto più diagnostica. La nuova CI deve passare prima di definire risolto il guasto. Non vi sono punti RC nuovi né commit/push/tag/publish automatici.

**Dopo il commit:** workflow standard con `browser_test=true`, `publish_image=false`, `rc_strict=false`; verificare `PASS Chromium built frontend` e `PASS Chromium editor mock fidelity`. Solo dopo eseguire eventuali workflow estesi.

---

# Quorivio 0.1.0-dev — RC ciclo 44 — avvio Chromium e informativa cookie (30 ottobre 2026)

**Ultimo commit confermato:** `1857ebb22560d0ddcc1fec439dfe865eb0183e98` (ciclo 43). La CI standard `41103165554` ha superato 500 test Node backend, 84 frontend, build TypeScript/Vite e la prova separata ClamAV reale. Il quality gate si è fermato in `tools/ci_browser_editor.py` attendendo «Apri sessione». Lo screenshot allegato è interamente bianco: quando si è verificato il timeout il frontend non era visibilmente montato. La vera causa sottostante (JavaScript o caricamento freddo Vite) non era riportata nei log e non può essere dichiarata identificata.

**Modifiche ciclo 44, non ancora verificate nella CI:** lo smoke Chromium attende il montaggio di React in `#root .app`, con un solo nuovo caricamento della pagina per gestire il caso dell'optimizer Vite in avvio. Se l'app non compare, fallisce esplicitamente con diagnostica minimale. I test desktop, mobile e PostgreSQL ora chiudono l'informativa modale cookie *prima* di cercare i comandi nella pagina. Aggiunti test dei contratti e prova Chromium isolata dell'intercettazione dei clic da parte del dialogo, senza bypass del consenso o clic forzati. La suite editor reale deve ancora essere confermata nella prossima CI.

**RC ufficiale invariata: 80,75%** (52 gate, 35 accettati, 17 parziali). `rc_strict=false`, `publish_image=false`. Nessun commit/push/tag/pubblicazione da parte dell'assistente.

---

# Quorivio 0.1.0-dev — RC ciclo 43 — hotfix TypeScript della CI standard (30 ottobre 2026)

**Nuova baseline committata dall'utente:** `55b5ab70dcc3ee772b47c5acd498b47d58874441` (ciclo 42). La run standard `41099464679` fallisce soltanto nel job `Production quality gate`, passo `Compile frontend and backend`: TS2339 in `main.tsx` per i campi `allowAnswerChange` e `showEmail` mancanti nel tipo locale dello storico widget. Prima della compilazione i test Node backend (500/500) e frontend (84/84) erano verdi; il container gate è stato saltato di conseguenza, non è un secondo errore.

**Hotfix non committato:** il tipo del widget nel canvas eredita i due campi dal `PageDesign` validato dal server usando `Pick<>`, evitando che la tipizzazione dell'editor diverga dal backend. Aggiunti contratto TypeScript e regressioni Python. Catalogo storico del ciclo 42 immutato; catalogo 43 corrente verificato in CI. Nessuna modifica alle regole di business su risposte o visibilità e-mail.

**Limiti:** test Python mirati verdi; build TypeScript/Vite non rieseguita sul nuovo codice perché l'installazione npm locale non è disponibile (cache offline incompleta ed errore dell'installer). Il gate dovrà essere confermato su GitHub dopo il prossimo commit. Completamento RC ufficiale **80,75%** invariato (52 gate: 35 accettati, 17 parziali); `rc_strict=false` e `publish_image=false`.

**Azione successiva:** commit/push del cumulativo ciclo 43 e CI standard. Nessun commit, push, tag o rilascio effettuato dall'assistente.

---

# Quorivio 0.1.0-dev — ciclo 42: timer personalizzabili e precedenza riempimenti — 30 ottobre 2026

**RC formale: 80,75%** (52 gate: 35 accettati, 17 parziali), invariata; i cicli 34–42 sono cumulativi e non committati rispetto al commit confermato `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`.

**Modifiche:** aggiunta l'opzione di quadrante per widget Timer e Quiz a tempo (`hourglass`, `dial`, `digital`), persistita nel modello e rifiutata dal validatore se il valore non è nell'allowlist. Le tre varianti usano il medesimo conto alla rovescia in editor, anteprima, presentatore e partecipante; il quadrante digitale ha una barra di avanzamento dedicata. Corretta la precedenza degli stili per `fillNone`, `fillOpacity` e riempimento solido: ora il tema decorativo non appare dietro un riempimento esplicitamente trasparente, incluso `fillOpacity=0`. Tutti gli effetti rispettano la preferenza di sistema per la riduzione del movimento.

**Test:** suite backend Node 500/500; frontend Node 84/84; contratti su persistenza, validazione, sicurezza dei valori, colori e viste. Build TypeScript/Vite e collaudo browser completo ancora da eseguire sul codice nuovo. Catalogo storico ciclo 41 intatto; inventario corrente ciclo 42 e controllo CI da verificare prima del commit. Nessun commit, tag, push o publish effettuato dall'assistente.

---

# Quorivio 0.1.0-dev — RC ciclo 41 — 30 ottobre 2026 — temi artistici per widget

**Punteggio RC formale invariato: 80,75% (52 gate: 35 accettati, 17 parziali).** Ultimo commit confermato: `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`; cicli 34–41 cumulativi e non ancora committati. Implementati temi per widget persistiti e validati dal server (`studio`, `glass`, `playful`, `minimal`) ed effetti facoltativi (`none`, `float`, `glow`, `tilt`). La resa è comune a editor, prova, presentatore e partecipante; i riempimenti manuali, le immagini e le trasparenze prevalgono sul tema. Anteprima artistica statica del timer nel canvas; conto alla rovescia reale nelle proiezioni. Il CSS distingue i tipi di widget e rispetta la riduzione del movimento. Inventario storico del ciclo 39 conservato e nuovo manifest per il ciclo 41. Verifiche: 500 test API Node e 81 frontend Node verdi; 4 nuovi test Node e 4 test contrattuali Python superati. Build di produzione completa, Chromium e collaudo manuale ancora da eseguire. Vedi `docs/RC_WIDGET_ART_THEMES_CYCLE41.it.md`. Nessun commit/push/release/pubblicazione dell'assistente.

---

# Quorivio 0.1.0-dev — RC ciclo 40 — stile artistico dei widget (30 ottobre 2026)

**Completamento formale invariato: 80,75%** (52 gate: 35 accettati e 17 parziali). Il codice di questo ciclo non è ancora verificato da una nuova CI GitHub né da un collaudo browser reale dell’utente. Ultimo commit confermato: `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`; i cicli 34–40 restano cumulativi e non committati.

**Implementato:** i widget del canvas, della prova interattiva, della pagina del presentatore e della pagina partecipante usano ora una resa visiva più ricca e coerente per categoria: superfici tipo card con profondità, riflessi, accenti cromatici e decorazioni semantiche per timer, domande, quiz, reazioni, risultati, profilo, QR, media, testi, note, conteggio partecipanti e domande del pubblico. Il timer è stato ridisegnato con anello di avanzamento, clessidra e cifre ad alto contrasto, con stato urgente nelle fasi finali. Le nuvole risultati e le barre statistiche sono state rese più leggibili e accattivanti. Le nuove skin sono applicate anche al canvas editor, così il presentatore vede già l’impatto visivo durante la composizione.

**Verifiche locali:** controllata l’integrazione dei nuovi attributi `data-widget-kind` nei punti di rendering condivisi e l’assenza di regressioni evidenti nella serializzazione delle pagine. Build TypeScript/Vite, test browser reali, suite Node complete e conferma utente restano da eseguire dopo il commit. Nessun nuovo punto RC assegnato.

**Dopo il commit:** CI standard con test browser (`browser_test=true`, preferibilmente anche `cross_browser_test=true`) e collaudo manuale di timer, widget domanda/quiz, risultati, profilo e QR in editor, anteprima presentatore, anteprima partecipante e visualizzazione live.

---

# Quorivio 0.1.0-dev — RC ciclo 38 — Interazioni partecipante e statistiche presentatore (30 ottobre 2026)

**RC verificata: 80,75%** (52 gate: 35 accettati, 17 parziali). Nessuna attribuzione di punti a codice non verificato su GitHub. Baseline di commit confermata `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`; cicli 34–38 cumulativi non ancora committati.

**Implementato:** nelle anteprime, il presentatore non vede più alcuna spunta o risposta del singolo partecipante nella widget interattiva. Le risposte simulate confermate aggiornano la widget Risultati collegata, senza cambiare la domanda. Le reazioni sono sostituibili nel client di prova e nell'API reale PostgreSQL (voto singolo per partecipante/pagina); modifiche alle domande e ai quiz sono disabilitate per default, attivabili per ogni domanda, e nei quiz a tempo rimangono soggette alla scadenza. I controlli radio/checkbox sono alla sinistra del testo. Il profilo mostra nome e foto quando presenti; l'email si pubblica soltanto su scelta esplicita del presentatore, così da proteggere gli altri indirizzi. Il widget profilo usa una proiezione autenticata nel canvas dell'editor anche quando la pagina non è stata ancora pubblicata.

**Prove locali:** 497 test Node backend e 77 frontend verdi, 1.260 test Python previsti; TypeScript/TSX verificato sintatticamente ma non compilato integralmente per dipendenza npm non presente nella cache offline. PostgreSQL reale, Chromium e test manuali delle anteprime saranno verificati nella successiva CI; HAProxy reale è ancora da provare. Limite: più widget reazioni sulla stessa pagina condividono attualmente una scelta per partecipante/pagina; la separazione per widget rimane una estensione successiva. Niente commit, push, tag o pubblicazioni da parte dell'assistente.

**CI dopo il commit:** standard + `browser_test=true`, `cross_browser_test=true`, eventualmente `kubernetes_haproxy_test=true`, con `publish_image=false` e `rc_strict=false`. Dopo le verifiche automatiche è richiesto un collaudo manuale di due schermi affiancati e dell'aggiornamento dei grafici.

---

# Quorivio 0.1.0-dev — RC ciclo 37 — Correzioni editor e salvataggio (30 ottobre 2026)

**Completamento formale invariato: 80,75% (52 gate, 35 accettati e 17 parziali).** Il codice di questo ciclo non è ancora verificato in una nuova CI GitHub. Ultimo commit confermato `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (ciclo 33); i cicli 34–37 sono cumulativi e non committati. Nessun commit, push, tag o pubblicazione effettuati dall'assistente.

**Quattro problemi segnalati con screenshot:** (1) testi chiari su widget bianche: colore predefinito nero, senza sovrascrivere quello scelto dall'utente; (2) menu widget tagliati: portal nel `document.body` e posizionamento compatibile con mouse, touch e tastiera; (3) anteprime presentatore/partecipante/affiancate che possono bloccare l'editor: boundary React recuperabile con uscita esplicita, chiusura con Escape/sfondo e refresh rallentato; (4) sondaggio a scelta multipla: preparazione atomica delle prime due opzioni e validazione locale secondo il contratto effettivo del server prima del salvataggio automatico.

**Test locali:** cinque nuovi test Node passati, 180 contratti Python sull'editor e 20 test specifici sui portal superati, TSX senza errori sintattici. Lo script Chromium già presente ora controlla il colore nero e il menu esterno al canvas, ma non è stato eseguito localmente per mancanza delle dipendenze. Build TypeScript/Vite, browser reale, backend PostgreSQL e conferma dell'utente ancora da eseguire. Il punteggio RC resta invariato. I 17 gate parziali richiedono prove esterne e revisioni indipendenti.

**Dopo il commit:** quality gate e `browser_test=true`, possibilmente `cross_browser_test=true`, con `publish_image=false`, `rc_strict=false`. Ripetere i quattro casi in browser reale; HAProxy rimane da collaudare separatamente.

---

# Quorivio 0.1.0-dev — ciclo 36 — accettazione Ingress HAProxy su KIND multi-worker (30 ottobre 2026)

**Completamento RC ufficiale 80,75%: 35 gate accettati e 17 parziali su 52, invariato.** Ultimo commit confermato `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (ciclo 33); i cicli 34–36 sono cumulativi e **non committati**. I collaudi CI precedentemente superati (`41048187760`) non vengono contabilizzati una seconda volta.

**Nuovo sviluppo funzionale:** lo smoke KIND su due worker supporta ora anche `--controller haproxytech`, mantenendo NGINX come default. Il controller ufficiale HAProxy Technologies è installato con Helm chart versionato `1.54.3`, Service ClusterIP privato e IngressClass `haproxy`. La prova opt-in usa le configurazioni HAProxy generate dal wizard e verifica PostgreSQL 18, repliche separate sui worker, storage condiviso esclusivamente per test, instradamento HTTP sul vero host, rifiuto di host non corrispondenti, sostituzione del pod e ripristino della disponibilità. Nuovo input `kubernetes_haproxy_test=true`, nessuna pubblicazione e diagnostica limitata agli stati delle risorse Kubernetes.

**Verifiche e limiti:** sintassi Python/YAML e 38 test mirati superati; la suite Python completa è inconcludente per timeout e limiti di import dell’ambiente locale; il controller HAProxy reale **non è stato eseguito localmente** e richiede una nuova CI GitHub dopo il commit. KIND usa un singolo host fisico e un bind mount: non certifica NFS/CSI RWX, server fisici distinti, TLS pubblico, il controller HAProxy Community, carichi prolungati o gli audit GDPR/AGID e di sicurezza indipendenti. Non attivare `rc_strict` o la pubblicazione di immagini.

**CI consigliata dopo il commit:** `kubernetes_haproxy_test=true`, eventualmente anche `kubernetes_multinode_test=true` e `clamav_runtime_test=true`, con `publish_image=false`, `rc_strict=false`.

---

# Quorivio 0.1.0-dev — ciclo 35 — 30 ottobre 2026 — RC 80,75% (+0,50 punti)

**Baseline committata confermata:** `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (ciclo 33). I cicli 34–35 restano non committati. Nella CI GitHub `41048187760`, job qualità `124037870206`, sono state verificate con PostgreSQL 18 due API avviate simultaneamente (un solo amministratore iniziale) e lo shutdown controllato con readiness `503`, WebSocket `1012` e seconda replica sana.

**Punteggio RC ufficiale: 80,25 → 80,75%**. Il gate B1 (peso 2) è stato suddiviso in residuo B1 parziale di peso 1, `B1-BOOTSTRAP-PG18` di peso 0,5 accettato e `B1-GRACEFUL-DRAIN` di peso 0,5 accettato. 52 gate complessivi, 35 accettati, 17 parziali; peso totale 100. Non vengono conteggiati i nuovi interventi locali.

**Nuovo sviluppo ancora senza certificazione CI:** in caso di errore prima di acquisire l'advisory lock PostgreSQL, la connessione viene distrutta anziché restituita al pool con `lock_timeout` modificato o stato incerto; copertura con regressioni Node per timeout, errore di setup, reset fallito e rilascio non confermato.

**Test locali ciclo 35:** 18 gruppi Python separati, 1.251 test eseguiti, nessun gruppo fallito; 8 test Node mirati passati. Suite Node complete e build TypeScript/Vite non eseguite localmente per dipendenze npm non presenti. Verifica dei checksum sorgenti e ZIP obbligatoria prima della consegna.

**Ancora aperti:** CSI/NFS RWX reale su più macchine, HAProxy, TLS di produzione, ARM64 fisico, collaudi di carico persistenti e guasti, dispositivi/accessibilità, valutazioni GDPR/AGID e sicurezza indipendenti. RC stretta NON pronta. Nessun commit, push, tag o publish dell'assistente.

---

# Quorivio 0.1.0-dev — RC ciclo 32 — 30 ottobre 2026 — antivirus produzione e Kubernetes

**RC ufficiale: 79,25% (48 gate: 31 accettati, 17 parziali)**. Ultimo commit confermato dall'utente: `016beea25d5e2d2fab21b0730aa15baf0b573e12` (ciclo 28); cicli 29–32 cumulativi e ancora senza commit. Nessun nuovo risultato GitHub indipendente su queste modifiche: punteggio non aumentato artificiosamente.

**Implementato:** scansione antivirus obbligatoria per ogni upload in produzione anche quando il flag manca o vale `false`; disattivazione possibile soltanto in sviluppo/test. Il client INSTREAM rifiuta chiusure anticipate, false risposte `OK` prima di ricevere tutti i byte, risposte eccessive e timeout complessivi, evitando rigetti di Promise non osservati. Il wizard Kubernetes genera scanner gestito privato (Deployment, Service ClusterIP, NetworkPolicy) e configura `QUORIVIO_AV_REQUIRED=true`; modalità esterna solo con host esplicito validato. Il passaggio a scanner esterno elimina i precedenti manifest gestiti. Helm: limite memoria ClamAV aumentato a 4 GiB. Documentazione IT/EN e regressioni aggiornate.

**Limiti:** i mock e i manifest non costituiscono una prova con ClamAV reale e firme aggiornate, né collaudo CSI RWX/failover, HAProxy/TLS o audit esterno. Il servizio antivirus gestito ha una replica: durante interruzioni gli upload falliscono in sicurezza. In produzione occorre tarare `StreamMaxLength` e verificare risorse e Pod Security Policy. La CI include ora anche `clamav_runtime_test=true` (opt-in) per provare file puliti e firma EICAR innocua con un ClamAV reale; non è stata ancora eseguita. Il collaudo KIND multiworker del ciclo 29 usa un host scanner esterno volutamente non configurato, poiché esercita NGINX e scheduling, non la scansione; non accreditarlo come prova antivirus.

**Prossimo passo:** dopo il commit dell’utente eseguire la Full CI e il test multiworker KIND opzionale. Per dare credito ai gate C4/D4 servono scanner ClamAV reale con firme e accettazione indipendente dello storage condiviso. `rc_strict=false`, `publish_image=false`. Nessun commit/push/tag/publicazione automatica.

---

# HANDOFF CORRENTE — ciclo 31 (2026-10-30)

**Baseline sorgente:** package del ciclo 30 più serializzazione PostgreSQL del ciclo 31. L'utente farà il commit dopo; ultimo commit confermato `016beea25d5e2d2fab21b0730aa15baf0b573e12` (ciclo 28).

**RC ufficiale:** 79,25% (48 gate: 31 accettati, 17 parziali). Non assegnare credito ai test locali. Alla prossima CI normale si esegue anche il nuovo avvio contemporaneo di due server su database PostgreSQL 18 vuoto. Test KIND multiworker/NGINX introdotto nel ciclo 29: abilitare `kubernetes_multinode_test=true`. Mantenere `publish_image=false`, `rc_strict=false`.

**Nuove modifiche:** lock PostgreSQL durante schema e bootstrap, transazione atomica di organizzazione/amministratore/tutorial, test simulati Node/Python, nuova prova PostgreSQL reale in CI, documentazione. Non ancora verificata su GitHub. Nessun commit/push/tag/pubblicazione dell'assistente.

---

# HANDOFF ATTUALE — ciclo 30 (2026-10-30)

**Sorgente**: cumulativo ciclo 29 con nuove modifiche ciclo 30. Ultimo commit dichiarato dall'utente `016beea25d5e2d2fab21b0730aa15baf0b573e12` (ciclo 28). Nessun commit/push/tag assistente.

**Regressione locale**: 1.218 test Python, uno saltato, nessun errore; 22 test specifici PASS. Build Node e runtime Kubernetes non verificati localmente.

**RC ufficiale**: 79,25%, 48 gate (31 accettati, 17 parziali). Niente punti da test locali. Il job KIND live 2-worker NGINX introdotto nel ciclo 29 deve essere eseguito con `kubernetes_multinode_test=true`, `publish_image=false`, `rc_strict=false` dopo il commit dell'utente. Il nuovo `k8s_operational_gate.py` del ciclo 30 interroga API cluster reali, ma non è stato eseguito in produzione. PostgreSQL interno è una replica singola, quindi non è database HA. Vedi `docs/K8S_OPERATIONAL_PREFLIGHT_RC30.it.md`.

**Prossimo**: CI multi-nodo e poi storage CSI RWX su veri nodi indipendenti, HAProxy, database HA, TLS, ClamAV, valutazioni indipendenti, senza inventare nuovi sottogate per alzare la percentuale.

---

# Handoff Quorivio 0.1.0-dev — RC ciclo 29 (30 ottobre 2026)

**Ultimo commit confermato dall'utente:** `016beea25d5e2d2fab21b0730aa15baf0b573e12` (ciclo 28). Il package ciclo 29 qui incluso NON è stato committato, taggato né pubblicato dall'assistente.

**Completamento RC misurato: 79,25%**, +0,25 punti sul 79,00% del ciclo 28, per la sola separazione del sottogate D3-OCI-ROOTLESS-RUNTIME già provato dalle CI remote `40980312270` (job OCI `123820527902`) e `40982728705` (job Podman `123827805762`). 48 gate: 31 accettati, 17 parziali; `rc_strict` deve restare disattivato.

**Interventi cumulativi non committati:** wizard genera correttamente PUBLIC_BASE_URL HTTP senza TLS; opzione `enforce_node_diversity` per distribuire due repliche su due worker, richiesta RWX; Helm rolling update e PodDisruptionBudget, vincolo RWX e `enforceNodeDiversity`; nuova workflow opt-in `kubernetes_multinode_test` con due worker KIND, PostgreSQL 18, Ingress NGINX e verifica del ripristino dopo eliminazione di un pod. Il volume fra i worker è un bind mount temporaneo del medesimo host runner (NON CSI/NFS di produzione). HAProxy, ARM64 fisico, TLS reale, storage CSI multi-macchina, verifiche GDPR/AGID indipendenti restano aperte.

**Test locali:** 1.193 unittest Python eseguiti (uno saltato), nessun fallimento; inventario SHA-256 sorgenti e ZIP verificato. Build Node/TS e prova KIND nuova non eseguite localmente per dipendenze/container runtime mancanti; sono da verificare nella CI del nuovo commit.

**Prossima CI proposta:** `workflow_dispatch` su main con `kubernetes_multinode_test=true`, `publish_image=false`, `rc_strict=false`; eventualmente aggiungere gli altri job opt-in. Non promuovere gate multi-nodo senza un job realmente verde. Non eseguire commit/push/tag/release automaticamente. Messaggio suggerito per il prossimo commit: `feat(k8s): add strict multi-node scheduling, live NGINX ingress CI and Helm HA guards`.

---

# Passaggio di consegne completamento software (2026-10-24)

Baseline: `quorivio-0.1.0-dev-accessibility-integration-cumulative.zip`.

## Verificato nel ciclo locale
- Controllo firma/MIME immagini PPTX e allineamento del rapporto di fedeltà all'importazione reale.
- 218 test Python e 116 Node.js superati.

## Sviluppi o verifiche ancora necessari prima della chiusura
- Gruppi, grafici, tabelle, SmartArt, temi complessi e mantenimento OOXML non supportato nei PPTX.
- Editor mobile completo e accessibilità visiva, partecipazione adattiva.
- Verifica indipendente dei metodi MFA e controllo generale di attivazione.
- Flusso pubblicazione/risposta/risultati widget; replica multipod e test 500 partecipanti.
- Importazione bundle `.quorivio` tra istanze con PostgreSQL e asset privati reali.
- Build pulita riproducibile, sicurezza, licenze, GDPR e manuali IT/EN.
- Collaudi Kubernetes dell'utente.

RC ponderata invariata 37,5%; versione `0.1.0-dev` invariata. Nessun intervento su GitHub o Kubernetes.
