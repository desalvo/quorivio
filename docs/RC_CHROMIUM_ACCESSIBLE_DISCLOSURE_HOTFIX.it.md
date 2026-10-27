# Hotfix RC Chromium: controlli accessibili e sovrapposizione (2026-10-27)

## Evidenze

- Run GitHub `40510491774`, job qualità `122210785185`, commit `a26ce48ea7d90bfdfe06e114398e2971e7846810`: errore `tools/ci_browser_editor.py:248` sul viewport mobile/touch 390 × 844.
- Il clic Playwright su `.canvas-accessible-controls > summary` era intercettato da **Stessa altezza** (disabilitato) nel pannello contestuale di allineamento aperto; nessun errore JS di pagina.
- I preflight Chromium CSS e selettore Salva erano PASS. Non è un problema di avvio browser, backend, database o pubblicazione.

## Correzioni

1. Il riepilogo accessibile chiuso ha precedenza di impilamento rispetto alla palette fluttuante; espandendolo cede tale precedenza per non impedire le azioni contestuali successive.
2. Il componente React `<details>` richiude automaticamente il menu contestuale quando si espande il pannello accessibile da tastiera e touchscreen.
3. Il test mobile verifica `document.elementFromPoint`, utilizza un tocco reale, controlla la chiusura del menu e prova la selezione e le azioni successive.
4. Il test Chromium editor con PostgreSQL richiude il menu prima di espandere il pannello accessibile nei due percorsi coinvolti.
5. Aggiunto alla Full CI il preflight Chromium `tools/ci_accessible_disclosure_chromium.py`, che riproduce intenzionalmente la sovrapposizione con il CSS reale su desktop e touch, senza `force=True`.

## Test e limiti

- Con CSS precedente: riproduzione del difetto **FAIL previsto**. Con CSS corretto: **PASS** desktop/mobile con Chromium reale `/usr/bin/chromium`.
- Preflight precedente su menu annidato PASS; 182/182 test Python editor/browser mirati e 447/447 Node PASS; 6 nuovi controlli contrattuali PASS.
- La Full CI applicativa React/Chromium/PostgreSQL non è stata eseguita localmente (dipendenze npm complete non disponibili). Necessaria la nuova esecuzione GitHub manuale con `browser_test=true`, `publish_image=false`.
- Percentuale RC **48,0%** invariata; nessun commit, push, tag o rilascio eseguito dall'assistente.
