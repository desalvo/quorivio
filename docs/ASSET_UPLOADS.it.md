# Allegati delle sessioni — stato di sviluppo

Versione: 0.1.0-dev. Il nuovo endpoint `POST /api/sessions/:id/assets` riceve **byte binari grezzi** (non multipart) con `Content-Type` e `Content-Length` esatto. Servono autenticazione, ruolo presentatore approvato e autorizzazione sulla sessione. Esempio:

```sh
curl -b cookies.txt --data-binary @slide.pdf -H 'Content-Type: application/pdf' \
  https://quorivio.example/api/sessions/SESSION_ID/assets
```

La risposta fornisce `id` e URL di recupero per presentatori autenticati (`GET /api/sessions/:id/assets/:assetId`). Sono verificate le firme dei file; formati ammessi PNG, JPEG, GIF, WebP, PDF, MP4 e WebM. L'impostazione `max_upload_mb` prevede 100 MB di default, massimo 1024 MB. L'Ingress deve applicare un limite coerente, come generato dal wizard Kubernetes. I byte sono salvati sotto `QUORIVIO_ASSET_DIR` (volume persistente Compose `asset-data`), con metadati e SHA-256 in PostgreSQL.

**Non pronto per produzione:** questa prima implementazione carica i file in memoria, non integra antivirus, sanitizzazione, distribuzione ai partecipanti, eliminazione dei file dopo rimozione dei record, quote o storage condiviso S3. I manifest Kubernetes non includono ancora lo storage condiviso per gli asset. Il controllo della firma non rende un file automaticamente sicuro. Non usare più repliche prima dello storage condiviso e del coordinamento eventi. Un backup completo richiede sia PostgreSQL sia i file binari.
