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
