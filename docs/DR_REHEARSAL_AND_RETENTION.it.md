# Collaudo disaster recovery e conservazione dei backup cifrati

**Quorivio 0.1.0-dev — ciclo 19, 29 ottobre 2026.** Questa procedura tecnica non è una certificazione di RPO/RTO di produzione, GDPR o approvazione indipendente del disaster recovery.

## Requisiti e limiti di sicurezza

Installare la libreria Python cryptography e il client PostgreSQL 18. Prima del backup fermare i processi che scrivono dati. **Non ripristinare in un database popolato**: creare una nuova banca dati vuota e una directory degli asset vuota, senza collegamenti simbolici. La directory `--work-dir` deve avere permessi **0700 ed essere collocata su un filesystem cifrato**. Durante la verifica/ripristino possono esistere file temporanei in chiaro in questa directory protetta: vengono eliminati al termine, ma la cancellazione fisica su SSD, snapshot e filesystem copy-on-write non è garantita. Le chiavi devono restare separate, protette (0600) e mai pubblicate nel repository.

## Collaudo effettivo del ripristino

Dopo aver creato un backup cifrato e, se necessario, ruotato la chiave:

```sh
export DATABASE_URL='postgres://<operatore>:<password>@<host-ripristino-isolato>:5432/quorivio_dr_drill'
python3 tools/secure_instance_backup.py drill \
  --input /backup-privati/quorivio-2026-10.qenc \
  --assets /ripristino/asset-vuoti \
  --key-file /chiavi-private/quorivio-2026-10.key \
  --work-dir /volume-cifrato/quorivio-work \
  --receipt /report-privati/quorivio-dr-receipt.json \
  --max-backup-age-seconds 86400 \
  --max-restore-seconds 3600 \
  --confirm RESTORE-QUORIVIO-DATA
```

Il comando autentica e verifica l'archivio prima del ripristino e blocca gli archivi troppo vecchi se la soglia è impostata. Non sovrascrive ricevute esistenti. La ricevuta JSON con permessi 0600 registra anzianità, durata del comando, numero di oggetti controllati ed esito delle soglie, **senza credenziali, URL del database, chiavi, percorsi degli asset o dati personali degli utenti**. Se il ripristino supera la soglia temporale, i dati sono **già stati ripristinati**: il comando segnala il mancato rispetto della soglia e conserva la ricevuta, ma **non effettua rollback**.

L'età del backup è soltanto un indicatore di freschezza, **non** la perdita reale dei dati (RPO). La durata di questo comando **non è** l'RTO completo: esclude provisioning dell'infrastruttura, switch dei servizi, DNS, failover, verifiche utenti e perdita di scritture. Sono necessarie misurazioni indipendenti su dati rappresentativi e un'approvazione operativa prima di accettare il gate D2.

## Conservazione autenticata e blocchi legali (ciclo 20)

**Modifica intenzionale della procedura:** l'opzione `--apply`, anche con conferma esplicita, **richiede** ora un registro privato dei blocchi di cancellazione, tutte le generazioni di chiavi necessarie e una directory di lavoro protetta. Il vecchio comando con i soli `--apply --confirm ...` viene rifiutato. Il registro è un JSON 0600 gestito dall'operatore, per esempio:

```json
{"version":1,"hold":["quorivio-vincolo-legale-2026.qenc"]}
```

Ogni nome deve riferirsi a un archivio `.qenc` presente nella directory privata 0700. Record inesistenti, non validi o link simbolici bloccano il comando. **Un registro vuoto non dimostra l'assenza di vincoli legali.** Occorre comunque verificare le procedure dell'organizzazione e le copie offsite. Gli archivi soggetti a blocco non vengono conteggiati nel minimo `--min-keep` delle altre copie.

```sh
# Simulazione senza cancellazione, non richiede le chiavi:
python3 tools/backup_retention.py --directory /backup-privati --days 30 --min-keep 3 \
  --holds-file /chiavi-private/quorivio-vincoli.json
# Applicazione: verifica prima l'autenticità di TUTTI gli archivi e dei manifest
# interni, includendo tutte le generazioni di chiavi ruotate.
python3 tools/backup_retention.py --directory /backup-privati --days 30 --min-keep 3 \
  --holds-file /chiavi-private/quorivio-vincoli.json \
  --key-file /chiavi-private/quorivio-2026.key \
  --key-file /chiavi-private/quorivio-ruotata.key \
  --work-dir /lavoro-cifrato/quorivio \
  --apply --confirm PRUNE-QUORIVIO-ENCRYPTED-BACKUPS
```

La pre-verifica autentica **tutti** gli archivi, anche quelli destinati alla cancellazione: se una copia recente è corrotta, il comando non elimina quella precedente. Dopo la verifica controlla nuovamente le identità dei file e il registro dei blocchi, rifiutando modifiche concorrenti. La directory `--work-dir` deve essere 0700 su filesystem cifrato: durante la verifica possono esistere temporaneamente file decifrati, rimossi al termine (senza garanzia di cancellazione fisica SSD). Nessuna pianificazione o cancellazione automatica viene attivata su Kubernetes. I timestamp dei file non certificano RPO, recuperabilità né copie offsite. D2/D6 richiedono ancora collaudo e approvazione indipendente.

## Accettazione CI

La CI PostgreSQL 18 ripristinerà un ulteriore database temporaneo indipendente da un archivio cifrato con chiave ruotata, confrontando schema, righe e asset. Pubblicherà una ricevuta tecnica priva di segreti (`dr-rehearsal-ci-only`) e non attribuirà un RPO/RTO di produzione. La nuova revisione richiede ancora Full CI verde e collaudo indipendente dei gate D2/D6.
