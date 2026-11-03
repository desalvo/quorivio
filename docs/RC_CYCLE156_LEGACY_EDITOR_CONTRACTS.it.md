# RC156 — Allineamento dei test storici dell'editor alla versione corrente

La CI GitHub [41720825704](https://github.com/desalvo/quorivio/actions/runs/41720825704) relativa alla RC155 ha superato preflight, 833 test Node, compilazione TypeScript/Vite e vari collaudi Chromium/PostgreSQL, ma nella suite finale Python di 1.798 test ha registrato tre fallimenti dovuti a confronti letterali obsoleti: `test_canvas_background_native_context`, `test_editor_page_isolation` e `test_rc_rehearsal_unique_mount_20261028`.

Il runtime applicativo non cambia. Aggiornati i tre test affinché verifichino i comportamenti attuali:

- Caricamento dello sfondo desktop e smartphone tramite il medesimo handler con destinazioni indipendenti e selezione dello sfondo dedicato.
- Identità del canvas legata a sessione, pagina e dispositivo (`canvasDevice`), con layout mobile separato.
- Anteprima dell'editor costruita dalla bozza non salvata, inclusi widget, sfondo desktop e layout smartphone.

Aggiunti test positivi e mutazioni negative in `tools/tests/test_rc156_editor_contracts.py`; le quattro suite vengono eseguite nella CI prima di npm e dei costosi test di integrazione. L'inventario RC155 rimane storico e immutato, mentre RC156 diventa corrente. Nessuna modifica funzionale, commit, push o deploy da parte dell'assistente.

**Accettazione ancora necessaria:** CI GitHub `[full-ci]` completa e collaudi esterni. La prova reale 500 utenti richiede esecuzione esplicitamente autorizzata e separata. Completamento certificato invariato **85,25%** (43 accettati / 17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
