# RC125 — Pubblicazione Docker Hub AMD64/ARM64 nativa senza QEMU (2 novembre 2026)

## Causa dimostrata dal log

Nel run GitHub `41361426087`, tentativo 2, sul commit `a97b80b8d09ebd1a6054111bf88326581e2cc80f`, il build ARM64 eseguito da un host x86 raggiunge `RUN npm install --no-audit --no-fund` e stampa `qemu: uncaught target signal 4 (Illegal instruction) - core dumped`, restando fermo sullo step BuildKit. In parallelo il ramo AMD64 completa TypeScript, Vite e SBOM. Il blocco avviene **prima della pubblicazione dei tag**: non riguarda le credenziali Docker Hub né il warning di deprecazione `punycode`. Non si attribuiscono automaticamente al medesimo bug tutti gli eventuali fallimenti futuri.

## Correzione

La pubblicazione usa adesso due runner GitHub distinti: `ubuntu-24.04` per `linux/amd64` e `ubuntu-24.04-arm` per `linux/arm64`, senza QEMU nel build di pubblicazione. I due job caricano su Docker Hub soltanto digest immutabili con SBOM e provenance. Il job finale scarica entrambi i digest, verifica formati e architetture reali e crea il manifest multipiattaforma attribuendo i tag approvati (SHA/versione e, soltanto quando richiesto, `latest`). Verifica poi la presenza effettiva di entrambe le piattaforme nell'indice pubblicato.

Se manca un'architettura, il manifest non viene creato e **nessun tag mutabile** viene assegnato; restano obbligatori i controlli di qualità, l'autorizzazione esplicita, il segreto Docker Hub, l'ambiente protetto `production` e la campagna RC completa per `[publish-docker]`. `[full-ci]` non pubblica. Timeout di 35 minuti per runner e 10 minuti per il manifest. Nessuna riduzione silenziosa alla sola AMD64.

## Prove e limiti

Test locali Python, controlli del workflow e simulazioni Docker confermano la protezione dei digest e dei tag, inclusi casi negativi. Mancano il collaudo remoto dei runner ARM64, il vero push al registry e l'ispezione del manifest Docker Hub: **nessuna pubblicazione viene dichiarata completata**.

Procedura: prima commit del cumulativo con `[full-ci]` e controllo della CI; poi, solo se si vuole pubblicare, `workflow_dispatch` con `publish_image=true`, `rc_acceptance_suite=false` e `publish_latest=true` **solo** se si desidera spostare `latest`. Alternativamente il commit con `[publish-docker]` pubblica soltanto dopo tutti i gate della campagna RC. I default restano `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Certificazione: 85,25%** (43 gate accettati / 17 parziali su 60); stima locale **85,75%** da RC124 non ancora certificata. Nessun commit, push, tag o release eseguito dall'assistente.
