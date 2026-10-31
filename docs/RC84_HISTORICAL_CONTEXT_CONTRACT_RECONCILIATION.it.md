# RC84 — adeguamento contratto test del menu widget

**CI:** `41234368553` / `124636106637`; commit `112d3c2a99b44b743bfc56f5137cd9781323f9fd`.

**Diagnosi:** 1 test Python fallito su 1.466, dopo superamento dei controlli Node, compilazione e integrazioni. Il test RC37 ricercava letteralmente l’handler inline `positionMenu(e.currentTarget,e.clientX,e.clientY)`, eliminato dal nuovo flusso `onContextMenuCapture` di RC83.

**Correzione:** RC37 ora verifica il percorso nativo `handleCanvasContext` → identificazione widget DOM/geometrica → `openWidgetContextMenu` → posizionamento nel viewport; mantiene controlli portal a `document.body`, touch e scorciatoia tastiera. I nuovi test RC84 controllano che tale contratto e la relativa fase CI siano mantenuti. Test funzionali Chromium restano obbligatori e non vengono saltati.

**Rilascio:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`; punteggio invariato 84,75%. Non attestare nuova CI fino a esecuzione GitHub.
