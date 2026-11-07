# RC249 — Menu miniature flottante sempre esterno al pulsante di apertura

## Fallimento confermato

RC248 committata come `9027af34f0d8182d12bda366a89e239286b63a41`, full CI GitHub [42405687692](https://github.com/desalvo/quorivio/actions/runs/42405687692): il browser React reale (`tools/ci_browser_editor.py`) non riusciva a cliccare sul pulsante «Menu pagina 1» già aperto. Nel portale del menu la voce «Rinomina pagina (R)» intercettava gli eventi del puntatore. Playwright ha giustamente rifiutato di forzare il clic. ClamAV verde; campagna estesa non proseguita.

## Correzione

La posizione del menu viene calcolata sul rettangolo reale del pulsante, a destra/sinistra quando possibile, riducendone la larghezza negli schermi stretti; in assenza di spazio laterale viene usato quello verticale. Restano lo scorrimento interno, la limitazione al viewport, l’accessibilità da tastiera, Escape e il ripristino del focus. La posizione viene aggiornata durante scroll della barra miniature, resize e variazioni dello zoom. Nessun clic forzato nei test, né rimozione dei vecchi controlli React/PostgreSQL.

## Test e stato

Nuovo preflight negativo prima di npm, test geometrici TypeScript e puntatore Chromium reale a 320×240, 390×844, 760×820, 960×760 e 1440×900. I test RC224/RC248 restano attivi e i manifest storici immutati. Full CI RC249 da eseguire. **85,25%** (43 accettati/17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`; nessun commit/push/tag o intervento sul cluster.
