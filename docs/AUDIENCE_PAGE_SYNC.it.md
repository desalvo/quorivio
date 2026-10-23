# Sincronizzazione delle pagine del partecipante guidata dal presentatore

Il client del partecipante ora sceglie la pagina da uno snapshot WebSocket tramite `session.current_activity_id`, soltanto se la pagina è `open`. In precedenza prendeva sempre la prima attività, lasciando il partecipante sulla prima slide dopo l'avanzamento del presentatore. Quando nessuna pagina è aperta torna alla schermata di attesa. Rimane invariato il timestamp server per i quiz a tempo.

## Verifiche e limiti

Build di produzione backend e Vite PASS; 107 test Node e 96 test Python PASS (inclusa regressione statica). Mancano ancora collaudi reali con due browser e PostgreSQL: il nuovo test non costituisce accettazione E2E.
