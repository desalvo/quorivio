# Quorivio RC166 — Verifica GitGuardian e credenziali CI

La run GitHub `41802327982` è verde (inclusi gate di qualità e campagna RC). La segnalazione esterna «Generic Password» non è inclusa nei log della run: identificare nel portale GitGuardian **file, riga, commit, validità e sorgente** dell'incidente, senza condividere il valore in chiaro.

Il repository conteneva password statiche per i soli test CI temporanei. RC166 sostituisce quelle usate nel workflow principale con valori generati per esecuzione: PostgreSQL è vincolato all'identificativo del workflow e al commit; autenticazione amministratore, cambio password, chiave AUTH e SMTP sono prodotti con `openssl rand`, mascherati e comunicati solo ai passi successivi del job. Le fixture di bootstrap, timer PostgreSQL e SSO non usano più quelle password statiche. Questo è un intervento preventivo: **non dimostra che l'incidente GitGuardian sia quello**, né cancella i valori dalla cronologia Git.

Se il valore rilevato è una vera credenziale valida (deploy, database, OAuth, Docker Hub, utente, SMTP), revocarla/ruotarla immediatamente e verificarne l'uso. Se è una fixture di test non utilizzabile fuori dalla CI, annotare la prova e classificare manualmente l'incidente come falso positivo/test credential **solo dopo** aver verificato il dettaglio. Non disabilitare lo scanner o ignorare genericamente la regola. Per la storia Git serve valutazione separata prima di un'eventuale riscrittura concordata.

RC version invariata `0.1.0-dev`; nessun commit, push o deploy effettuato. La nuova CI deve convalidare l'intera pipeline con le credenziali effimere. Il completamento resta 85,25% in assenza di nuovi criteri d'accettazione verificati.
