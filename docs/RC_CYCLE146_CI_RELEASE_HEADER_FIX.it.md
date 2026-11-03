# RC146 — Hotfix coerenza intestazioni release in CI

## Causa

La run [41674561888](https://github.com/desalvo/quorivio/actions/runs/41674561888) sul commit `04b124a381cc63a54ad1a584144ba7479a5aa706` è fallita nel **Production quality gate**, allo step `Validate active RC release headers against the current inventory`. Inventario attivo RC145, ma `docs/COMPLETION_HANDOFF.md` aveva ancora l'intestazione RC144 e `docs/COMPLETION_HANDOFF.it.md` RC143. L'arresto precede installazione, compilazione, test Node, PostgreSQL e pubblicazione Docker. Il controllo ClamAV reale è passato indipendentemente; il riepilogo finale fallisce come conseguenza.

## Correzione

- Allineate a RC146 tutte e quattro le intestazioni attive di stato e passaggio di consegne, conservando le sezioni storiche.
- Inventario RC145 conservato immutato, marcato storico nel workflow; nuovo inventario cumulativo RC146.
- Aggiunto `tools.tests.test_rc146_release_header_fix` per verificare intestazioni, flag, percentuali localizzate e riferimento corrente nel workflow.
- Nessuna modifica runtime: mantenute tutte le correzioni RC145 per sfondo smartphone e Arial.

## Verifica

Eseguire `python3 -m unittest tools.tests.test_rc_cycle100_release_status_guard tools.tests.test_rc146_release_header_fix -q`, `python3 tools/ci_inventory_reference_guard.py`, `python3 tools/verify_rc_release_status.py` e `python3 tools/verify_rc_cycle146_inventory.py` dopo il nuovo manifesto. CI completa necessaria prima di Docker/RC formale. 85,25% certificato (43 accettati/17 parziali) invariato. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

Commit suggerito dopo RC145: `Fix RC146 release headers and CI inventory continuity [full-ci]`.
