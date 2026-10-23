# Quiz a tempo e pulsante Risultati — implementazione iniziale (23 ottobre 2026)

## Disponibile nel package
- Tipologia attività distinta `timed_quiz` dalla scelta «Quiz a tempo (classifica)», con risposte singole o multiple e scadenza obbligatoria tra 5 e 600 secondi (attualmente 30 secondi dalla UI).
- Avvio autorevole con `activities.opened_at` scritto dal server quando il presentatore apre la pagina e diffuso ai partecipanti via WebSocket; il tempo è calcolato dal server all'arrivo della risposta, **non** dal cronometro JavaScript del client.
- `responses.elapsed_ms`, indice parziale sulla classifica e endpoint riservato ai presentatori `GET /api/sessions/:id/activities/:aid/timed-leaderboard`: contatori totali e corrette; primi 100 partecipanti corretti ordinati per millisecondi, data invio e UUID (spareggio deterministico).
- Validazione di risposte singole e multiple corrette, esclusione di errori e risposte invalidate, non divulgazione della chiave corretta nelle risposte pubbliche.
- Widget di palette indipendenti «timed-quiz» e «results-button», con geometria salvata; pagina presentatore con controllo «Risultati», inizialmente chiuso, e classifica aggiornata ogni 2 secondi. Il pulsante non viene mostrato ai partecipanti.
- Countdown su schermo partecipante e presentatore basato su opened_at; frontend e backend compilano; test unitari Node 90/90.

## Non ancora completo o collaudato
- Il widget «timed-quiz» è un marcatore visivo della domanda a tempo dell'attività, **non** un quiz autonomo multiplo sulla stessa pagina; le risposte passano attraverso l'attività principale.
- Il pulsante «Risultati» ha una posizione indicativa da layout, **non** ancora geometria assoluta identica al widget nell'editor. Le statistiche widget-specifiche e le domande per argomento restano nella dashboard separata, non nella sovrapposizione «Risultati».
- Non implementati menu contestuale per scegliere barre/torta/nuvole, rendering dei grafici differenti e modalita live/finale configurabile per ciascun widget.
- Il timestamp coincide con l'apertura server, non con la ricezione simultanea del pacchetto da ogni browser; latenze di rete, distribuzione e precisione temporale richiedono analisi e test, e non viene attestata una competizione equa al millisecondo.
- Mancano E2E PostgreSQL e browser multiutente, concorrenza/retry, verifica sicurezza privacy, più nodi e manuali PDF aggiornati.
- Percentuale gate RC invariata **67%** fino ai collaudi reali; nessun commit o release effettuati.
