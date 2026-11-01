# Quorivio 0.1.0-dev — RC121 — Esportazione JSON delle bozze pagina (1 novembre 2026)

**CI precedente:** GitHub Actions `41341765759`, commit `494416c3cc3c20db6c3da6330ba69d42df51196c`, ha superato compilazione TypeScript/React, Chromium iniziale, prove dei partecipanti con PostgreSQL e verifiche reali di salvataggio/conflitto/riconciliazione. Si è fermata all'esportazione JSON nel test `ci_browser_editor_postgres.py`: `page.expect_download()` senza download. L'artefatto diagnostico della CI riporta `JS errors: ['invalid_draft_value']`; il menu della miniatura è rimasto aperto. I job successivi sono stati saltati.

**Correzione RC121:** prima della validazione e dell'esportazione le sole proprietà *facoltative* `undefined` degli oggetti widget sono omesse dalla rappresentazione JSON, senza modificare i widget nell'editor. Restano bloccati valori non validi negli array, numeri non finiti, cicli, chiavi non sicure, identificativi duplicati e proprietà obbligatorie mancanti. Formato v2, revisione e riconciliazione restano invariati. Un errore di esportazione appare in un messaggio accessibile nel menu, che rimane aperto. Aggiunte cinque regressioni Node e cinque controlli Python; il test PostgreSQL/Chromium continua a richiedere un file JSON realmente scaricato e l'esatta revisione base.

**Completamento certificato:** **85,25%**, 43 gate accettati e 17 parziali su 60, invariato. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. La full CI RC121 è ancora da eseguire; nessun commit/push/pubblicazione effettuati dall'assistente.

**Messaggio di commit suggerito dopo RC120:** `Handle optional widget props safely in page draft JSON exports and preserve strict backup validation [full-ci]`.
