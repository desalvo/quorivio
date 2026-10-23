# Classifica quiz a tempo: paginazione
L'endpoint riservato ai presentatori autenticati `GET /api/sessions/:id/activities/:aid/timed-leaderboard?page=N` restituisce al massimo 20 risposte corrette per pagina. Ordina per millisecondi trascorsi, timestamp di invio e UUID della risposta. I campi `page`, `page_size`, `total_pages`, `correct`, `answers` e `ranking[].rank` permettono di navigare mantenendo la posizione globale. Le risposte errate sono escluse e l'endpoint dei partecipanti non espone le identità della classifica. La misura lato server risente della latenza di rete e non costituisce una correzione delle differenze di latenza.

Serve ancora un collaudo PostgreSQL e multi-browser durante una sessione reale, verificando paginazione e riservatezza dei dati.
