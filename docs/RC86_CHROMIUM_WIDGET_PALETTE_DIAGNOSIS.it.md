# RC86 — Correzione test Chromium palette

Fonte: `logs_111780102568(1).zip`, Production quality gate / Chromium editor UI acceptance. `tools/ci_browser_editor.py:273` falliva dopo la verifica del menu widget perché richiedeva esattamente 17 bottoni. La palette corrente include 19 tipi, inclusi `title` e `footer`. Nessun tipo di widget è stato rimosso.

RC86 sostituisce il conteggio fisso con i seguenti contratti eseguiti in Chromium: presenza dei 19 tipi noti, `data-widget-kind` unici, etichette aria non vuote/uniche, SVG con classi distinte e nessun tooltip HTML `title`. L'inserimento testo, l'autosave e il reload restano obbligatori. Quattro test Python di regressione vengono eseguiti prima dell'installazione delle dipendenze.

Il risultato della CI estesa RC86 non è ancora disponibile; progressione RC invariata a 84,75%. Non si pubblicano immagini e non si abilita RC strict.
