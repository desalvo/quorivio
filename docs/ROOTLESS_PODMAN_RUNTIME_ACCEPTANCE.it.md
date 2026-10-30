# RC ciclo 27: collaudo effettivo con Podman rootless (opzionale, non ancora validato su GitHub)

Versione `0.1.0-dev`, licenza EUPL-1.2 invariate. La nuova opzione manuale di GitHub Actions `rootless_podman_test=true` costruisce il `Dockerfile` di produzione **come utente non privilegiato** e avvia, tramite Podman rootless, PostgreSQL 18 Alpine e l'immagine Quorivio con rete interna temporanea. Nessun push, pubblicazione di porte, container privilegiato o dato di produzione. Lo script rifiuta l'utente root, il Podman rootful e i motori remoti configurati tramite variabili d'ambiente.

I controlli verificano la reale esecuzione Node come utente non-root, i file compilati API/web, l'assenza della CLI npm nell'immagine finale, la disponibilità di PostgreSQL, l'avvio del servizio, le risposte positive da `/api/health/ready` e `/api/health/live` e una pagina HTML. Le password sono usa-e-getta, non vanno nei log; i container e la rete vengono eliminati alla fine anche in caso di errore. Il job fallisce esplicitamente su errori/timeout.

## Prossimo collaudo

Dopo il commit manuale del nuovo package cumulativo, eseguire **Quorivio CI and Docker Hub** con `rootless_podman_test=true`, `runtime_arch_test=true` e gli altri collaudi già previsti, lasciando **`publish_image=false`, `publish_latest=false`, `rc_strict=false`**. Il fix OCI AMD64/Node `x64` del ciclo 26 deve ancora essere verificato in esecuzione su GitHub. Questo nuovo percorso **non** dimostra HA multinodo, RWX CSI reale, ingress produttivo, hardware ARM64 nativo, compatibilità SELinux su tutti gli host o approvazione indipendente accessibilità/GDPR/AGID.

## Stato

In locale risultano PASS la suite Python completa (1.172 test, uno saltato), 474 test Node backend e 65 Node frontend, oltre alla sintassi, ai contratti del workflow e ai percorsi di errore. Build TypeScript/Vite non verificata: le dipendenze npm locali sono incomplete. Non verificati Podman/Docker/QEMU o PostgreSQL effettivo. La **percentuale RC rimane 79,0%** (30 gate accettati, 17 parziali), senza attribuire accettazioni premature. Nessun commit, tag, push o rilascio automatico.
