# Visualizzazione risultati presentatore — 23 ottobre 2026

Questo ciclo aggiunge una scelta persistente al widget `results-button` della pagina: barre (predefinito), torta proporzionale o tabella compatta. Le proprietà vengono salvate nel JSON del layout esistente, senza migrazioni. La vista riservata al presentatore segue la pagina attiva e conserva la classifica dei quiz a tempo e la paginazione delle domande per argomento. Con dati assenti non si mostra un grafico a torta fuorviante. La sorgente dei conteggi rimane l'aggregato dell'attività.

**Limiti:** è una visualizzazione aggregata di pagina configurata dal pulsante Risultati, **non** un motore di statistiche per singolo widget interattivo. Rimangono aperti i quiz multipli indipendenti nella stessa pagina, la scelta individuale di grafici, le nuvole di parole nel pannello e i collaudi browser/database. Non considerare completati tali gate.

Verificati localmente build TypeScript backend, frontend TypeScript/Vite, 90 test Node.js e 93 test Python con il binario esbuild Linux fornito separatamente. Non eseguiti i collaudi browser e PostgreSQL. I manuali PDF non sono ancora allineati a questa impostazione.
