# RC129 — Ripristino editor nel test Chromium

- Run GitHub `41389141345`: gate qualità fallito nel passo `Chromium editor UI acceptance`, dopo la compilazione.
- Il test salvava 4 widget ed eseguiva `page.reload()`, ma ripeteva la navigazione manuale. RC128 ripristina già sessione, scheda e pagina con autenticazione.
- La miniatura `.page-editor-thumb-row.is-active` intercettava il clic di background: comportamento atteso della protezione dei puntatori, non prova di un difetto di sovrapposizione CSS.
- Il test attende ora la riapertura automatica della pagina, il focus editor, la miniatura attiva, 4 widget e gli ID della stessa sessione/pagina in `sessionStorage`.
- Nessun `force=True`, nessuna modifica al rendering, alla sicurezza o alla pubblicazione.
- RC129: test statici locali superati, browser reale e CI completi da verificare sul prossimo commit.
- Gate RC: 43 accettati, 17 parziali su 60; punteggio **85,25%** certificato; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
