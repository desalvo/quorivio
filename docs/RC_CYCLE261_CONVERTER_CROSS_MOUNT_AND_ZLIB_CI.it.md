# Quorivio 0.1.0-dev — RC261 — PDF/PPTX su Kubernetes e aggiornamenti di sicurezza

**Stato:** correzioni sviluppate e verificate localmente; **full CI RC261 non ancora eseguita**. Non avviare il rilascio Docker dalla CI automatica: pubblicazioni esplicite soltanto. **Completamento prodotto 85,25%** (43 gate accettati, 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Diagnosi verificata

- Installazione Kubernetes con due `emptyDir` separati: `/tmp` e `/conversions`. Il worker RC260 convertiva in `/tmp/quorivio-import-*` e tentava `Path.rename()` della directory completa su `/conversions/<job>/pages`. Tra filesystem diversi `rename()` fallisce con `OSError: [Errno 18] Invalid cross-device link` (`EXDEV`). La riproduzione precedente alla correzione fallisce con `errno=18`; il codice RC261 completa PDF e PPTX reali su `/dev/shm` distinto da `/tmp`, con Poppler/LibreOffice.
- CI RC260 su commit `d3f58e634d13900ea989aca7d68e82f38acd7e38`: run [42486677344](https://github.com/desalvo/quorivio/actions/runs/42486677344), **Production quality gate verde**, **Container build gate fallita** alla scansione Trivy del converter. Nel pacchetto Debian `zlib1g` sono segnalati `CVE-2026-76844` e `CVE-2026-85091` (HIGH), versione risolta `1:1.3.dfsg+really1.3.1-1+deb13u1`.

## Correzioni

1. `tools/import_presentation.py`: scratch temporaneo privato **dentro la directory del job**, sullo stesso filesystem dell'output; pubblicazione atomica invariata e pulizia automatica.
2. `tools/conversion_worker.py`: log del solo codice POSIX `errno` sugli errori `OSError`, senza riportare percorsi/documenti/diagnostica interna; stesso HTTP 422 con `conversion_failed`.
3. `apps/api/src/server.ts` e `apps/web/src/main.tsx`: l'HTTP 422 del converter è restituito all'utente come errore di conversione riconoscibile, non come generico `internal_error`. Credenziali e percorsi non sono divulgati.
4. `Dockerfile.converter`: aggiorna obbligatoriamente `zlib1g` prima di installare Poppler e LibreOffice e verifica con `dpkg` la versione corretta; in assenza di pacchetto sicuro la build fallisce. Il precedente fix APT resta attivo. **Trivy HIGH/CRITICAL continua a bloccare la CI**.
5. `tools/k8s_converter_upgrade.py` e wizard standalone `k8s_wizard.py` RC261: `--sync-generated` riconcilia un nuovo **digest di immagine converter** già distribuito al cluster, mantenendo l'overlay Kustomize e il backup privato. Solo l'immagine può differire; modifiche a Secret, filesystem, risorse, porte, securityContext, probe, o container applicativo rimangono vietate.
6. Nuovi test RC261: `tools/tests/test_rc261_conversion_mount_and_zlib.py`, `tools/tests/test_rc261_real_mount_pdf_pptx.py`, `tools/tests/test_rc261_converter_image_sync.py`. Gate CI preventivi e prova reale Poppler/LibreOffice su filesystem separati.

## Aggiornare l'installazione esistente

**Non eseguire la procedura fino a dopo il commit RC261, full CI verde e nuova pubblicazione manuale del converter.** Il solo commit non ricostruisce né pubblica `desalvo/quorivio-converter:latest`.

1. Eseguire il workflow **Publish Quorivio PDF/PPTX converter (manual only)** su `main` con autorizzazione esplicita; annotare il digest `sha256:...` della nuova immagine dai log del workflow. Verificare architetture `linux/amd64` e `linux/arm64`.
2. Sul cluster Kubernetes, prima verificare contesto e oggetto: `kubectl config current-context` e `kubectl -n quorivio get deployment quorivio`.
3. Aggiornare la **sola immagine converter**, usando il digest vero e non un valore di esempio:

   ```bash
   kubectl -n quorivio set image deployment/quorivio \
     converter=desalvo/quorivio-converter@sha256:<DIGEST_VERIFICATO>
   kubectl -n quorivio rollout status deployment/quorivio
   kubectl -n quorivio logs deployment/quorivio -c converter --since=5m
   ```

   La stringa `<DIGEST_VERIFICATO>` è un segnaposto, **non un comando eseguibile direttamente**. Un semplice rollout restart con `:latest` e `imagePullPolicy: IfNotPresent` può riusare la vecchia immagine.
4. Scaricare il wizard RC261 aggiornato (`tools/k8s_wizard.py` standalone) ed eseguire dalla directory dei manifest originali:

   ```bash
   python3 k8s_wizard.py --version
   python3 k8s_wizard.py --sync-generated --generated-dir ./k8s-generated \
     --set namespace=quorivio --set name=quorivio
   kubectl kustomize ./k8s-generated > /dev/null
   ```

   La sincronizzazione aggiorna **solo i manifest locali**, con backup privato; non modifica PostgreSQL, PVC, Ingress, TLS o token. Il wizard standalone controlla GitHub all'avvio, oppure usare consapevolmente `--no-self-update` su sistema isolato.
5. Importare un PDF e un PPTX reali come immagini. Se rimane un errore, leggere il nuovo codice `errno` nei log converter senza condividere file o token privati.

La correzione del codice API/frontend entra in un'immagine applicativa nuova solo dopo relativa pubblicazione separata. La conversione PDF/PPTX come immagini richiede principalmente il **nuovo converter**.
