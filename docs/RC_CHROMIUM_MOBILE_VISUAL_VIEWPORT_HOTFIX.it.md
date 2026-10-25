# Hotfix Chromium full: viewport visivo mobile — 25 ottobre 2026

## Errore confermato

Run GitHub Actions `40218596128`, quality job `121245025409`: il test `tools/ci_browser_editor.py` fallisce nella fase **mobile/touch**, durante la conferma dell'informativa cookie. La fase desktop aveva già raggiunto l'editor: l'artefatto `mobile-failure.png` identifica il punto effettivo del blocco.

Playwright trova il pulsante `Ho capito`, ma scade il timeout perché il `<dialog>` nativo intercetta il clic. Il precedente `showModal()` risolveva il problema dello stacking con la dashboard, ma non quello delle coordinate mobile.

## Causa riprodotta

Analizzati gli artefatti della CI e riprodotto il fallimento in Chromium locale caricando il DOM mobile salvato. In una finestra touch **390×844**, l'overflow può produrre un viewport di layout **574×1243** mentre quello visivo rimane **390×844**. Il dialogo ancorato in basso posiziona il pulsante intorno a **y=1173**, fuori dalla zona cliccabile. La riproduzione prima della correzione genera lo stesso timeout Playwright; dopo la correzione il pulsante è intorno a **y=196** e il clic reale riesce.

## Correzione e verifiche

- `apps/web/src/style.css`: su schermi <=740 CSS px, ancoraggio del dialogo in alto (`top:18px;bottom:auto`); il desktop rimane in basso, con top layer nativo.
- Entrambi i test browser (`ci_browser_editor.py`, `ci_browser_editor_postgres.py`) verificano che il centro del pulsante sia all'interno di `window.visualViewport`, poi eseguono il normale clic senza `force=True`.
- `tools/ci_cookie_viewport.py`: test Chromium locale senza rete su desktop e mobile/touch con viewport di layout intenzionalmente più largo; il CSS precedente fallisce, quello nuovo passa.
- Tre nuove regressioni Python e aggiornamento dei test contrattuali esistenti.

**Validazione locale:** Node **314/314**, Python **633/633**, build TypeScript API e TypeScript/Vite web **PASS**, click Chromium desktop/mobile **PASS**. Test completo GitHub `browser_test=true` ancora **da eseguire**. Gate A1 parziale e avanzamento RC **45,5% invariato**. Nessun commit/push/tag/release/deploy effettuato dall'assistente.
