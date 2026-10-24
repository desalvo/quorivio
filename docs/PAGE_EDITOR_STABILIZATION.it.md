# Stabilizzazione della selezione e del ciclo di vita dell'editor

- La duplicazione aggiorna lo snapshot e seleziona la copia identificandola tra le nuove attività; non dipende dall'ordinamento restituito dal server.
- Le miniature selezionabili supportano Freccia su/giù e Home/Fine; restano disponibili trascinamento e pulsanti di riordino.
- Quando la sessione è chiusa, l'editor disabilita creazione, eliminazione, duplicazione e riordino; il controllo effettivo dei permessi resta sul backend.
- Nessuna nuova API o migrazione; salvataggio layout preesistente conservato.
- **Da verificare:** avviso modifiche non salvate, browser, PostgreSQL e Kubernetes reali. Build non completata per assenza delle dipendenze npm in questo ambiente.
