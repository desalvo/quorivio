# Affidabilità della distribuzione live — 24 ottobre 2026

## Modifiche

- Le snapshot live di ciascuna replica usano ora una coda per sessione: notifiche multiple durante una lettura attivano un'ulteriore lettura aggiornata, impedendo l'invio fuori ordine di snapshot obsolete.
- Ogni WebSocket ha un limite di 2 MiB di dati in attesa. I client lenti vengono disconnessi con codice 1013 (`slow_consumer`), evitando l'accumulo illimitato di memoria. La riconnessione recupera una nuova snapshot.
- Gli errori di lettura sono registrati e non fanno perdere le notifiche più recenti già accodate.

## Verifiche

Backend TypeScript PASS, build di produzione frontend TypeScript/Vite PASS, Node 143/143 PASS, Python 235/235 PASS. Cinque nuovi test Node verificano la coda, le sessioni indipendenti, gli errori transitori e il limite dei buffer. Non sono stati eseguiti in questo ciclo test reali PostgreSQL, browser, multi-replica o con 500 partecipanti.

## Accettazione RC ancora necessaria

Ciclo sessione con due browser, LISTEN/NOTIFY PostgreSQL su almeno due repliche API, interruzioni e riconnessioni, coerenza quiz temporizzati e risultati, 500 partecipanti simultanei, telemetria memoria WebSocket e riconnessioni. I gate infrastrutturali restano aperti/parziali.
