# RC70 — Aggiornamento editor e timer di pagina

Il timer è configurabile nelle proprietà del singolo widget (1–3600 s; default 60). Il timer della pagina blocca tutte le interazioni dei partecipanti allo scadere: in simulazione, nella vista web live e sul server con l'orologio PostgreSQL. In presenza di più timer vale la prima scadenza.

La modifica di dimensione globale del widget preserva i rapporti tra le dimensioni locali del testo, il tipo di font, colore e stile di ogni porzione. Le maniglie di dimensionamento/rotazione dei widget selezionati sono al di fuori del ritaglio. Il contatore partecipanti è solo per il presentatore; in prova usa dati dimostrativi. Nella prova affiancata le risposte testuali inviate devono essere mostrate al presentatore assieme ai dati dimostrativi. L'email del profilo presentatore è mostrata in anteprima privata; la pubblicazione agli utenti resta solo con consenso esplicito.

**Nota di rilascio:** a questo ciclo non viene attribuito incremento del punteggio RC; richiede nuova CI completa e test browser/PostgreSQL su commit nuovo.
