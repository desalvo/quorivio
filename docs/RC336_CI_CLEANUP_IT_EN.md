# Quorivio RC336 — CI and diagnostic cleanup / Ripristino CI e cleanup diagnostica

**Source baseline:** `desalvo/quorivio/main` `287e4bdd3c880aed1b42e30aa8e2ffc45a6e2152` (13 November 2026).

## Italiano

- Conservate le **quattro esportazioni visuali**: PDF/PPTX presentatore e PDF/PPTX partecipante, con filename derivato dal titolo della sessione e pagina correttamente selezionata per vista. Nessuna modifica al renderer Chromium o alle sue protezioni.
- Il test storico `tools/tests/test_rc332_export_background.py` richiedeva due vecchie etichette non più presenti. Ora verifica le quattro etichette e le quattro URL con parametro `view`.
- Il cleanup diagnostico tentava di passare `[retentionDays]` alla query `WHERE expires_at<=now()` priva di `$1`, facendo fallire PostgreSQL 18 e l'eliminazione dei bundle scaduti. Rimossi i bind superflui; mantenuti `FOR UPDATE SKIP LOCKED`, transazione, rollback e limite di 100 righe per ciclo.
- Tre regressioni Node coprono la rimozione del file e dei metadati, il rollback in caso di errore filesystem e l'idempotenza quando il file manca già.
- Inventario SHA-256 dei sorgenti aggiornato nello stesso commit, senza riscrivere inventari storici. La full CI, il converter e il publishing Docker amd64/arm64 devono ancora essere verificati al termine del workflow.
- Completamento globale ufficiale **85,25%** (43 criteri accettati, 17 parziali); la parità visiva del PDF/PPTX con sessioni reali rimane un criterio di collaudo esterno.

## English

- Preserve independent PDF/PPTX presenter/participant visual exports and Chromium capture security; update historical RC332 UI assertions to check all four current labels and URLs.
- Fix PostgreSQL bind-parameter mismatch in expired diagnostic-bundle cleanup. Expiry is already stored in `expires_at`; do not bind a parameter to a query with no placeholders. Transactional locking and rollback stay intact.
- Add three Node regressions for successful cleanup, rollback on removal errors and missing-file idempotence. Refresh the current source inventory without touching historical signed receipts.
- Fail closed until the full CI and paired native Docker Hub publication succeed. Official independent acceptance remains 85.25%.
