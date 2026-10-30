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
