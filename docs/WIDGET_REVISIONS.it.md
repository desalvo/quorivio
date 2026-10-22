# Revisioni delle domande-widget — 0.1.0-dev

Durante una sessione attiva, il presentatore può modificare il formato di una domanda-widget. Le modifiche a modalità, obbligatorietà o opzioni creano una nuova revisione numerica in `widget_revisions`, preservando le risposte precedenti in `widget_answers` e il loro numero di revisione. Cambiare soltanto l’etichetta o lo stile non apre una nuova revisione.

## Operazioni

1. Aprire l’editor della sessione come presentatore autorizzato.
2. Modificare la configurazione del widget domanda e salvare la pagina.
3. I nuovi invii sono associati alla nuova revisione; gli invii precedenti restano disponibili come dati storici.
4. `GET /api/sessions/{id}/widget-answers` restituisce conteggi raggruppati per revisione.
5. `GET /api/sessions/{id}/widget-answers/detail?activity_id={uuid}&widget_id={id}` restituisce distribuzioni delle opzioni per revisione, conteggi di risposte libere e allegati, senza pubblicare testi individuali.

**Limitazioni:** non è stato verificato il comportamento con un database PostgreSQL reale; l’invalidazione selettiva, le autorizzazioni multi-organizzazione e i test concorrenti richiedono verifiche ulteriori. Il caricamento di allegati da anonimi rimane aperto. Le migrazioni SQL devono essere sottoposte a backup e collaudo prima del rilascio.
