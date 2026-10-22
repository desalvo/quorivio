# Worker isolato per le conversioni PDF/PPTX

Quorivio esegue la conversione esclusivamente nel container **converter** (`Dockerfile.converter`), mai nel processo API. I processi si scambiano file mediante un volume temporaneo privato e richiedono un token interno `QUORIVIO_WORKER_TOKEN` di almeno 32 caratteri. Il worker espone la porta 8099 solo nella rete privata dello stack; il pod Helm usa `127.0.0.1`. Il servizio usa utente non privilegiato, filesystem di base in sola lettura e limiti CPU/memoria nei deployment.

## Compose
Generare una chiave casuale forte per `QUORIVIO_WORKER_TOKEN` (ad es. `openssl rand -hex 32`) e inserirla nel file d'ambiente dello stack. Compose gestisce il container converter e il volume temporaneo. Non pubblicare la porta 8099.

## Helm
Predisporre `QUORIVIO_WORKER_TOKEN` nel Secret indicato da `existingSecret`. Il sidecar e l'API condividono un `emptyDir` a durata del pod; il container converter necessita anche del mount `/tmp`. Configurare risorse adeguate ai documenti caricati.

## Stato e limiti
Test Python del protocollo e del percorso superati, nessun collaudo del worker Compose/Helm reale; i binari PDF/PPTX devono essere provati nel container su file concreti. Il worker non preserva le animazioni; il volume temporaneo deve essere monitorato e protetto. Non dichiarare pronto per la produzione senza collaudi end-to-end, migrazioni PostgreSQL e controlli di isolamento dei container.
