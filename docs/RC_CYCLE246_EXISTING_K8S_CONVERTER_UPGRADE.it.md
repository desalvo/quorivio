# RC246 — Aggiungere il worker PDF/PPTX al cluster Kubernetes esistente senza reinstallare Quorivio

**Baseline:** Quorivio RC245, commit `c108694705d2bd0d8d8444f7840a944b5913e25d`, full CI GitHub [42382296263](https://github.com/desalvo/quorivio/actions/runs/42382296263) **14 job riusciti, 11/11 gate obbligatori**; pubblicazione multiarch dell'immagine *principale* [42385404670](https://github.com/desalvo/quorivio/actions/runs/42385404670) OK (`desalvo/quorivio:sha-c108694705d2`, `:latest`). **L'immagine converter non viene pubblicata insieme a quella principale**: costruirla/pubblicarla separatamente prima dell'aggiornamento. RC246 non è ancora certificata su GitHub.

## Modalità aggiuntive del wizard `tools/k8s_wizard.py`

La modalità storica di nuova installazione Kustomize resta invariata. Le nuove modalità **leggono il Deployment Kubernetes effettivo** con `kubectl`, non tentano di ricalcolarlo dai vecchi default o dal file di override; non rigenerano Namespace, Secret applicativi, PostgreSQL/StatefulSet, PVC, ConfigMap, Service, Ingress o certificati. Il wizard non accede direttamente a cluster remoti da ChatGPT: i comandi seguenti si eseguono dalla macchina dell'operatore con `kubectl` configurato.

### 0. Verificare il contesto e predisporre l'immagine converter

```bash
kubectl config current-context
kubectl -n quorivio get deployment quorivio
kubectl -n quorivio get pods
```

**Opzione A:** su GitHub Actions, eseguire manualmente il nuovo workflow **Publish Quorivio PDF/PPTX converter (manual only)** (`.github/workflows/converter-image.yml`) su `main`, selezionare `confirm_publish=true` e, volendo, `publish_tag=0.1.0-dev`. Il workflow autentica su Docker Hub con le variabili già previste (`vars.DOCKERHUB_USERNAME` e `secrets.DOCKERHUB_TOKEN`), costruisce amd64/arm64 da `Dockerfile.converter`, pubblica `desalvo/quorivio-converter:sha-<12 caratteri del commit>` e il tag aggiuntivo richiesto, quindi verifica entrambi i manifest. **Non viene avviato automaticamente da push o pull request**. Eseguire solo dopo la CI verde della nuova revisione.

**Opzione B:** da workstation con Docker Buildx e permessi sul registry:

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
  -f Dockerfile.converter \
  -t IL_TUO_REGISTRY/quorivio-converter:rc246 \
  --push .
docker buildx imagetools inspect IL_TUO_REGISTRY/quorivio-converter:rc246
```

Il manifest deve contenere le architetture realmente utilizzate dal cluster. Non impostare l'immagine dell'API (`desalvo/quorivio`) come worker: è un container diverso.

### 1. Preparare una sola volta il token interno, SENZA modificare altre credenziali

```bash
python3 tools/k8s_wizard.py --ensure-converter-token \
  --set namespace=quorivio --set name=quorivio
```

L'operazione cerca il Secret già usato dalla API per `DATABASE_URL`/`AUTH_SECRET` o in `envFrom`, e aggiunge **solo se assente** `QUORIVIO_WORKER_TOKEN` (valore casuale generato con `secrets.token_hex(32)`) in modo atomico, con controllo `resourceVersion`. Il token non è stampato, non appare in argomenti della shell, non viene scritto su disco o nel repository. Se il Secret è immutabile, ha un token non valido oppure il riferimento è ambiguo, l'operazione fallisce senza sostituire altre chiavi. Per usare un Secret diverso aggiungere `--converter-secret NOME_SECRET` e assicurarsi che sia nello stesso namespace. **Questa è l'unica fase che modifica il Secret e richiede un comando esplicito.**

### 2. Generare una patch di anteprima non distruttiva

```bash
python3 tools/k8s_wizard.py --upgrade-converter \
  --set namespace=quorivio --set name=quorivio \
  --converter-image desalvo/quorivio-converter:sha-IL_SHA \
  --output ./converter-upgrade-rc246
```

Il percorso `--output` deve essere **nuovo e vuoto, diverso da `k8s-generated`**. Se il Deployment reale ha un nome diverso, usare `--converter-deployment NOME`; se il container API ha un nome non standard, usare `--app-container NOME`; per il Secret, `--converter-secret NOME`. I file creati con permessi privati sono:

- `converter-plan.json`: cluster context, namespace, Deployment, UID, resourceVersion, app container, Secret e SHA-256 della patch; **nessuna credenziale**.
- `converter-patch.json`: JSON Patch RFC6902, con precondizioni atomiche su UID/resourceVersion, e **solo** aggiunte al pod: sidecar converter, `emptyDir` `/conversions` e `/tmp`, mount sull'API, URL locale, abilitazione converter e token tramite `secretKeyRef`.
- `LEGGIMI.txt`: comandi di dry-run e applicazione.

Le risorse già configurate, le variabili in conflitto, l'immagine senza tag/digest, l'assenza di `fsGroup` o un Deployment Helm-managed fanno fallire la preparazione invece di essere sovrascritti. La patch è generata a partire dal Deployment esistente, conservando repliche, immagini API, Secret, PVC, configmap, ingress e politica di rollout.

### 3. Verificare e applicare SOLO la modifica intenzionale

Prima di applicare, leggere i due JSON; il piano non contiene Secret né password. È possibile effettuare un dry-run server-side:

```bash
kubectl -n quorivio patch deployment quorivio \
  --type=json --patch-file=./converter-upgrade-rc246/converter-patch.json \
  --dry-run=server -o name
```

Applicare con il comando separato:

```bash
python3 tools/k8s_wizard.py --apply-converter \
  --output ./converter-upgrade-rc246
```

**Prima di modificare il cluster**, il wizard controlla nuovamente contesto, UID e resourceVersion del Deployment, Secret/token e SHA-256 del piano, ricostruisce indipendentemente le sole operazioni consentite, prova il dry-run server-side, applica una sola patch atomica e attende il rollout. Se è intervenuta una modifica nel Deployment, rifiuta l'applicazione: **rigenerare il piano in una nuova directory**. Non tocca database, StatefulSet, StorageClass, PVC, Service, Ingress, TLS, né sostituisce le credenziali. In caso di errore del rollout, esaminare i nuovi pod senza eliminare quelli precedenti e, se necessario, usare `kubectl -n quorivio rollout undo deployment/quorivio` con il controllo dell'operatore.

### 4. Collaudo e attivazione Quorivio

```bash
kubectl -n quorivio rollout status deployment/quorivio
kubectl -n quorivio get pods
kubectl -n quorivio logs deployment/quorivio -c converter --tail=80
```

Dopo il rollout: **Amministratore piattaforma → Configurazione server → Convertitore PDF / PowerPoint (worker isolato) → Verifica stato worker → Abilita importazione PDF/PPTX**. Il pannello non crea il pod: abilita il flag persistente soltanto dopo che worker e configurazione sono operativi. Provare file PDF/PPTX reali (immagini e import parzialmente modificabile), controllare le opzioni e la conservazione delle sessioni precedenti. Il worker espone `8099` **solo dentro il pod** (`127.0.0.1:8099`); il volume `/conversions` è `emptyDir` **per pod**, non è un PVC condiviso tra nodi. La API e il converter dello stesso pod condividono la directory; non attivare un Service o Ingress pubblico per il converter. Il worker è eseguito come UID 1000, con root filesystem read-only, limiti CPU/memoria e `/tmp` su `emptyDir`.

### Requisiti di accettazione

RC246 aggiunge test preventivi di non-distruzione e precondizioni Kubernetes, ma **non prova il cluster di produzione né la disponibilità delle immagini**. Quorivio resta `0.1.0-dev`, punteggio certificato **85,25% (43 accettati/17 parziali)**; mantenere `rc_strict=false` e non dichiarare i gate C4/D3 o la RC conclusi senza verifica esterna dei nodi e dello storage. Nessun commit/push/tag o pubblicazione da parte dell'assistente.
