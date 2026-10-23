# Sessioni, layout e risposte invalidate — IT

## Configurazione delle immagini container
La distribuzione Compose utilizza per impostazione predefinita `desalvo/quorivio:latest` (sovrascrivibile con `QUORIVIO_IMAGE`), così come il wizard Kubernetes. Il repository dei sorgenti rimane `github.com/desalvo/quorivio`. Il workflow pubblica le immagini su `desalvo/quorivio`; verificare che il repository esista su Docker Hub e che il token abbia permessi di scrittura.

## Presentatore: nome, data e layout
Dalla pagina di creazione, assegnare il titolo e la data di riferimento. Selezionare poi la sessione e usare **Metadati della sessione** per modificarli anche durante lo svolgimento; le risposte esistenti sono conservate. Dalla riga di un'attività selezionare **Layout pagina**, impostare intestazioni e sfondi HTTPS separati per domanda e risultati, poi salvare. I loghi comuni restano nel tema di sessione. È supportato il modello dati delle pagine, ma la resa browser di tutti gli elementi multimediali deve essere ancora verificata.

## Invalidazione e nuova risposta
Il presentatore può invalidare tutte le risposte di una domanda: le righe storiche sono conservate per audit ma non concorrono ai risultati attivi. Dopo l'invalidazione è ammessa una nuova risposta per il partecipante alla stessa attività, se essa viene riaperta ed è ancora disponibile. La migrazione sostituisce il precedente vincolo UNIQUE su `(activity_id,participant_id)` con un indice univoco parziale per le sole risposte non invalidate. Applicare lo schema prima di aggiornare il backend e verificare il percorso con un PostgreSQL reale.

## Avvertenze
La build TypeScript completa, l'interfaccia browser e la migrazione PostgreSQL non sono state validate in questo ciclo. Non eseguire aggiornamenti in produzione senza backup e collaudo.
