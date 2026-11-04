# RC164 — Correzione collaudo Chromium della palette grafica

La run GitHub [41760453415](https://github.com/desalvo/quorivio/actions/runs/41760453415) sul commit `81ff882` ha superato 588 test Node API, 272 frontend e la compilazione TypeScript/Vite. Si è fermata in `tools/ci_browser_editor.py`: il collaudo leggeva solamente `data-widget-kind`. Dalla RC161 i pulsanti Linee e Forme mantengono la classe `.editor-icon-tool` ma usano `data-graphic-palette` per il menu contestuale. Il test li considerava assenti benché presenti.

La RC164 riconosce entrambi gli attributi, verifica unicità delle icone e dei nomi accessibili, conserva l'eccezione al tooltip nativo per gli elementi grafici e controlla l'apertura con tasto destro dei due menu nell'accettazione Chromium reale. Il menu viene richiuso senza inserire elementi. Il preflight anticipato include mutazioni negative.

Nessuna modifica al runtime o ai dati. Inventario RC163 storico immutato. CI GitHub completa e pubblicazione Docker non ancora certificate dai test locali. Completamento certificato 85,25% (43 accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
