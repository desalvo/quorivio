# Kubernetes HA e aggiornamenti sicuri — ciclo RC 23

Il wizard ora configura `maxUnavailable: 0` e `maxSurge: 1` per il Deployment applicativo. Con **2–20 repliche** e storage RWX genera un PodDisruptionBudget `policy/v1` con `minAvailable=repliche-1` e una distribuzione preferenziale (non obbligatoria) dei pod per hostname. Con una replica il PDB è assente e quello precedente viene rimosso in fase di rigenerazione. Queste impostazioni limitano le interruzioni volontarie; non garantiscono HA senza nodi indipendenti e storage affidabile.

## Credenziali

`05-app-secret.yaml` e `quorivio-overrides.json` sono sostituiti atomicamente, con permessi `0600` e rifiuto dei symlink o dei file non regolari. Le credenziali generate rimangono persistenti tra invocazioni. Non utilizzare cartelle condivise non attendibili, custodire le copie delle credenziali e non aggiungere i file a Git.

`--set replicas=3 --set asset_access_mode=ReadWriteMany --set max_upload_mb=150` interpreta correttamente i campi numerici. Con più repliche è obbligatorio un volume RWX effettivamente supportato dalla StorageClass.

## Terminazione controllata

Su `SIGTERM`, il servizio restituisce HTTP 503 (`status=draining`) alla readiness e chiude i WebSocket con codice `1012` (`service_restart`); dopo un breve intervallo arresta HTTP. La finestra di terminazione Kubernetes è di 45 secondi. Le altre repliche devono accettare nuove connessioni preservando i voti già registrati in PostgreSQL. La prova su database reale è ancora in attesa della nuova CI; non si tratta di un SLO di produzione.

## Accettazione

La CI standard include un test SIGTERM con PostgreSQL e due processi reali, dopo il test opzionale di carico. Il nuovo job KIND **manuale**, `kubernetes_manifest_test=true`, verifica con `kubectl apply --dry-run=server` quattro varianti NGINX/HAProxy, TLS, PostgreSQL interno/esterno e RWX. Controlla solo le API e lo schema Kubernetes; non certifica routing ingress, RWX reale, ClamAV, scheduling su più nodi o HA di produzione. Il parametro separato `runtime_arch_test=true` prova OCI AMD64/ARM64 con QEMU.

Le nuove prove non sono ancora state eseguite su GitHub. Per accettare D3 e B1 sono ancora indispensabili un cluster di staging reale, RWX, ingress e TLS configurati, fault injection e un collaudo con responsabile operativo. Non pubblicare immagini durante le prove.
