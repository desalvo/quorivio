# Backup e ripristino completo di Quorivio (IT)

## Ambito e stato

La prima procedura **offline** comprende un dump PostgreSQL in formato custom e i file della directory privata degli asset, raccolti in un archivio `.tar.gz` con manifest e checksum SHA-256 per ogni elemento. Non costituisce ancora una funzione accessibile dal pannello amministratore. Le prove con un server PostgreSQL reale, uno storage S3 o un cluster Kubernetes non sono state effettuate.

## Prerequisiti

Fermare le scritture dell'applicazione prima del backup e del restore. Installare `pg_dump`/`pg_restore` compatibili con il server PostgreSQL in un ambiente amministrativo protetto. Definire `DATABASE_URL` nell'ambiente senza inserirlo nella shell history. Eseguire la procedura con permessi sull'archivio asset, assicurando che l'utente del processo possa leggerne tutti i file. Le password e i dati personali del database e dei contenuti sono sensibili: **cifrare il backup, proteggerne la chiave, definire un periodo di conservazione e verificare le autorizzazioni**.

## Backup

```bash
export DATABASE_URL='postgresql://...'
python3 tools/instance_backup.py backup --assets /app/assets --output /secure/backups/quorivio-YYYYMMDD.tar.gz
python3 tools/instance_backup.py verify --input /secure/backups/quorivio-YYYYMMDD.tar.gz
```

Per `docker compose`, eseguire l'operazione da un host/sidecar amministrativo con accesso **in sola lettura** agli asset e al database. Non eseguire `pg_dump` o i comandi nell'immagine runtime che non contiene necessariamente i tool PostgreSQL.

## Ripristino

1. Creare un nuovo database **vuoto** e una directory asset **vuota** su un ambiente isolato.
2. Verificare SHA-256 ed integrità dell'archivio con il comando `verify`.
3. Fermare le applicazioni che potrebbero scrivere durante il ripristino.
4. Eseguire:

```bash
python3 tools/instance_backup.py restore --input /secure/backups/quorivio-YYYYMMDD.tar.gz --assets /new-assets --confirm RESTORE-QUORIVIO-DATA
```

5. Verificare migrazioni, collegamenti tra record e file, accessi/ruoli, salute dei servizi e funzionalità su una copia di staging prima della produzione.

Non utilizzare il restore su un database contenente dati: lo script non esegue `--clean`. Il ripristino **non è transazionale tra PostgreSQL e filesystem**: in caso di errore ricreare entrambi i target vuoti e ripartire; non riutilizzare un target parzialmente popolato.

## Kubernetes

Il wizard genera `15-assets-pvc.yaml` con `asset_storage_size` (default `10Gi`), `asset_storage_class` e `asset_access_mode`. L'app monta il PVC in `/app/assets`. `ReadWriteMany` va selezionato solo se realmente supportato dallo StorageClass. Restano richiesti backup del PVC e di PostgreSQL coordinati, test di disaster recovery e verifiche GDPR.

## Limiti prima della produzione

Non sono ancora disponibili: pulsanti amministrativi di backup/restore, schedulazione integrata, crittografia automatica degli archivi, snapshot coordinati, storage S3 e test PostgreSQL reali. Questa funzionalità è una procedura amministrativa iniziale, non un disaster recovery certificato.

## Rafforzamento ripristino (24 ottobre 2026)

La CI PostgreSQL 18 è stata confermata verde dal manutentore. Prima di `pg_restore`, lo script verifica che il database di destinazione non contenga relazioni applicative: un database già popolato o una verifica fallita interrompono il ripristino senza modifiche. I dati estratti vengono inoltre ricontrollati tramite SHA-256 e dimensione, anche dopo la verifica iniziale dell'archivio, prima di scrivere nel database. La CI controlla anche il rifiuto del ripristino nel database sorgente, la corrispondenza dello schema, la riservatezza della directory degli allegati e i tempi di backup/ripristino; questi tempi non sono SLA RTO/RPO.

Restano obbligatori una prova di disaster recovery operativa, politiche di cifratura e conservazione, test con dati rappresentativi e la convalida di RPO/RTO.
