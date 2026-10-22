# Sequenza grafica delle pagine e duplicazione

Versione: 0.1.0-dev. Il presentatore approvato (incluso un amministratore autorizzato) apre la sessione e, nella lista delle attività, sceglie **↑ / ↓** per spostare una pagina o **Duplica pagina** per creare una copia indipendente in fondo alla sequenza.

Il server controlla che la sequenza contenga esattamente le pagine della sessione, con identificativi unici; aggiorna tutti gli ordinamenti in una transazione PostgreSQL e invia uno snapshot WebSocket dopo il commit. L'ordine può essere modificato anche con sessione attiva; la pagina corrente e le risposte restano associate agli stessi identificativi. Non è consentito modificare una sessione chiusa.

La duplicazione copia soltanto definizioni, impostazioni di quiz, stili e widget; **non** replica voti, reazioni o identità dei partecipanti. Il duplicato viene aggiunto alla fine. La vista non è ancora un canvas con drag & drop delle pagine; servono collaudi reali PostgreSQL/browser e test concorrenti prima della produzione.
