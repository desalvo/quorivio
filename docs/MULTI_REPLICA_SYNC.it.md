# Sincronizzazione delle sessioni fra repliche (sperimentale)

## Sviluppato

- Il backend usa PostgreSQL `pg_notify('quorivio_session_update', sessionId)` dopo le mutazioni di sessione che già generavano un broadcast.
- Ogni istanza sottoscrive `LISTEN quorivio_session_update` su connessione dedicata, con riconnessione automatica dopo interruzioni; le notifiche ammettono solo UUID. Il contenuto non trasporta dati personali: le istanze ricaricano lo snapshot autorizzato da PostgreSQL.
- Il wizard Kubernetes permette 2–20 repliche **solo** se gli asset sono su un PVC `ReadWriteMany`; il chart Helm supporta PVC degli asset o claim esterno.
- Restano disponibili il broadcast locale immediato e il funzionamento con una sola replica.

## Limitazioni rilevanti

- `LISTEN/NOTIFY` è un meccanismo di notifiche *best effort*, non una coda persistente; in caso di disconnessione, il client dovrebbe riconnettersi per ottenere lo snapshot corrente.
- Gli stati temporanei di autenticazione OAuth/OIDC e i limiter per-IP rimangono in memoria di processo, quindi un deployment multi-replica dietro bilanciatore **non è ancora supportato integralmente** per quei flussi; usare replica singola o session affinity per i test, senza considerare quest'ultima un sostituto dello stato distribuito.
- Il PVC deve davvero supportare `ReadWriteMany` (NFS/CephFS o altro); non basta impostare il flag. I test sulle condizioni concorrenti e sull'accessibilità dei file dalle repliche restano da eseguire.
- Il chart Helm non è stato eseguito su un cluster reale; le modifiche sono state verificate tramite test statici.

## Verifica operativa richiesta

1. Avviare PostgreSQL e applicazione in ambiente di test, con due repliche e un volume RWX effettivo.
2. Collegare due browser tramite repliche distinte; inviare un voto da un client, verificare l'aggiornamento WebSocket sull'altra replica.
3. Forzare una disconnessione del listener PostgreSQL; verificare la riconnessione e l'aggiornamento degli snapshot.
4. Verificare lettura degli allegati indipendentemente dalla replica che ha gestito l'upload.
5. Prima dell'uso multi-replica in produzione completare anche lo stato OAuth condiviso e i controlli anti-abuso distribuiti.
