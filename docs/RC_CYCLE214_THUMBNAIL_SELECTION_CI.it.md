# RC214 — CI miniature con selezione multipla e ripristino del focus

## Diagnosi GitHub
Run `42142002249`, job `127644319112`, fallita nello step `RC106 isolated compiled-preview and floating portal contracts`: il test storico `test_editor_contextual_layout_v2.py` esigeva il vecchio `onClick={()=>beginPageDesign(a)}`, sostituito correttamente da RC206 con il gestore evento che distingue clic standard e Ctrl/Cmd+clic. ClamAV verde, gli altri job saltati. La verifica anticipata di TypeScript RC213 non ha prodotto errori in questa run.

## Riconciliazione e correzioni
Aggiornati i contratti storici `test_editor_contextual_layout_v2.py`, `test_editor_thumbnail_keyboard_rc.py` e `test_page_editor_followup.py`: ora verificano apertura della pagina su clic normale, selezione multipla con Ctrl/Cmd senza navigazione, tasti D/R/Backspace, riordino con Alt+frecce, blocco azioni su sessioni chiuse, etichette dinamiche per l'azione in gruppo e accessibilità. Corretto un difetto reale di focus: con Escape, il menu portalled delle miniature ora cattura il riferimento al pulsante di apertura *prima* di chiudersi e vi restituisce il focus dopo la rimozione del menu. Nuovo `test_rc214_thumbnail_selection_ci.py` con mutazioni negative sul guard Ctrl/Cmd, sulla chiamata all'editor, sull'accessibilità e sul focus, eseguito nel preflight prima di npm. La logica applicativa della selezione/duplicazione/rinomina/cancellazione resta invariata.

## Politica di rilascio
Versione `0.1.0-dev`; completamento certificato **85,25%** (43 accettati / 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Cumulativo dal RC213, inventario con SHA-256 per ogni file e 201 riferimenti storici/corrente CI. Full CI RC214 e build React finale da confermare; ultima full CI verde: RC203 `42110429701`. Nessun commit, push o tag da parte dell'assistente.
