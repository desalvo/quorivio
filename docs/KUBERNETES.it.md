# Wizard Kubernetes con Kustomize

Esecuzione unattended, dalla root del progetto:

```bash
python3 tools/k8s_wizard.py --unattended --output ./k8s-generated --set host=quorivio.example.org --set image=desalvo/quorivio:v0.1.0
kubectl kustomize ./k8s-generated
```

Esecuzione interattiva: `python3 tools/k8s_wizard.py --output ./k8s-generated`. Vengono mostrati i default e i valori precedentemente personalizzati. Con gli stessi parametri si generano **gli stessi manifest**. Il file `quorivio-overrides.json` memorizza solo i valori diversi dai default, senza password. `--values path/to/quorivio-overrides.json` importa le personalizzazioni. Sono generati Namespace, ConfigMap, Deployment, Service, Ingress e Kustomization. Non viene eseguito alcun deploy.

**Precondizioni**: PostgreSQL esterno, Secret Kubernetes `quorivio-app-secrets` con `DATABASE_URL` e `AUTH_SECRET` (verificare i nomi effettivi delle variabili), e Secret TLS `quorivio-tls` oppure cert-manager. Verificare WebSocket nell'ingress, DNS e HTTPS. Attualmente i WebSocket usano broadcast locale: limitare `replicas=1` fino all'introduzione di Redis/pubsub. Kubernetes e limiti risorse devono ancora essere verificati in un cluster reale.

## Estensioni PostgreSQL 18 e ingress (terzo ciclo)

Il wizard propone PostgreSQL interno `postgres:18.6-alpine`, StatefulSet e PVC da 10 GiB montato in `/var/lib/postgresql` (layout PostgreSQL 18+). Un volume PG17 **non si aggiorna** cambiando immagine: eseguire una migrazione major supportata con backup/ripristino o `pg_upgrade`, previa verifica.

```sh
python3 tools/k8s_wizard.py --unattended --output ./generated --set ingress_controller=haproxy --set haproxy_variant=community
python3 tools/k8s_wizard.py --unattended --output ./external --set postgres_mode=external --set postgres_host=pg.example.org --set postgres_sslmode=verify-full
```

`haproxy_variant=community` aggiunge l'annotazione legacy `kubernetes.io/ingress.class`; `haproxy_variant=haproxytech` usa `haproxy.org/ingress.class`. In entrambi i casi si imposta `spec.ingressClassName`. Verificare la variante controller effettiva. NGINX usa per default `ingressClassName: nginx`.

Il wizard **non salva credenziali**. Preparare un Secret con `DATABASE_URL` e `AUTH_SECRET`; PostgreSQL interno richiede anche `POSTGRES_PASSWORD`. L'URL deve usare l'escaping corretto, un adeguato `sslmode` e CA attendibili per database esterni. `PGSSLMODE` nella ConfigMap *non sostituisce* la corretta configurazione TLS di `DATABASE_URL`. Lo StatefulSet generato non offre ancora backup gestiti né alta disponibilità; configurarli e testarli prima della produzione. L'API deve restare a una replica finché non è implementata la sincronizzazione degli eventi tra repliche.

Usare `kubectl kustomize ./generated` e validare sul cluster: wizard e chart Helm non sono ancora stati verificati in un cluster reale.


## RC246 — Aggiornare senza reinstallare (worker PDF/PPTX)

Per una installazione già generata con il wizard, **non** rigenerare o applicare tutti i vecchi manifest: usare invece `python3 tools/k8s_wizard.py --ensure-converter-token`, poi `--upgrade-converter` per ottenere una patch mirata sul Deployment vivo e infine `--apply-converter` per applicarla esplicitamente dopo la revisione. L'immagine del worker deve essere pubblicata separatamente con il workflow manuale `.github/workflows/converter-image.yml` oppure con `docker buildx`. Il wizard non cambia PostgreSQL/PVC/Ingress/Service/credenziali e rifiuta di applicare piani scaduti. Procedura completa: `docs/RC_CYCLE246_EXISTING_K8S_CONVERTER_UPGRADE.it.md`.

## RC247 — Tag immagine worker

Eseguire manualmente il workflow di pubblicazione converter su `main` con `confirm_publish=true` per ottenere `desalvo/quorivio-converter:latest`; eseguirlo sul tag Git per ottenere `desalvo/quorivio-converter:<nome-tag>`. Il wizard di aggiornamento live accetta `latest`, tag release oppure un digest e non re-installa database/PVC/Ingress. Il tag `latest` è mobile: verificare il digest prima del rollout. Nessun aggiornamento del cluster è automatico.
