# Scansione antivirus degli upload (sviluppo 0.1.0-dev)

Gli upload dei presentatori, dei partecipanti e dei documenti da convertire possono essere esaminati da un servizio ClamAV/clamd tramite protocollo `INSTREAM`, senza eseguire programmi esterni nel processo web. Il server invia blocchi di dimensione limitata e non considera `FOUND`, `ERROR`, timeout o interruzioni come esiti puliti.

## Configurazione

- `QUORIVIO_AV_REQUIRED=true`: obbliga lo scanner; in assenza di `CLAMAV_HOST`, le richieste interessate falliscono senza registrare il file.
- `CLAMAV_HOST`: nome DNS del servizio clamd raggiungibile in rete privata; non pubblicare la porta al pubblico.
- `CLAMAV_PORT`: porta TCP clamd, normalmente 3310.
- `CLAMAV_TIMEOUT_MS`: timeout per la connessione/scansione, default 30000.

Il valore di default `QUORIVIO_AV_REQUIRED=false` serve alla compatibilità degli ambienti di sviluppo; **non è una configurazione di produzione sicura**. In produzione predisporre un servizio ClamAV, aggiornare le firme e richiedere esplicitamente la scansione. Non caricare materiale riservato in servizi antivirus esterni non autorizzati.

## Verifica e limiti

Test automatizzati con un server fittizio controllano esiti puliti, minacce e anomalie. Restano da collaudare clamd reale, scansione concorrente, gestione dei timeout con file grandi, rate limit distribuiti e capacità dello storage condiviso. Gli errori attuali vengono riportati genericamente dall'API come `internal_error` anziché come una risposta specifica antivirus.
