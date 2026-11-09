# Quorivio 0.1.0-dev — RC279 — Contratti OAuth HA manuali e riparazione CI

**RC279:** Correzione della run GitHub Actions [42599356568](https://github.com/desalvo/quorivio/actions/runs/42599356568): il test RC126/RC59 cercava nel generatore PDF una frase sullo stato OAuth PostgreSQL a consumo singolo, mentre i manuali sono ora sorgenti Markdown bilingui. Il test verifica i manuali effettivi e le callback OIDC/social con stato PostgreSQL condiviso. Riconciliato anche il controllo RC154 sul test CLI da 500 partecipanti e Gravatar; aggiunta procedura di carico autorizzato con precauzioni, rigenerati i sei PDF. Inventario RC278 storico immutabile, RC279 corrente. Nessuna modifica runtime. La CI non è arrivata alle schermate autentiche; resta da collaudare. **85,25%** (43 gate accettati/17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; nessun commit/push/tag. `docs/RC_CYCLE279_MANUAL_CI_OAUTH_HA.it.md`.

## Acceptance / Collaudo

- New contract tests check both documentation languages and source-level PostgreSQL single-consume OAuth callbacks.
- The RC154 CLI/Gravatar contract checks editable manual sources, not incidental Python generator contents.
- Six role-specific manuals regenerated from authoritative Markdown; real screenshots must come from disposable Chromium/PostgreSQL CI and satisfy provenance SHA-256.
- Full GitHub CI, screenshot generation, actual browser/manual publication and DR tests remain pending.
