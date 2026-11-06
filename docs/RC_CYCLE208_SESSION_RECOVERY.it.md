# RC208 — Prevenzione dashboard vuota e ripristino sessioni avviate

## Segnalazione

Durante la riapertura di una sessione già avviata o della sua dashboard l'interfaccia poteva risultare vuota, con necessità apparente di cancellare i cookie. Non è disponibile l'eccezione esatta del browser in produzione: l'analisi della RC207 ha però identificato una fragilità concreta nel caricamento anticipato del WebSocket e della sessione prima dell'autenticazione, richieste HTTP senza timeout, mancanza di comandi di recupero quando non arriva lo snapshot e assenza di un contenitore che intercetti gli errori React. La correlazione con il refresh QR non costituisce da sola prova di causalità.

## Correzioni

- Caricamento delle sessioni proprietario/presentatore subordinato al controllo di autenticazione; timeout di 12 secondi per login e prima lettura della sessione.
- Se il server è temporaneamente indisponibile: stato visibile, «Riprova ora», «Torna alle sessioni» e tentativi automatici limitati in frequenza. Non si svuotano i cookie. Il fallback HTTP del WebSocket accetta una sola richiesta contemporanea, interrotta dopo 10 secondi.
- Su 401: ritorno al login; su 403/404/410: eliminazione del solo percorso persistito della scheda e ritorno all'elenco.
- Snapshot WebSocket incompleti o appartenenti ad altre sessioni non possono sovrascrivere il contenuto. Statistiche opzionali mancanti normalizzate.
- Intercettazione errori di rendering React: un solo tentativo automatico di ripristino senza cancellazione cookie; altrimenti comandi di recupero visibili.
- Timeout di 9 secondi per la singola richiesta QR, mantenendo l'aggiornamento live e la rimozione del vecchio QR revocato.
- Test Node/Python, oltre allo scenario Chromium integrato per riapertura attiva, rotazione QR, 503 e 401. La verifica compilata e la full CI restano da eseguire.

**Versione:** `0.1.0-dev`; **completamento certificato:** 85,25% (43 accettati, 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag da parte dell'assistente.
