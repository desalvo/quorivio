# Quorivio 0.1.0-dev — RC183: riconciliazione della suite Python completa

## Diagnosi GitHub

La run `41952294082` (commit `95ab635b6c856dadb4653a835013e7973199df4b`, job `126998827097`) ha superato preflight, compilazione, Chromium editor e verifiche reali React/PostgreSQL, arrivando allo step **Kubernetes wizard and worker integration tests**. La discovery Python ha completato **1.948 test in 44,102 secondi**, con quattro errori dovuti a espressioni obsolete presenti in tre test storici (RC139, RC141 e public stage 20261028), non a un errore Kubernetes.

- RC139 verificava una vecchia maschera inline dei titoli, mentre oggi `RatingStageContent` e `widgetTitleVisible()` centralizzano il comportamento e impediscono duplicazioni durante la modifica.
- RC141 richiedeva la stessa maschera precedente, ora sostituita dalla resa condivisa di reazioni e titoli per editor, anteprima e live.
- Public-stage verificava una vecchia selezione a due modalità e l'attivazione automatica mobile in base alla larghezza: ora esistono tre modalità esplicite. La verifica dello sfondo cercava la concatenazione diretta `backgroundAssetId`, mentre il rendering usa `slideBackgroundCss()` con URL privati vincolati alla sessione e all'attività.

## Correzione

Aggiornati i tre moduli storici sulla semantica corrente e aggiunto `test_rc183_projection_contract_reconciliation.py`, con mutazioni negative per prevenire titoli duplicati, confusione delle modalità, visibilità dei risultati privati e URL media non vincolati. Aggiunto **preflight anticipato senza dipendenze** alla CI, prima di npm, Chromium e PostgreSQL. Nessuna modifica al runtime dell'applicazione; nessuna credenziale o dato utente aggiunto.

## Stato di accettazione

Il percorso GitHub precedente ha già superato i collaudi autentici React/PostgreSQL fino al gate Python conclusivo, ma solo la CI del nuovo commit potrà certificare RC183 completamente. Punteggio invariato **85,25% (43 gate accettati / 17 parziali)**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag/deploy dell'assistente.
