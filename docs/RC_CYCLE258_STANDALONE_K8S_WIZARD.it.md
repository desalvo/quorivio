# RC258 — Wizard Kubernetes standalone e sicurezza del rollout del converter

**Base cumulativa:** RC257 (non modificare il lavoro sui font Arial e sui controlli storici RC193). **Origine dell'incidente:** il comando `--upgrade-converter` rifiutava il valore Kubernetes predefinito `maxUnavailable: 25%` senza tener conto delle repliche. Kubernetes arrotonda *per difetto* `maxUnavailable` percentuale e *per eccesso* `maxSurge`. Con 1, 2 o 3 repliche, 25% corrisponde a zero pod indisponibili; con 4 repliche corrisponde a un pod e resta bloccato. Valori espliciti che consentono indisponibilità, `Recreate`, configurazioni invalide o rollout fermo sono tuttora rifiutati.

## Un unico file da copiare sul nodo amministrativo

Il solo file `tools/k8s_wizard.py` contiene ora, in chiaro e con SHA-256 verificato, le funzionalità complete di `k8s_converter_upgrade` e `k8s_cluster_inspection`. **Non occorre scaricare il repository, né moduli Python aggiuntivi o template YAML**. Servono Python 3 con libreria standard e, per le operazioni sul cluster, un `kubectl` già installato, configurato e autorizzato. La generazione della configurazione per una nuova installazione non richiede `kubectl`; per applicarla serve `kubectl apply -k`.

```bash
# Sul nodo: dopo aver copiato solo k8s_wizard.py
python3 ./k8s_wizard.py --help

# Nuova installazione: scrive i manifest Kustomize, NON applica alcuna risorsa
python3 ./k8s_wizard.py --unattended --set host=quorivio.example.org \
  --output ./quorivio-new-install
kubectl apply -k ./quorivio-new-install  # solo dopo controllo di Secret e manifest

# Installazione ESISTENTE: inventario a sola lettura, non ricrea Secret/DB/PVC
python3 ./k8s_wizard.py --inspect-cluster \
  --set namespace=quorivio --set name=quorivio \
  --output ./quorivio-inventory

# Prima autorizzare SOLO l'aggiunta del token al Secret già in uso
python3 ./k8s_wizard.py --ensure-converter-token \
  --set namespace=quorivio --set name=quorivio

# Generare piano e patch senza modificare il Deployment
python3 ./k8s_wizard.py --upgrade-converter \
  --set namespace=quorivio --set name=quorivio \
  --converter-image 'desalvo/quorivio-converter@sha256:95223a548ca5e813199216e80ce565c6a203c6b6105c8655e8d62048e94d74f7' \
  --output ./converter-upgrade-rc258

# Leggere converter-plan.json e converter-patch.json, quindi dry-run server
kubectl -n quorivio patch deployment quorivio --type=json \
  --patch-file=./converter-upgrade-rc258/converter-patch.json --dry-run=server -o name

# Applicazione esplicita del piano già verificato: senza altri --set
python3 ./k8s_wizard.py --apply-converter --output ./converter-upgrade-rc258
kubectl -n quorivio rollout status deployment/quorivio
kubectl -n quorivio logs deployment/quorivio -c converter --tail=80
```

Il converter è un **sidecar** nello stesso pod: endpoint privato `127.0.0.1:8099`, volume temporaneo `emptyDir` montato in `/conversions`, Secret `QUORIVIO_WORKER_TOKEN` referenziato senza stamparne il valore. Si mantengono intatti: PostgreSQL, volume dati applicativo, PVC, Ingress, Service e configurazione delle altre variabili. Il wizard protegge il piano mediante contesto Kubernetes, UID e `resourceVersion`; una modifica concorrente obbliga a rigenerare il piano. **Non aggirare il blocco Helm**: per Deployment Helm usare l'upgrade del chart.

**Importante:** `--inspect-cluster` e `--upgrade-converter` non sono un aggiornamento generalizzato di tutti i componenti dell'installazione; un eventuale aggiornamento dell'app o del database resta soggetto alla normale procedura e ai backup del cluster. Il wizard standalone genera una nuova base e aggiunge il converter in sicurezza a un Deployment esistente.

**Validazione locale:** test con una sola copia del wizard, ambiente senza altri file Quorivio e `kubectl` fittizio; generazione, ispezione, token, piano, applicazione; casi percentuali 1–4+ repliche; test di compatibilità, CI preflight e ricevute SHA-256. Nessuna connessione o modifica a un cluster reale effettuata. Full CI RC258 da confermare.
