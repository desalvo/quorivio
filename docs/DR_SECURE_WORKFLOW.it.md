# Disaster recovery cifrato — procedura operativa integrata

**Quorivio 0.1.0-dev — sviluppo locale, 29 ottobre 2026.** Il nuovo comando consente backup, verifica, rotazione e ripristino cifrati. Non configura un pianificatore, un gestore segreti o obiettivi RPO/RTO di produzione. Il precedente `instance_backup.py backup` continua a produrre archivi non cifrati; il comando integrato **non lo sostituisce automaticamente**.

## Backup cifrato

Predisporre una directory **0700 su un filesystem cifrato**, posseduta dall'utente che esegue il comando. Durante il backup, dump e `tar.gz` non cifrati esistono soltanto in questa directory protetta e vengono eliminati al termine o in caso di errore. La rimozione dei file non garantisce cancellazione fisica su SSD, snapshot e filesystem copy-on-write. Arrestare prima tutti i processi che modificano DB o asset.

```sh
umask 077
mkdir -m 700 -p /volume-cifrato/quorivio-work
python3 tools/backup_envelope.py keygen --key-file /keys/quorivio-2026-10.key
export DATABASE_URL='postgres://<utente>:<password>@<host-db>:5432/quorivio'
python3 tools/secure_instance_backup.py backup --assets /srv/quorivio/assets --key-file /keys/quorivio-2026-10.key --work-dir /volume-cifrato/quorivio-work --output /backup/quorivio-2026-10.qenc
python3 tools/secure_instance_backup.py verify --input /backup/quorivio-2026-10.qenc --key-file /keys/quorivio-2026-10.key --work-dir /volume-cifrato/quorivio-work
```

Sono necessari `cryptography>=43,<47` e il client PostgreSQL 18. La chiave è un file casuale di 32 byte, proprietario del processo e con permessi `0600`, separato dagli archivi. Non inserire chiavi e password nei log o nei parametri della riga di comando. Il file destinazione non viene sovrascritto.

## Rotazione e ripristino

```sh
python3 tools/backup_envelope.py keygen --key-file /keys/quorivio-2026-11.key
python3 tools/secure_instance_backup.py rotate --input /backup/quorivio-2026-10.qenc --output /backup/quorivio-2026-11.qenc --old-key-file /keys/quorivio-2026-10.key --new-key-file /keys/quorivio-2026-11.key
# Solo su una destinazione isolata, con DB nuovo VUOTO e tutti i writer fermati:
export DATABASE_URL='postgres://<utente>:<password>@<host-restore>:5432/quorivio_nuovo'
python3 tools/secure_instance_backup.py restore --input /backup/quorivio-2026-11.qenc --assets /srv/quorivio-restored/assets --key-file /keys/quorivio-2026-11.key --work-dir /volume-cifrato/quorivio-work --confirm RESTORE-QUORIVIO-DATA
```

La rotazione ora funziona **in streaming senza creare copie temporanee in chiaro**. Tag errato, alterazioni, chiave sbagliata o identica alla precedente causano il rifiuto prima della pubblicazione. Il ripristino rifiuta conferma mancante, URL DB mancante, directory degli asset già occupata e database con oggetti esistenti prima di decifrare. Il ripristino di base ricontrolla gli stessi requisiti. Conservare le chiavi vecchie fino alla verifica completa della rotazione e registrare custodia, conservazione, anzianità degli archivi, tempi e perdita dati nei collaudi operativi.

**Limiti:** la CI PostgreSQL 18 eseguirà il percorso completo su un secondo DB temporaneo, ma tale verifica non è ancora stata eseguita su GitHub per questo nuovo codice. I gate D2/D6 di DR operativo, RPO/RTO, custodia chiavi e approvazioni indipendenti restano parziali.


**Ciclo 19:** le procedure di collaudo del ripristino e conservazione prudente sono in [DR_REHEARSAL_AND_RETENTION.it.md](DR_REHEARSAL_AND_RETENTION.it.md). Tempi tecnici e anzianità del backup non equivalgono a RTO/RPO di produzione.
