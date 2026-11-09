# Quorivio RC275 — Correzione dei contratti UI risultati

Full CI GitHub Actions [42551661125](https://github.com/desalvo/quorivio/actions/runs/42551661125) fallita al preflight `RC220`, precisamente nel controllo storico `test_rc192_source_and_delete`: il componente condiviso `LinkedResultChart` passa ora `viewWidget` a `LinkedResultSourceQuestion` affinché il pulsante R controlli la visualizzazione delle risposte corrette/sbagliate nella domanda sorgente. Il test RC192, e anche il contratto RC196 eseguito in una fase successiva, richiedevano ancora il precedente passaggio `widget`.

Le verifiche sono aggiornate a `result={viewWidget}` e rafforzate: devono riconoscere il ponte di stato `hasKey&&truthVisible` e il pulsante `setTruthVisible`; un test di mutazione fallisce se si ripristina il vecchio passaggio `widget` o si rimuove il ponte di stato. Nessun cambiamento nei dati dei partecipanti o nel codice runtime.

Verifiche locali: suite mirata RC192/RC196/RC275, preflight Python, inventario corrente SHA-256 e ZIP cumulativo. Full CI e collaudi browser/cluster da certificare. Baseline **85,25%**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag.
