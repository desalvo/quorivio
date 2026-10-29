# Replica dei backup cifrati su filesystem montato — Quorivio 0.1.0-dev, ciclo RC 21

Questo componente effettua una **replica tecnica con verifica di recuperabilità**, non costituisce automaticamente una copia offsite indipendente, un servizio DR completo né una garanzia RPO/RTO. L'operatore deve predisporre uno storage separato fisicamente, credenziali e custodia delle chiavi indipendenti, monitoraggio, conservazione e procedura di ripristino verificata.

`tools/backup_mirror.py` trasferisce **soltanto gli archivi cifrati AES-256-GCM `.qenc`** in una directory esistente, privata (0700), su un filesystem già montato. Se il mount non è presente, rifiuta la copia per evitare di scrivere per errore sul filesystem locale sottostante. Non monta NFS né gestisce servizi cloud automaticamente. `--mount-root` deve essere un punto di mount reale diverso da `/` e contenere la directory di destinazione. `--work-dir` deve trovarsi su filesystem **cifrato** gestito dall'operatore, con permessi 0700: la verifica decifra temporaneamente **solo in tale area**, mai sul volume di replica. La rimozione dei temporanei non è cancellazione sicura su SSD/COW. Le chiavi non vengono copiate sul volume.

L'archivio sorgente e le chiavi devono essere file regolari privati 0600, dell'utente corrente. Non sono consentite sovrascritture. La copia viene predisposta, autenticata con AES-GCM, verificata nel contenuto e confrontata tramite SHA-256 prima della pubblicazione atomica, con ricevuta JSON privata e priva di segreti. `verify` controlla nuovamente checksum, autenticazione e manifest; la ricevuta non è una firma dell'identità dell'operatore.

```sh
# Montare prima, in modo indipendente, /mnt/backup-remoto.
# mkdir -m 700 /mnt/backup-remoto/quorivio
python3 tools/backup_mirror.py push \
  --source /backup-privati/snapshot.qenc \
  --directory /mnt/backup-remoto/quorivio \
  --mount-root /mnt/backup-remoto \
  --key-file /chiavi-private/backup-attuale.key \
  --work-dir /spool-cifrato/quorivio
python3 tools/backup_mirror.py verify \
  --name snapshot.qenc \
  --directory /mnt/backup-remoto/quorivio \
  --mount-root /mnt/backup-remoto \
  --key-file /chiavi-private/backup-attuale.key \
  --work-dir /spool-cifrato/quorivio
```

Per un **ripristino reale** eseguire `tools/secure_instance_backup.py drill` sull'archivio replicato, verso un database PostgreSQL isolato e vuoto e una directory degli asset vuota. Consultare `DR_REHEARSAL_AND_RETENTION.it.md` per ricevuta, tempi misurati e anzianità del backup. Misurare separatamente **perdita reale delle scritture, predisposizione infrastrutturale, commutazione dei client e disponibilità applicativa**. Nessuna pianificazione automatica, gestione dei provider o cancellazione degli archivi viene abilitata.

La Full CI prova il trasferimento su un tmpfs `/dev/shm` montato e il ripristino su un **quarto database PostgreSQL 18 temporaneo**, confrontando schema, righe e asset. Questa prova NON dimostra indipendenza offsite, guasti di rete NFS/cloud, conformità normativa, RPO/RTO di produzione o approvazione operativa. I gate RC D2/D6 rimangono parziali fino a nuova CI verde e collaudo indipendente.
