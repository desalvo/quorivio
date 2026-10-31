# Quorivio 0.1.0-dev — ciclo 57: distribuzione WebSocket efficiente e isolata

**Baseline dell'utente:** commit `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; cicli 49–57 non ancora committati, cumulativi. **RC certificata 81,25%** (53 gate: 36 accettati, 17 parziali); nessun incremento attribuito ai soli test locali.

## Problema

Ogni aggiornamento live serializzava con `JSON.stringify` lo stesso oggetto per ciascun WebSocket, pur usando soltanto due viste dei dati: una riservata a presentatori autorizzati, l'altra ridotta per partecipanti. Con 500 partecipanti e un presentatore erano possibili 501 serializzazioni per snapshot. Inoltre il primo snapshot della connessione veniva letto e inviato fuori dalla coda ordinata, con rischio di inversione rispetto agli aggiornamenti successivi.

## Correzione

Il nuovo modulo `apps/api/src/live-broadcast.ts` prepara un solo payload per dominio di autorizzazione **per sessione e per replica**; i buffer risultanti sono riutilizzati per tutti i socket della vista corrispondente. I destinatari non autorizzati a vedere i dati del presentatore ricevono soltanto `participantSnapshot`. La serializzazione pubblica deve riuscire prima che inizi qualunque invio, evitando la diffusione parziale della vista privata in presenza di errori. I socket lenti vengono chiusi singolarmente con il limite precedente di 2 MiB; eventuali errori di trasporto non interrompono la distribuzione agli altri destinatari.

Il primo snapshot passa ora per `broadcastLocal(sid)` e la stessa `createLiveSnapshotQueue` usata per le notifiche PostgreSQL e gli aggiornamenti periodici. Non viene più letto dal database e inviato indipendentemente fuori coda.

## Evidenze, limiti e criteri di accettazione

- Nuovi test unitari Node: 501 client con esattamente **2 serializzazioni**, controllo della separazione privata/pubblica, gruppi singoli, chiusura individuale del client lento, invio su altri socket dopo un errore di trasporto e rifiuto di trasmissione parziale se fallisce la proiezione pubblica.
- Test strutturali Python per assicurare che il primo snapshot rimanga nella coda, che le viste siano indipendenti e che il catalogo storico 56 resti disponibile.
- Soglia di pressione invariata (`MAX_LIVE_SOCKET_BUFFER_BYTES=2 MiB`). Nessuna nuova dipendenza npm o modifica del protocollo dei client.
- Verifica ancora necessaria su GitHub: build TypeScript/Vite, test PostgreSQL reali, `live_idle_test`, `capacity_slo_test` e prove su Kubernetes. I test unitari non dimostrano latenza p95 o riduzione di uso CPU in produzione; la matrice RC non viene avanzata senza collaudo.

**Dopo il commit dell'utente:** CI standard, poi estesa con `capacity_slo_test=true`, `live_idle_test=true`, `kubernetes_tls_test=true`, `publish_image=false`, `rc_strict=false`. Non eseguire commit/push/tag da parte dell'assistente.
