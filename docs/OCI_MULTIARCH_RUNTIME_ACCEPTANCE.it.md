# Accettazione runtime OCI — prova opzionale AMD64/ARM64

Ciclo 22, Quorivio 0.1.0-dev. Il parametro manuale `runtime_arch_test=true` attiva un job GitHub separato: compila l'immagine con Docker Buildx per `linux/amd64` e `linux/arm64`, senza alcuna pubblicazione. ARM64 viene eseguito con **QEMU**, non su hardware ARM64 nativo.

Per ogni architettura `tools/ci_oci_runtime_smoke.sh` avvia realmente l'immagine, verifica `process.arch`, UID non-root, file compilati API e UI e assenza di npm nell'immagine di produzione. Avvia un PostgreSQL 18 separato su rete Docker interna e controlla che l'applicazione resti attiva e risponda alle richieste `/api/health/ready`, `/api/health/live` e `/` con HTML. Le richieste partono dal container, senza pubblicare porte sull'host. I container temporanei vengono eliminati anche in caso di errore; le credenziali sono esclusivamente di prova e non vengono riportate nei log da questo script.

**Finché il nuovo job non passa su GitHub non si assegna alcun punto RC.** Questa prova non sostituisce Podman rootless (l'UID non-root *interno* non rende rootless il motore Docker), test su CPU ARM64 fisica, Kubernetes multi-nodo, HAProxy/NGINX, storage RWX, failover ClamAV, rete reale né accettazione operativa. Tali elementi restano aperti nel gate D3.

Dopo il commit eseguire manualmente la CI con `runtime_arch_test=true`, `browser_test=true`, `cross_browser_test=true`, `capacity_test=true` e tutte le opzioni di pubblicazione disattivate. Registrare run, commit e job effettivamente verdi.
