# MFA email: protezione invii e concorrenza

Il login limita a tre richieste per utente e finestra di un minuto tramite contatori condivisi in PostgreSQL. Una sola sfida email rimane valida per account grazie a `INSERT ... ON CONFLICT(user_id) DO UPDATE` e indice univoco. La migrazione elimina eventuali sfide duplicate storiche conservando la più recente.

Verifiche: compilazione TypeScript backend, build Vite frontend, test Node.js e test Python disponibili. **Non ancora verificati:** consegna SMTP reale, concorrenza PostgreSQL, repliche multiple, flusso browser ed equità di rete. Questi gate RC restano aperti.
