# RC105 — finestre mobili e resize sul canvas

Baseline: RC104 cumulativa non ancora committata; RC102 e full CI 41265300884 confermate. Versione applicazione 0.1.0-dev.

## Correzioni

- Gli otto ancoraggi e l'ancoraggio di rotazione vengono posizionati assolutamente rispetto al **border box** del singolo widget. Il vecchio tema artistico imponeva `position:relative` ai figli: sovrascriveva la geometria degli ancoraggi.
- Ancoraggi e controlli di rimozione sono nascosti sui widget non selezionati; si visualizzano solo quando `data-selected=true`. Gli ancoraggi rimangono utilizzabili con puntatore e touch.
- Palette PowerPoint: ora è una finestra con `position:fixed` portata fuori dal flusso del canvas con un React portal. Non occupa righe della griglia, non sposta né ridimensiona la diapositiva; scroll interno per viewport stretti.
- Pannello Proprietà widget e Impostazioni pagina: finestre flottanti trascinabili dal titolo; i campi rimangono interattivi e non avviano il trascinamento. Le coordinate sono vincolate al viewport e adattate al resize.
- Il clic sui pulsanti della palette continua a preservare la selezione del testo, mentre i gesti di trascinamento iniziano solo dalla sua intestazione.

## Evidenze e limiti

- `tools/ci_editor_floating_layout_chromium.py`: test del CSS effettivo in Chromium desktop 1440×900 e mobile 390×844; controlla visibilità, posizionamento degli otto bordi, tema artistico e invarianza della geometria del canvas all'apertura della palette.
- `tools/tests/test_rc105_editor_floating.py`: contratti sorgente relativi a drag dalla barra titolo, portal, selezione e posizione.
- La build completa React, il trascinamento reale con interazioni complete dell'app e i test di regressione GitHub sono **da confermare con `[full-ci]`**.
- Non è attestata un'accettazione indipendente su dispositivi fisici né sono stati promossi gate RC. Completamento certificato invariato: 85,25% (43 accettati, 17 parziali).
