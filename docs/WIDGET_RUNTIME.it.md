# Widget in esecuzione e portabilità — 0.1.0-dev

## Timer reale
Nel pannello del presentatore aprire **Layout pagina**, aggiungere il widget `timer`, salvare e avviare un quiz con durata configurata. Il partecipante vede i minuti e i secondi residui calcolati da `opened_at` (orario del server) e `duration_seconds`. Il timer visualizzato è indicativo: **il backend continua ad applicare il controllo temporale autorevole** anche quando l'orologio del dispositivo è impreciso. Non è ancora previsto un segnale accessibile di fine conto alla rovescia né una sincronizzazione continua dell'orologio.

## QR widget della pagina
Aggiungere `qr` dalla palette e salvarlo. Durante la sessione attiva è visualizzato un QR SVG generato dall'applicazione. Esso include **solo** la URL di ingresso pubblica e non conferisce diritti di presentazione. Il link non è disponibile per sessioni inattive o scadute. L'endpoint pubblico dispone degli stessi limiti generali di richieste delle API.

## Portabilità dei quiz
L'esportazione della definizione JSON preserva ora `answer_mode`, `answer_required`, `correct_option_ids`, il tempo e i design delle pagine. L'importazione ricrea attività con nuovi ID. **Non importa risultati, persone, file o inviti**; per il ripristino integrale si usa il backup amministrativo offline. Prima della produzione verificare in PostgreSQL la compatibilità delle esportazioni legacy.

## Stato dei controlli
I widget rating, emoji, testo, separatore, timer e QR hanno una rappresentazione nella pagina del partecipante; il drag & drop li riordina nell'editor. Non esiste ancora un sistema di widget arbitrari per tutte le tipologie di pagina, e i test browser end-to-end, di accessibilità e di carico sono pendenti.
