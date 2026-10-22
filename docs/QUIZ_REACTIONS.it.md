# Quiz e reazioni — Quorivio 0.1.0-dev

Quiz e sondaggi: risposta singola, multipla, testo libero fino a 5000 caratteri, o riferimento a file; proprietà di obbligatorietà della risposta; validazione lato server. Reazioni: 👍 ❤️ 😂 😮 👏 🎉 🤔 😕, una per partecipante per attività; statistiche per pagina, partecipante e sessione per presentatori autorizzati. Il database conserva le risposte strutturate in JSONB e usa una chiave univoca per le reazioni.

**Non completato**: caricamento allegati da anonimi tramite il flusso partecipante, reazioni su pagine non-attività, gruppi di quiz, test end-to-end PostgreSQL/browser e produzione.
