# Run 40549836288 — clic contestuale del canvas coperto

- Baseline committata `b6736aaab6b7dc11e33bedecd4ceb9954d7e8ed3`.
- Gate qualità FALLITO sul test Chromium dell'editor; build/publisher SALTATI. I preflight di layout, CSS, autosave/Esci e mobile erano PASSATI.
- Errore: il clic destro del test a 7 px dall'angolo del canvas colpiva l'intestazione `.editor-mock-brand` dopo lo scorrimento della sezione accessibile.
- Correzione: leggere viewport, area centrale, rettangolo canvas e `document.elementFromPoint`; individuare un pixel visibile, esclusi widget e menu, e fare un normale clic destro. La stessa logica è condivisa tra Chromium mock, PostgreSQL, chiusura dei menu e coordinate touch.
- Nuovo preflight obbligatorio riproduce il vecchio fallimento e verifica apertura, azione, chiusura e riapertura su desktop e viewport touch. Nessun `force=True` né clic DOM sintetico.
- Risultati locali: 836/836 test Python, 447/447 test Node e preflight Chromium PASS. Full CI con PostgreSQL ancora da eseguire.
- RC: 53,0% invariato, gate editor parziali; nessuna pubblicazione né commit eseguito.
