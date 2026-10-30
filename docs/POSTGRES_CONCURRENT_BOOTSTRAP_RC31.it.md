# RC ciclo 31 — avvio concorrente PostgreSQL 18

## Lacuna funzionale corretta
Prima del ciclo 31, ogni replica API eseguiva indipendentemente `schema.sql` e verificava la tabella utenti prima di creare l'amministratore iniziale. Due pod avviati insieme potevano entrare in competizione nelle migrazioni, nei vincoli univoci o nella creazione incompleta dell'organizzazione e dell'utente.

Ora l'avvio protegge **schema e creazione iniziale** con un advisory lock PostgreSQL di sessione su **una connessione dedicata**, usata per tutte le operazioni nella sezione critica. Organizzazione, amministratore e sessione/tutorial vengono creati in **un'unica transazione**: in caso di errore si esegue il rollback. Il blocco ha un limite di attesa di **120 secondi**; viene rilasciato sempre e la connessione viene eliminata dal pool se non è possibile confermare il rilascio. Il server diventa raggiungibile soltanto dopo il bootstrap. Listener WebSocket e processi periodici rimangono al di fuori della sezione protetta.

## Prova CI introdotta (ancora da eseguire dopo il commit)
Nel quality gate standard si crea un database PostgreSQL 18 **temporaneo distinto** (`quorivio_bootstrap_ci`), si avviano simultaneamente due processi API realmente compilati su porte differenti e si controllano entrambe le readiness, una sola organizzazione, un solo amministratore e un solo utente. Processi e database vengono rimossi anche in caso di errore. Nessun log completo o dato privato viene pubblicato.

I test locali verificano l'algoritmo di esclusione, gli errori e i vincoli della CI. Il test reale con due processi e PostgreSQL **non è stato eseguito localmente**: dovrà essere confermato dalla prossima GitHub CI. La percentuale RC ufficiale resta **79,25%** e 17 gate di verifica indipendente rimangono parziali. Resta inoltre da eseguire su GitHub il test multiworker NGINX del ciclo 29. Non si afferma che PostgreSQL HA, CSI RWX, HAProxy o nodi fisici indipendenti siano certificati.

## Limiti operativi
- Se una migrazione impiega più di 120 secondi, una replica in attesa può fallire l'avvio ed essere riavviata da Kubernetes; non eliminare il lock per aggirare il problema.
- Per l'alta disponibilità del database è necessario un servizio PostgreSQL HA gestito separatamente: la serializzazione dell'avvio **non** equivale al failover del database.
- Non abilitare il gate RC strict finché non risultano concluse le verifiche esterne, storage, dispositivi, accessibilità e conformità.
