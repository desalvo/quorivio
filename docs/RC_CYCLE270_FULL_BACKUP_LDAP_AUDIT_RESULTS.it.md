# Quorivio 0.1.0-dev — RC270 | Full export, LDAP, audit, grafici risultati

## Stato e compatibilità

Base: **RC269**, archivio originale validato con SHA-256. RC270 contiene codice sorgente cumulativo. Nessun commit, push, tag o pubblicazione. La baseline generale **85,25% (43 gate accettati, 17 parziali)** rimane invariata finché la CI completa e il collaudo di ripristino non sono disponibili: non attribuire falsi incrementi percentuali. RC270 non è dichiarata release candidate finale accettata.

## Backup completo di istanza

* Admin piattaforma → **Configurazione server → Backup completo**: PostgreSQL dump custom (`pg_dump` v18), intera directory degli asset persistenti (immagini, media, sfondi, foto e materiale di sessione), `manifest.json`, tar.gz, SHA-256, download diretto da browser autorizzato.
* Un'unica destinazione attiva configurabile per backup on-demand e per la **pianificazione periodica da 1 a 720 ore**, con registro delle ultime 25 esecuzioni. Backend `posix`, `nfs` (sottocartella sotto volume già montato), `s3` (multipart HTTPS SigV4) e `webdav` (PUT HTTPS, redirect disabilitati). La generazione browser è indipendente dalla destinazione salvata; lo scheduler multi-pod reclama il turno con UPDATE atomico nel DB.
* Helm: `backup.allowedBackends`, `backup.posix.enabled`, `backup.posix.existingClaim|accessMode|size|storageClassName`, `backup.nfs.enabled`, `backup.nfs.existingClaim` oppure `server`+`path` (mount diretto nel pod), `backup.tmpSize` (scratch disco), `backup.bootstrap.*`. Se `backup.bootstrap.existingSecret` è valorizzato, creare un Secret con chiave `BACKUP_TARGET_JSON` contenente l'oggetto JSON di destinazione; impostare `backup.bootstrap.enabled` e `intervalHours` facoltativamente. In alternativa si può passare `backup.bootstrap.target` (ma NON inserire credenziali nei valori Helm non protetti). Il target viene importato una volta, cifrato AES-256-GCM lato server con chiave derivata da AUTH_SECRET, poi amministrabile via UI; i redeploy non lo sovrascrivono.
* Wizard standalone `tools/k8s_wizard.py`: tutte le voci `backup_*` per abilitazione, volume POSIX nuovo/esistente, server/export NFS, destinazioni remote con credenziali e programmazione. Le credenziali sono archiviate nel file YAML `05-app-secret.yaml` e negli override a permessi `0600`: **non aggiungere mai manifest/override del wizard in Git**. Parametri di connessione WebDAV/S3 validati anche dall'API al bootstrap. Compose: named volumes per backup POSIX e `/tmp` dell'app.
* In Kubernetes l'API ha filesystem in sola lettura: lo scratch `emptyDir` montato su `/tmp` deve contenere sia il dump sia l'archivio. Con più repliche e PVC POSIX sono richiesti RWX; NFS richiede permessi scrivibili dall'UID 1000 e un export raggiungibile dai nodi. Conservare le credenziali nello storage segreto del cluster, non nei log.
* **Restore offline, manuale e non implementato automaticamente**: fermare scritture/traffico, conservare una copia dell'istanza precedente, creare database vuoto, `pg_restore --clean --if-exists --no-owner --no-privileges -d <database> database.dump` e ripristinare la directory `assets/` nel PVC Quorivio; applicare il manifest e verificare la consistenza tra database e file. Testare sempre prima su ambiente di staging. PostgreSQL dump e asset non sono uno snapshot atomico simultaneo: per una garanzia point-in-time è necessario quiescere i writer o effettuare snapshot coordinati. I backup contengono dati personali e segreti; cifrare e gestire scadenze/permessi a livello storage. La retention *automatica delle copie di backup sul backend* non è ancora implementata (resta a carico del backend/operatori). Ripristino automatico e schedule multiple sono backlog.

## Directory LDAP e approvazione

* Nuova autoregistrazione LDAP/AD con **bind dell'utente e password reale**, creazione identità collegata e account `approved=false`; non è possibile fare login prima dell'approvazione di un amministratore. Login LDAP con autoprovisioning opzionale crea comunque account pendente. Ruoli LDAP non prevalgono più su quelli autorizzati nel pannello admin.
* Email ai platform admin approvati tramite SMTP configurato per ogni nuova registrazione locale/LDAP. Senza SMTP il sistema mantiene l'account pending ma non recapita la notifica (log esplicito).
* Pannello utenti admin: ricerca LDAP autenticata con service bind, selezione identità stabile e creazione account autorizzato con ruolo scelto. Per motivi di sicurezza una identità già assegnata non viene ricollegata implicitamente.

## Audit GDPR

* Tracciamento delle mutazioni API amministrative, sessioni, presenter e MFA dopo risposta positiva: chi, timestamp, rotta normalizzata, UUID risorsa quando disponibile, metodo e stato HTTP. **Mai** password, payload, token, indirizzo IP, cookie o dettagli delle risposte dei partecipanti.
* Admin → Configurazione server → Audit: ricerca per risorsa/UUID/utente, registro paginabile lato API, retention da 7 a 3650 giorni, purge manuale e cancellazione automatica oraria. Migrazione SQL additiva in `apps/api/src/schema.sql`.

## Grafici risultati

* **Formato widget → Contenuti**: per torta, opzione numeri (fette e testo delle opzioni sotto), opzione percentuali su fetta; colore fetta derivato dalla formattazione dell'opzione o della riga. Per grafico a barre, gradiente opzionale con saturazione/tonalità proporzionale agli hit rispetto al massimo della serie. Render condiviso in editor, preview e proiezione.

## Test locali e verifiche richieste

* Eseguiti `node --experimental-strip-types --test apps/api/test/rc270-backup-audit.test.ts`, `node --experimental-strip-types --test apps/api/test/rc269-ldap-housekeeping.test.ts`, `python3 -m unittest tools/test_rc270_wizard_backup.py`; verifica sintattica TS/TSX via compilatore TypeScript globale; wizard Python compilato e manifest POSIX/NFS generati.
* Non eseguiti: build Node/npm end-to-end (dipendenze non disponibili offline), render Helm CLI, bootstrap DB vero, trasferimento reale S3/WebDAV, restore di PostgreSQL 18, LDAP/SMTP in infrastruttura, browser cross-platform, full CI GitHub. Aggiungere test di integrazione, prova di restore e verifica credenziali su cluster prima di accettare la RC.
