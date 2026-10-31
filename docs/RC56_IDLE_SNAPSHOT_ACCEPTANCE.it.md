# Quorivio RC 56 — Accettazione delle sessioni live inattive

## Difetto rilevato e correzione

La presenza WebSocket veniva aggiornata ogni 20 secondi esclusivamente nel database. Senza cambiamenti di pagina o risposte, i browser non ricevevano ulteriori snapshot dopo l'apertura della connessione. Il watchdog client aggiunto nel ciclo 55 poteva quindi chiudere dopo 65 secondi **socket sani**: un grave problema per eventi con molti partecipanti.

`apps/api/src/live-periodic-refresh.ts` introduce una singola lettura e distribuzione per ogni sessione con client connessi, ogni 20 secondi. Riusa la coda di snapshot già coalescente, non genera nuove notifiche PostgreSQL e non effettua una lettura per ciascun partecipante. Lo snapshot trasportato è lo stesso, distinto per presentatore e partecipante, già usato in produzione. Se il database non risponde, non viene falsificato un successo e il client può ripristinare la connessione secondo il suo watchdog.

## Collaudo locale e CI

- `node --experimental-strip-types --test apps/api/test/live-periodic-*-cycle56.test.ts` copre 500 abbonati della stessa sessione, richieste concorrenti, errori database e ripristino; la prova integrata utilizza un orologio simulato per 10 minuti di inattività.
- `python3 -m unittest tools.tests.test_idle_live_postgres_cycle56 tools.tests.test_live_heartbeat_cycle56` controlla invarianti del test operativo e del collegamento con server e client.
- Dopo commit, avviare **workflow_dispatch** su un commit verificato con `live_idle_test=true`, `publish_image=false`, `rc_strict=false`. Il collaudo interroga soltanto API effimere su `localhost:8080` e `localhost:8081` con PostgreSQL temporaneo, apre una sessione provvisoria, collega il presentatore e un partecipante su repliche incrociate, attende 70 secondi senza mutazioni, verifica nuovi snapshot dopo 35 e 55 secondi, controlla privacy e pulizia finale.

Non utilizzare lo script su cluster di produzione: rifiuta URL non loopback. Un successo su GitHub permetterà di rivalutare il sottogate di *idle WebSocket freshness* senza confonderlo con HTTPS pubblico, 500 utenti sostenuti, recupero da guasto reale o storage CSI/RWX. **Finché il collaudo non è verde, punteggio RC certificato invariato: 81,25%.**
