# Autorizzazione WebSocket dei presentatori su più repliche

Dal presente ciclo cumulativo 0.1.0-dev, ciascuna replica API verifica ogni 10 secondi le connessioni WebSocket già aperte dei presentatori autenticati, interrogando PostgreSQL. Sono applicati revoca amministrativa MFA, cambio password, stato di approvazione e obbligo di cambio password. Una connessione revocata viene chiusa con codice 4003; in caso di indisponibilità del database le connessioni interessate vengono chiuse con codice 1011 (fail-closed). Le connessioni dei partecipanti continuano a seguire le regole preesistenti: questa modifica non introduce la loro revoca.

La verifica tramite database condiviso funziona concettualmente tra repliche senza notifiche locali. La revoca **non è immediata**: si prevede un massimo approssimativo di 10 secondi più latenze di pianificazione/database, da verificare prima della produzione. I messaggi in transito prima della verifica possono ancora essere ricevuti. Servono collaudi con PostgreSQL reale, più repliche, bilanciamento e riconnessione.

Verifiche locali: build API TypeScript, build Vite produzione, 95 test Node, 93 test Python. Non equivalgono a un test reale multi-replica. Il secondo fattore email facoltativo e le altre funzioni admin/SSO restano aperti.
