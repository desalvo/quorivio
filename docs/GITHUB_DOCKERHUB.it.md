# Configurazione GitHub / Docker Hub
Repository: `https://github.com/desalvo/quorivio`. Immagine Docker Hub: `desalvo/quorivio`.

1. Crea su Docker Hub il repository `desalvo/quorivio` e un **access token** con permessi di scrittura (non la password).
2. In GitHub **Settings > Environments** crea **production**: variabile `DOCKERHUB_USERNAME=desalvo` e secret `DOCKERHUB_TOKEN` con il token Docker Hub.
3. Restringi l'ambiente `production` a `main` e ai tag di rilascio fidati. Configura gli approvatori richiesti ove supportati dal piano e dalla visibilità del repository; l'autoapprovazione non rappresenta una revisione indipendente.
4. In **Settings > Actions > General**, abilita Actions e le azioni necessarie. In **Settings > Branches / Rulesets** proteggi `main`, imponi i check `Production quality gate` e `Container build gate`, vieta force push e push diretti non revisionati, restringi la creazione dei tag.
5. Attiva gli avvisi Dependabot e la scansione dei segreti dove disponibili; risolvi ogni gate fallito. Per una filiera più rigorosa, fissa le azioni allo SHA completo e verifica digest/provenance dei container.
6. Push su `main` -> `desalvo/quorivio:latest`; push di un tag compatibile (`v*`, `0.*`, `1.*`, `2.*`) -> immagine con lo **stesso tag**. In produzione preferisci digest o tag immutabili.

La pipeline pubblica l'immagine, ma non esegue deploy su server reali. Alcune regole di approvazione richiedono un repository pubblico a seconda del piano GitHub.
