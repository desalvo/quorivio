# RC222 — Formato widget compatto e opzioni di risposta corrette (2026-11-06)

## Funzionalità
- La finestra **Formato widget** è stata compattata nell’intestazione e nei controlli; eliminati i grandi spazi minimi ereditati dalle regole CSS delle finestre precedenti. Le intestazioni visuali ridondanti sono nascoste ma le sezioni mantengono i nomi accessibili.
- Su schermi stretti tutti i gruppi di comandi restano raggiungibili mediante scorrimento orizzontale e tastiera; nessuna funzionalità viene soppressa. Per le widget risultati, i numerosi formati dei singoli elementi sono racchiusi in **Testi indipendenti…**, apribile su richiesta.
- L’editor delle domande a scelta singola/multipla mostra l’intero testo delle opzioni su più righe, anche per sottodomande e contenuti rich-text. Le anteprime e la proiezione non sono state alterate.
- Il font iniziale delle risposte è **Arial**, e «Widget intero» applica un nuovo font a opzioni, pulsante e titolo, anche con precedenti formati rich-text. Rimane possibile formattare singole porzioni di testo selezionate.

## Implementazione
- `apps/web/src/main.tsx`: normalizzazione della tipografia opzioni con `widgetTextDefaults`, applicazione esplicita della formattazione totale, pannello avanzato di risultati espandibile.
- `apps/web/src/style.css`: regole specifiche sul glyph span per annullare `white-space:nowrap`, `overflow:hidden`, `text-overflow:ellipsis` legacy soltanto nell’editor; barra compatta e swipe smartphone.
- `tools/ci_rc222_format_widget_chromium.py`: prova CSS reale in Chromium 1440/390 px (in una fixture statica con DOM editor); controlla a capo, Arial, override Georgia, presenza del testo integrale e altezza del pannello. Non sostituisce una prova sull’intera applicazione compilata.
- Test di regressione API/frontend e contratti Python anticipati nella CI. Nessuna modifica a schema dati o backend.

## Stato e limiti
- Baseline integrata verde: RC219, run `42197607753`. Nuove RC220/221/222 non ancora certificate in CI completa.
- Progresso certificato **85,25%**, 43 gate accettati / 17 parziali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
- Non eseguire commit/push/tag senza richiesta. Conservare tutte le precedenti ricevute SHA-256.
