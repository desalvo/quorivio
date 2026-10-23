# Configurazione attività direttamente dai widget — 0.1.0-dev

Nel canvas selezionare un widget `question` o `timed-quiz`: viene mostrato un pannello dedicato per modificare il testo della domanda, il tipo di risposta (scelta singola/multipla, e per le domande anche testo/file), le opzioni fino a 12, l'obbligatorietà, le risposte corrette e la durata (5–600 secondi) per quiz a tempo. Salvare il layout della pagina dopo le modifiche.

I widget e il formato degli identificativi restano compatibili con le API esistenti. La validazione server e le restrizioni relative alle modifiche dei quiz live continuano ad applicarsi.

**Accettazione ancora pendente:** build frontend con dipendenze installate, test browser di creazione/modifica/salvataggio/riapertura, quiz reale con partecipanti e test Kubernetes. Il modulo attività legacy non è stato eliminato.
