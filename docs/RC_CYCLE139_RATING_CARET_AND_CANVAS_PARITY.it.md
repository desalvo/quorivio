# RC139 — Gradimento uniforme, selezione testo e spaziatura canvas (2 novembre 2026)

Baseline: RC137 committata con CI completa verde (run 41475936282); il cumulativo include RC138 non ancora committata.

Un unico componente 0–10 viene utilizzato in editor, schermo reale del presentatore, prova affiancata e vista del partecipante. L'editor mostra un solo titolo, la vista presentatore non può inviare voti, mentre il partecipante utilizza pulsanti grandi e leggibili (oppure il selettore configurato). Il layout rispetta geometria e stile del canvas.

La chiusura della finestra **Formato widget** non deseleziona più il widget. Gli eventi del puntatore nei campi di testo modificabili non avviano lo spostamento del widget; il doppio clic non riporta forzatamente il cursore all'inizio. Nei campi delle proprietà è stata rimossa la selezione totale forzata; clic e trascinamento del mouse devono consentire il posizionamento e la selezione del testo. La spaziatura interna 16:9 è uniforme, senza i 23 px extra riservati a destra dal solo editor. La geometria definita dall'autore resta indipendente dalla dimensione naturale del contenuto.

Verifiche locali: sintassi TypeScript, Node, contratti storici Python, inventario SHA-256. La build completa e le interazioni nel browser reale devono essere confermate dalla prossima CI GitHub e dall'installazione dell'utente.

**Completamento certificato 85,25% (43 gate accettati / 17 parziali)**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o rilascio effettuato dall'assistente.
