# Editor delle pagine e dei widget (0.1.0-dev)

- Ogni attività ammette una sequenza di widget; trascina per riordinare o usa i comandi ↑/↓.
- Dal menu del widget modifica titolo, descrizione, modalità di risposta e stile (font, dimensione, colore, grassetto, corsivo, sottolineato, barrato, animazioni).
- Il titolo è obbligatorio per i widget di gradimento; la descrizione è facoltativa. Il partecipante può inserire un commento facoltativo fino a 1000 caratteri insieme al voto, memorizzato in PostgreSQL; i commenti non sono inclusi nei riepiloghi pubblici.
- Per modificare velocemente un titolo fai doppio clic nel campo (selezione testo), modifica e salva il layout.
- Il widget domanda è un elemento visuale aggiuntivo: l'invio di risposte resta legato all'attività corrente; le risposte indipendenti per ogni widget richiedono un modello dati aggiuntivo.
- Le animazioni devono rispettare prefers-reduced-motion. Test end-to-end browser e PostgreSQL ancora pendenti.
