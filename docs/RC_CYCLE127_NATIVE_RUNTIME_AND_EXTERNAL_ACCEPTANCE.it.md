# RC127 — Runtime nativo su due architetture e collaudo esterno per RC (2 novembre 2026)

## Evidenza già confermata su GitHub

La run GitHub Actions **41377221623** (commit `d5cff85367a8e906d6e0d59a41ecf82477245b99`, marcatore `[publish-docker]`) ha concluso correttamente la campagna completa RC126: quality gate, browser reali e PostgreSQL, Kubernetes/NGINX/HAProxy, ClamAV, Podman e pubblicazione Docker Hub separata AMD64/ARM64. I tag verificati sono `desalvo/quorivio:sha-d5cff85367a8` e `desalvo/quorivio:latest`, entrambi sul manifest `sha256:752b3108dd3a7a8a351fbfe93870bbc8455bacd8e5349746dcaca5882066ec5d`. È una prova tecnica multiarch di **compilazione/pubblicazione**; non prova esecuzione nativa con PostgreSQL su un host ARM.

## Sviluppi RC127

- Il precedente test `runtime-architecture` costruiva ARM64 tramite QEMU su una macchina AMD64. Ora crea **due job nativi indipendenti**, ciascuno con il proprio runner (`ubuntu-24.04`, `ubuntu-24.04-arm`), e fallisce se `uname -m` non corrisponde alla CPU richiesta.
- Per ognuno, build OCI **non pubblicante**, esecuzione con PostgreSQL 18 e verifica reale di architettura Node, non-root, assenza di npm nell'immagine, esistenza di frontend/backend compilati, readiness, liveness, pagina HTTP, Content-Security-Policy e Permissions-Policy. La rete e le credenziali sono usa-e-getta. La campagna RC continua a richiedere **entrambe** le matrici; un fallimento non viene nascosto dall'altra (`fail-fast: false`).
- Aggiornati i soli test storici che pretendevano QEMU nel job runtime; aggiunti test nuovi di confinamento e autorizzazione. Il nuovo preflight avviene prima di npm.
- Creato un **piano operativo IT/EN a evidenza esterna**, `docs/validation/RC127_OPERATOR_ACCEPTANCE_PLAN_20261102.json`, generato dal registro di 60 gate e verificato dalla CI. Contiene i **17 gate ancora parziali** e l'esatto tipo di riscontro da far approvare a un operatore esterno. Tutte le approvazioni e i collegamenti alle prove sono inizialmente vuoti; non si falsificano collaudi fisici o consenso OIDC.

## Completamento e blocco reale

**Punteggio certificato: 85,25% (43 gate accettati e 17 parziali, su 60).** Stima locale 85,75%, non certificata. La run verde 41377221623 conferma le modifiche RC125/RC126, ma **non** le prove native di runtime RC127, che richiedono un nuovo commit e la CI GitHub.

La RC formale resta **BLOCCATA** fino ad accettazione indipendente di A1–A4, B1–B4, C1–C4, D2–D6 (device/AT, provider esterni, CSI/RWX, SLA, restauro offsite, sicurezza, GDPR e revisione manuali). `rc_strict` non deve essere disabilitato per dichiarare RC; nessuna promozione o approvazione è effettuata da questo package. Il prossimo commit può contenere `[full-ci]` ma **non** richiede `[publish-docker]`.

## Verifiche locali / Local verification

Suite Python completa: **1.661 test eseguiti, OK (1 saltato)**. Il controllo `--strict` del readiness preflight termina intenzionalmente con codice 2, perché 17 gate non sono accettati. Inventario del package e relativi SHA-256 verificati. La prova con reali runner ARM64 e la compilazione Node/TS restano compito della successiva CI GitHub.
