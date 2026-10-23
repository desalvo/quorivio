# Deployment Kubernetes di test — Quorivio 0.1.0-dev

## Nome immagine e CI
L'immagine applicativa ufficiale di default è **`desalvo/quorivio:latest`** in Compose, wizard Kubernetes, Helm e pubblicazione GitHub Actions. Il repository sorgente è `desalvo/quorivio`. Il cambio rispetto al precedente nome richiede un nuovo commit/push **a cura del manutentore**, il superamento della CI e la disponibilità della nuova immagine su Docker Hub **prima** del deployment. Il converter, se pubblicato separatamente, usa `desalvo/quorivio-converter:0.1.0-dev`: il cambio del nome non garantisce la presenza dell'immagine sul registry; verificarla prima di usare Helm.

## Wizard Kustomize
Esempio, con TLS terminato dall'Ingress usando il suo certificato di default:

```sh
python3 tools/k8s_wizard.py --unattended --output ./k8s-generated \
  --set host=quorivio.example.org --set ingress_controller=nginx \
  --set tls_termination=true --set tls_secret= \
  --set app_node_selector=kubernetes.io/arch=amd64,disktype=ssd \
  --set postgres_node_selector=disktype=hdd
kubectl kustomize ./k8s-generated
```

`tls_termination=true` emette `spec.tls` con gli host. Se `tls_secret` è vuoto, non emette `secretName`: **deve essere già configurato un certificato di default nell'Ingress controller**; il wizard non crea certificati. Impostare `tls_secret=mio-cert` se si usa un Secret TLS specifico. `tls_termination=false` omette `spec.tls` del tutto. Le configurazioni salvate in `quorivio-overrides.json` vengono riutilizzate: `--set tls_secret=` cancella il valore precedente. I selector sono espressi come coppie `chiave=valore` separate da virgole, e si applicano separatamente al Deployment applicativo e allo StatefulSet PostgreSQL interno. In modalità database esterno non viene creato lo StatefulSet.

Per installare, preparare prima i Kubernetes Secrets previsti dalla configurazione dell'applicazione e, se il DB è interno, le credenziali PostgreSQL coerenti; non includere password nei manifest o nel repository. Controllare PVC, StorageClass, architettura delle immagini e IngressClass prima di eseguire `kubectl apply -k ./k8s-generated`. Eseguire lo smoke test su una nuova installazione di prova, mai su un database di produzione. Kubernetes, PostgreSQL, TLS reale e pull delle immagini sono ancora da collaudare esternamente.

## Helm
`helm/quorivio/values.yaml` usa il default `desalvo/quorivio:latest` e `ingress.tlsTermination=true`, `ingress.tlsSecret=""`. Per i pod del chart (applicazione, converter e ClamAV nello **stesso pod**) usare `nodeSelector`; un selector per ogni container dello stesso pod non è possibile in Kubernetes. Verificare la presenza dell'immagine converter prima dell'installazione.
