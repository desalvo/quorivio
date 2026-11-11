# RC306 — Leggibilità delle risposte lunghe nei risultati a barre

**Data:** 11 novembre 2026. **Baseline GitHub:** `028bb3328dea2728fb50fe8284f12d447dbad45e` (RC305, full CI e Docker Hub pubblicati).

**Bug reale:** le opzioni lunghe venivano interpretate come contenuti da ridimensionare integralmente anziché testo impaginabile. Un vecchio percorso di auto-fit misurava il `scrollWidth` di righe a `max-content`, riducendo tutti i testi nel widget fino a diventare quasi illeggibili, anziché andare a capo.

**Correzione:** `WidgetContentFit` riconosce i risultati con `result-view-bars`: per essi mantiene factor=1 e usa la modalità scroll, con testo alla dimensione dell'autore. CSS specifico per le barre vincola righe, etichette e track alla larghezza effettiva del widget; abilita il ritorno a capo e lo scorrimento verticale. Torte, nuvole, tabelle e altre widget mantengono la logica auto-fit preesistente.

**Test:** `apps/web/test/rc306-long-bar-labels.test.ts` include regressioni sul contratto CSS e sul rendering; `tools/ci_rc306_bar_wrap_chromium.py` misura in Chromium il numero reale di righe di una risposta lunga, la dimensione del font, l'assenza di overflow orizzontale e la larghezza delle barre a 420 e 740 px, usando lo stylesheet originale. La prova è inserita nella full CI, prima del test Chromium dell'editor.

**Stato:** nessuna promozione dei 17 gate esterni mancanti; completamento ufficiale invariato a 85,25% prima della verifica CI. La pubblicazione Docker app+converter multiarch AMD64/ARM64 avviene solo dopo full CI verde e commit `[publish-docker]`.
