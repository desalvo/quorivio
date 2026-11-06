# RC237 — Correzione contratto CI della rinomina miniature

**Base:** Quorivio 0.1.0-dev RC236, committata dall'utente (`910c60216d9e18c7602a47070a5d822588f1194f`).
La full CI https://github.com/desalvo/quorivio/actions/runs/42256926397 è fallita nel test negativo RC218 prima di npm e Chromium.

## Causa

Il verificatore cercava `actions=page.get_by_role(...)` come sottostringa non delimitata. Il nuovo `export_actions=page.get_by_role(...)` di RC236 conteneva anche quella sottostringa: la sostituzione del selettore di rinomina nel test negativo non veniva rilevata. La CI quindi falliva correttamente con `AssertionError not raised`.

## Intervento

Il controllo richiede l'assegnazione `actions=...` su una riga completa, senza poterla confondere con `export_actions`. Restano obbligatori Chromium/PostgreSQL, persistenza del titolo e menu espandibile RC236. Aggiunti test negativi RC237 nel preflight. Nessuna modifica al runtime, database, privacy o pubblicazione. Nessun test disattivato.

## Verifica

- `python3 -m unittest tools.tests.test_rc237_rename_scope_guard tools.tests.test_rc218_browser_postgres_thumbnail_rename tools.tests.test_rc236_page_menu_disclosures -q` senza `PYTHONPATH`.
- Mutazioni della rinomina devono essere respinte anche in presenza del menu di esportazione.
- RC236 storico; RC237 inventario corrente. Verificare quattro header, hash delle sorgenti e ZIP.
- Full CI GitHub ancora da certificare dopo il commit del manutentore.

**Completamento certificato 85,25%** (43 gate accettati/17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag dell'assistente.
