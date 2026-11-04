# Quorivio 0.1.0-dev — RC179: comandi contestuali accessibili sopra la palette

**Evidenza CI:** run [41878608401](https://github.com/desalvo/quorivio/actions/runs/41878608401), job `126744879605`, commit `88d0cbb842b131a5315e92a093e7c2e60349424b`. Il 4 novembre 2026 il job è fallito nello step `Chromium editor UI acceptance (opt-in)`; installazione npm, unit test, build frontend/backend e controlli Chromium iniziali erano riusciti. I test successivi non sono stati eseguiti; il riepilogo RC ha fallito conseguentemente. Il controllo ClamAV è riuscito.

**Errore effettivo:** `tools/ci_browser_editor.py:272` cerca di cliccare `Duplica selezione`, richiamando `control.click()` in `tools/ci_editor_context_tools.py:102`. Nonostante il pulsante sia visibile e attivo, la griglia `.editor-widget-grid` della palette ne intercetta il puntatore e Playwright va in timeout dopo 12 secondi. Screenshot diagnostico disponibile nell'artefatto `chromium-editor-failure` della CI.

**Causa:** RC178 ha corretto l'altezza della palette a più righe, ma la palette appartiene al livello di stacking `z-index:13`, mentre il contenitore `.editor-stage` è a `z-index:1`. La barra contestuale è `position:fixed` con livello interno elevato, che però resta confinato nello stacking context del suo contenitore. I pulsanti in alto vengono quindi coperti dalla palette: non è solo un problema del test.

**Correzione:** lo stage sale a `z-index:70` soltanto quando contiene `.canvas-editor-group[data-tools-open="true"]`, tramite CSS `:has(...)`. Il normale comportamento della palette torna invariato quando gli strumenti vengono chiusi; l'header resta sopra lo stage. Non sono stati usati clic forzati né disattivate le intercettazioni del browser.

**Verifica:** nuova prova Chromium che carica il CSS distribuito, controlla l'elemento fisicamente sotto il puntatore e clicca realmente i pulsanti «Duplica selezione» e allineamento a 1440×900, 960×800 e 390×844. Test *fallito sulla CSS precedente* e *superato dopo la correzione*. Aggiunto preflight Python e test Chromium anticipato nella CI.

**Accettazione:** **85,25% certificato, 43 gate accettati e 17 parziali**, in attesa della CI completa successiva al commit e dei collaudi indipendenti. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag/release eseguito dall'assistente.
