# Domande indipendenti come widget — 0.1.0-dev

Ogni pagina può contenere più widget `question`, ciascuno con identificativo univoco, titolo, modalità (`single`, `multiple`, `text`, `file`), campo `required` e opzioni proprie. Dal pannello widget il presentatore imposta modalità, obbligatorietà e opzioni; salva il layout della pagina. Il partecipante risponde separatamente a ciascun widget senza modificare la risposta primaria della pagina.

Endpoint: `POST /api/join/:code/activities/:aid/widgets/:wid/respond`. Body per scelta singola `{ "option_id": "choice-1" }`, multipla `{ "option_ids": ["choice-1", "choice-2"] }`, testo `{ "text": "..." }` oppure file `{ "asset_id": "UUID" }`. L'identità deriva dal cookie di partecipazione alla sessione. Il server richiede la sessione attiva e l'attività aperta, verifica la configurazione persistita e scrive in `widget_answers` con unicità `(activity_id,participant_id,widget_id)`.

Un presentatore autorizzato può leggere i soli conteggi aggregati da `GET /api/sessions/:id/widget-answers`. Per privacy il dettaglio delle risposte non viene pubblicato ai partecipanti. Limitazioni: manca il flusso upload per anonimi, i test PostgreSQL/browser sono pendenti, la modifica di un widget già votato non produce una revisione storicizzata; la rimozione dal layout non elimina i record storici, ma gli stessi saranno eliminati con la sessione.
