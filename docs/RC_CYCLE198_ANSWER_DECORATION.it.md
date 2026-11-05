# RC198 — Sottolineato e barrato coerenti delle risposte

**Versione:** Quorivio `0.1.0-dev` (invariata)  
**Base:** cumulativo RC197, committato dall'utente il 5 novembre 2026 (`0794f02`; GitHub Actions #298 avviata).  
**Ambito:** formattazione rich-text dei widget domanda, quiz temporizzati e domande con sottodomande.

## Difetto risolto

Il menu «Formato widget» distingueva correttamente font, dimensione, colore, grassetto e corsivo delle risposte, ma «Sottolineato» e «Barrato», quando applicati alle **Risposte**, venivano invece scritti nello stile del **titolo**: il risultato non appariva su opzioni e sottodomande. Anche «Widget intero» non propagava gli attributi agli elementi privi di marcature rich-text.

## Modifiche

- Aggiunte proprietà opzionali `answerUnderline` e `answerStrikethrough` al contratto dati dell'API. I valori sono booleani, con validazione rigorosa; i vecchi progetti senza queste proprietà rimangono validi. Nessuna migrazione di database.
- `answerOptionStyle` applica `underline`, `line-through`, entrambi o `none` ai testi delle risposte, compresi i campi di risposta e i widget di anteprima/proiezione che riusano lo stesso stile.
- «Widget intero» trasmette questi attributi alle risposte e alle marcature interne, anche delle sottodomande; «Risposte» cambia solo le due proprietà dedicate, senza modificare involontariamente il titolo.
- Aggiunti pulsanti espliciti «Sottolineato risposte» e «Barrato risposte» nella palette e controlli corrispondenti nella proprietà della widget, con stato accessibile `aria-pressed`.

## Verifiche e limiti

- Node API **605/605** e Node frontend **348/348**: verdi, compresi **5 nuovi test** di serializzazione, validazione fail-closed, legacy compatibility, stile applicato e isolamento degli ambiti.
- TypeScript/Vite *non eseguibili completamente offline* in questa sessione perché mancano `node_modules` e `vite/client`. Non attribuire esito positivo al typecheck completo.
- Restano da validare nel prossimo commit la build React/TypeScript, i test browser compilati, PostgreSQL e l'intera GitHub CI. Il risultato della CI #298 riguarda RC197, non il presente cumulativo.

**Governance:** completamento **85,25%** certificato, **43 accettati, 17 parziali**, nessun avanzamento arbitrario. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag, deploy né pubblicazione eseguita dall'assistente.
