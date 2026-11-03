# RC142 — Copia fra pagine, anteprima smartphone e formato dei widget

**Baseline:** RC141 cumulativa, non ancora confermata come committata. Questo archivio contiene le correzioni TypeScript RC140, le modifiche RC141 e le nuove funzioni RC142. Nessun commit, push o rilascio eseguito dall'assistente.

- Copia dei widget selezionati con Cmd/Ctrl+C e incolla in un'altra pagina della **stessa sessione** con Cmd/Ctrl+V. Appunti in memoria, nuovi ID e nuovi riferimenti interni nel gruppo; i campi di testo mantengono la normale selezione/copia del browser. Backspace/Delete richiede conferma prima di eliminare i widget selezionati. Undo/Redo usa lo storico esistente.
- Chiusura della finestra Formato widget senza deselezione. Allineamento verticale alto/centro/basso. Font, dimensione e colore individuali del numero pagina nel Footer; padding destro e inferiore predefinito **5 pixel logici**, modificabile separatamente.
- Dimensioni delle emoji Reazioni (16–96) e dei pulsanti Gradimento (10–64) modificabili dalla finestra di formato; convalida backend e unità relative per le reazioni, compatibili con la riscalatura del contenuto.
- Anteprima **Smartphone** separata e selettore Desktop/Smartphone nella prova affiancata, accessibili da dashboard ed editor. Simulazione di dispositivo largo 390 px, non certificazione di tutti i dispositivi fisici.
- Ripristinata la visibilità completa del righello superiore con altezza esplicita di 29 px.
- Inventario RC142 rigoroso con storici preservati.

**Validazione:** test mirati Node/Python, suite Node completa, parsing TS/TSX e integrità SHA-256 del sorgente e del package. Build Vite completa, verifiche browser reali e collaudi Kubernetes da confermare nella prossima CI. Completamento certificato **85,25%** (43 gate accettati / 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Evidenze locali (3 novembre 2026):** 810/810 test Node superati; 30/30 Python mirati superati; parsing TypeScript/TSX valido per sei moduli modificati; metadati di rilascio e inventory guard superati. Build npm/Vite completa, suite Python generale e test visivi su browser/dispositivi reali non completati localmente: non vanno considerati superati.
