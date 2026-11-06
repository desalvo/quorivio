# RC230 — Correzione inventario CI attivo dopo RC229

## Errore

La run GitHub Actions `42230115609` (SHA `41a0339e9cc0ac6f52c7f7d28d322e2c9229fa66`) fallisce nella fase "Validate active RC release headers against the current inventory". L'ultimo inventario non storico nel workflow era RC227 mentre le intestazioni correnti indicavano RC229. Il report finale fallito e i job saltati sono effetti conseguenti, non prove autonome di regressioni runtime.

## Correzione

- Conservare i manifest originali RC227, RC228 e RC229; i loro verificatori sono invocati come `--historical`.
- Designare solo `verify_rc_cycle230_inventory.py` come ultimo inventario non storico nella CI.
- Aggiornare le quattro intestazioni correnti a RC230 senza cancellare le sezioni storiche né i flag di sicurezza.
- Produrre un catalogo cumulativo SHA-256 e un test prima di npm che verifica la coerenza release/inventario e rileva intestazioni ferme a RC227.
- Non modificare il codice runtime né la percentuale certificata: 85,25%, 43 gate accettati e 17 parziali.

## Accettazione

In un checkout Git pulito eseguire `PYTHONPATH=tools python3 tools/verify_rc_release_status.py`, `python3 tools/ci_inventory_reference_guard.py`, `PYTHONPATH=tools python3 tools/verify_rc_cycle230_inventory.py` e `python3 -m unittest tools.tests.test_rc230_inventory_promotion tools.tests.test_rc199_release_headers -q`. Poi attendere i risultati effettivi della full CI sul commit dell'utente; i test locali non certificano la CI remota.

Versione `0.1.0-dev`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o pubblicazione Docker da parte dell'assistente.
