# Quorivio 0.1.0-dev RC262 — spazio disco e notifiche amministratori

## Misure e limiti

La misura del volume temporaneo `emptyDir` legge il **filesystem sottostante**, non la quota `emptyDir.sizeLimit` imposta da kubelet: esaurimenti di tale quota possono verificarsi anche sotto il 90% del filesystem; usare anche le metriche kubelet per la quota. Con più repliche, gli alert del volume temporaneo sono deduplicati **per pod**, perché il volume non è condiviso.

La sezione **Configurazione server → Spazio disco e allarmi**, visibile agli amministratori di piattaforma, visualizza le capacità **fisiche dei filesystem** tramite `statfs` del container API per `/app/assets` e `/conversions`. Se le conversioni sono disabilitate e il relativo volume non è montato, la misura è **non disponibile**, non 0%.

PostgreSQL gira su un pod/PVC distinto. `pg_database_size()` misura solo i dati logici e **non** include tutto lo spazio del filesystem (WAL, altri database e overhead). La percentuale PostgreSQL proviene perciò esclusivamente da una sonda **read-only** nello stesso pod dello StatefulSet. La sonda usa `df -Pk /var/lib/postgresql` e, mediante `psql` su localhost, aggiorna `disk_monitor_samples` ogni 5 minuti. Non espone porte, API pubbliche, password in chiaro nei manifest, token di service account né privilegi Kubernetes. Il database è misurato correttamente anche se un pod API risiede su un altro nodo. Un campione oltre 15 minuti è segnalato come **non disponibile** e non provoca allarmi.

Il sistema verifica tutte e tre le misure ogni 5 minuti. A partire dal **90%** per ciascun volume, invia una sola email ai soli `platform_admin` approvati tramite l'SMTP/SMTPS già configurato. Il monitor torna a essere notificabile dopo una misura **≤85%**, prevenendo notifiche ripetute intorno alla soglia. Lo stato è serializzato con `SELECT ... FOR UPDATE` sul database, funzionando anche con più repliche API. La consegna SMTP fallita viene ritentata e non viene registrata come riuscita. In caso di crash durante la transazione immediatamente dopo la consegna email è possibile una ripetizione: nessun protocollo SMTP garantisce un'esecuzione exactly-once. Senza SMTP o destinatari approvati, la situazione resta visibile e si ritenta, ma non si finge di aver spedito una mail.

## Nuova installazione Kubernetes

La generazione tramite wizard RC262 include già il sidecar `db-disk-probe` **solo per PostgreSQL interno gestito dal wizard**. È necessario utilizzare una nuova immagine applicativa RC262 con le tabelle `disk_monitor_samples` e `disk_monitor_alert_state`, create automaticamente all'avvio. Il sidecar usa il medesimo Secret PostgreSQL già esistente. Per database esterni, installare un collettore di filesystem equivalente lato operatore o accettare lo stato "non disponibile"; la dimensione logica non viene mai presentata come uso percentuale del PVC.

## Attivazione su Kubernetes già esistente

**Attenzione:** aggiungere un container al pod PostgreSQL ne comporta il **riavvio** durante il rollout dello StatefulSet, con possibile disservizio su una singola replica. Prima di applicare: controllare backup/restauro, finestra di manutenzione, capacità di storage, e aggiornare l'immagine dell'applicazione alla RC262. Non è un'operazione a disponibilità garantita.

Dalla directory che contiene `k8s-generated` e il wizard standalone RC262:

```bash
python3 k8s_wizard.py --version
python3 k8s_wizard.py --plan-disk-monitor \
  --generated-dir ./k8s-generated \
  --set namespace=quorivio --set name=quorivio \
  --output ./disk-monitor-plan-rc262
cat ./disk-monitor-plan-rc262/disk-monitor-plan.json
kubectl -n quorivio patch statefulset quorivio-postgres --type=json \
  --patch-file=./disk-monitor-plan-rc262/disk-monitor-json-patch.json \
  --dry-run=server -o name
# SOLO dopo revisione del piano e finestra di manutenzione:
python3 k8s_wizard.py --apply-disk-monitor --acknowledge-db-restart \
  --output ./disk-monitor-plan-rc262
kubectl -n quorivio rollout status statefulset/quorivio-postgres
kubectl -n quorivio logs statefulset/quorivio-postgres -c db-disk-probe --since=10m
kubectl kustomize ./k8s-generated > /dev/null
```

L'ultima fase aggiunge l'overlay Kustomize `97-postgres-disk-probe-patch.json` e il relativo riferimento in `kustomization.yaml`, con backup privato dei manifest precedenti. Se lo StatefulSet viene modificato tra piano e applicazione il comando è bloccato. Se la sonda è già installata, utilizzare l'operazione **solo lettura Kubernetes**:

```bash
python3 k8s_wizard.py --sync-disk-monitor \
  --generated-dir ./k8s-generated \
  --set namespace=quorivio --set name=quorivio
```

`--sync-disk-monitor` non aggiorna il cluster, ma verifica la configurazione live della sonda e aggiorna `k8s-generated`. Il wizard continua a essere un singolo file Python auto-aggiornante, senza dipendenze Quorivio ulteriori, e la modalità esplicitamente offline è `--no-self-update`.

## Diagnostica

Verificare **Configurazione server → SMTP/SMTPS**, destinatari amministratori approvati, gli indicatori disco e l'ora della misura. La schermata e gli endpoint privati non mostrano password né percorsi dei documenti. Nel database, le righe `disk_monitor_samples` e `disk_monitor_alert_state` contengono solo capacità, timestamp e stato di notifica. Una sonda assente, un DB esterno senza probe o un problema di collegamento sono stati **non disponibili**, non una misura sana. Non abilitare mail sulla sola `pg_database_size()`.

La full CI GitHub rimane obbligatoria prima della release. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
