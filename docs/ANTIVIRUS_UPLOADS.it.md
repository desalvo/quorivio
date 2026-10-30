# Scansione antivirus degli upload (sviluppo 0.1.0-dev)

Gli upload dei presentatori, dei partecipanti e dei documenti da convertire possono essere esaminati da un servizio ClamAV/clamd tramite protocollo `INSTREAM`, senza eseguire programmi esterni nel processo web. Il server invia blocchi di dimensione limitata e non considera `FOUND`, `ERROR`, timeout o interruzioni come esiti puliti.

## Configurazione

- `QUORIVIO_AV_REQUIRED=true`: obbliga lo scanner; in assenza di `CLAMAV_HOST`, le richieste interessate falliscono senza registrare il file.
- `CLAMAV_HOST`: nome DNS del servizio clamd raggiungibile in rete privata; non pubblicare la porta al pubblico.
- `CLAMAV_PORT`: porta TCP clamd, normalmente 3310.
- `CLAMAV_TIMEOUT_MS`: timeout per la connessione/scansione, default 30000.

In produzione la scansione è ora sempre obbligatoria per gli upload, anche quando `QUORIVIO_AV_REQUIRED` è assente oppure impostato a `false`. La disattivazione esplicita è consentita **solo fuori dalla produzione** per sviluppo e test controllati. Valori booleani errati vengono rifiutati; timeout complessivo, connessioni interrotte, risposte anticipate ed eccessive falliscono in modo sicuro. In produzione predisporre un servizio ClamAV, aggiornare le firme e richiedere esplicitamente la scansione. Non caricare materiale riservato in servizi antivirus esterni non autorizzati.

## Verifica e limiti

Test automatizzati con un server fittizio controllano esiti puliti, minacce e anomalie. Restano da collaudare clamd reale, scansione concorrente, gestione dei timeout con file grandi, rate limit distribuiti e capacità dello storage condiviso. Gli errori attuali vengono riportati genericamente dall'API come `internal_error` anziché come una risposta specifica antivirus.

## Generatore Kubernetes (ciclo 32)

Il wizard `tools/k8s_wizard.py` genera per impostazione predefinita (`antivirus_mode=managed`) un Deployment ClamAV privato, un Service ClusterIP e una NetworkPolicy che consente connessioni dai soli pod applicativi. L'app riceve `QUORIVIO_AV_REQUIRED=true` e il nome DNS del servizio privato. Se lo scanner è gestito esternamente usare `antivirus_mode=external` con `antivirus_host=<DNS privato>`; il wizard non crea in quel caso lo scanner. Cambiando modalità vengono rimossi i manifest gestiti precedentemente. Se il servizio esterno non risponde gli upload vengono rifiutati.

Lo scanner può richiedere fino a 4 GiB durante il caricamento/aggiornamento delle firme; predisporre memoria sufficiente e verificare i privilegi richiesti dall'immagine. Configurare `StreamMaxLength` nel clamd reale in coerenza con il limite upload: file superiori al limite del demone vengono rifiutati, mai accettati senza scansione. I test di questo ciclo verificano manifest e protocollo simulato, non certificano l'avvio dell'immagine reale, le firme antivirus, la policy Pod Security o i collaudi operativi.

## CI opzionale ClamAV reale

Con `clamav_runtime_test=true` la workflow GitHub avvia un container ClamAV isolato, con porta esposta **soltanto su loopback**, verifica un file temporaneo pulito e il campione EICAR innocuo, quindi elimina container e file. Il superamento del job fornisce una prova con motore e firme reali, non sostituisce il penetration test o una revisione operativa. Il test è opzionale per il maggiore consumo di RAM e i tempi di inizializzazione del database firme.
