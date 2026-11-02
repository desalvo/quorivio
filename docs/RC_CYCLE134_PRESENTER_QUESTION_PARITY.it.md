# RC134 — Uniformità delle domande nello schermo presentatore

2 novembre 2026. **Ultima baseline committata con CI verde:** RC130, workflow `41420021082`, commit `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d`. **Cumulativo non committato:** RC131–RC134. Nessun commit, push, tag o rilascio eseguito.

## Interventi funzionali

- **Proiezione presentatore reale:** sostituita l'etichetta errata «Risposta testuale» con la vera casella di risposta non interattiva, della dimensione configurata, e il pulsante **Invia risposta** disabilitato. Funziona anche per domande indipendenti e quiz; per risposte a scelta vengono visualizzati radio/checkbox disabilitati e formattati come le opzioni dell'autore. Gli allegati mostrano un segnaposto senza input attivi e il pulsante disabilitato.
- **Domande sul tema:** sullo schermo presentatore appaiono casella per il testo e pulsante **Invia domanda** disabilitati, anziché testo segnaposto estraneo. Le risposte effettive e le statistiche rimangono separate nei widget autorizzati.
- **Anteprima presentatore:** riutilizza lo stesso componente per le domande sul tema, evitando una seconda casella duplicata. La prova partecipante rimane simulata e interattiva.
- **CSS e proporzioni:** unificati inset, tipografia dei titoli, opzioni di scelta, dimensioni dei radio/checkbox, formati del campo e del tasto fra proiezione e anteprima. Sulla prova presentatore in 16:9 è eliminato il vecchio minimo mobile di 100 px solamente per i controlli disabilitati; i veri input partecipante mantengono le dimensioni accessibili.
- **Sicurezza e privacy:** nessuna risposta esposta sullo schermo presentatore, nessun invio o focus possibile dai controlli disabilitati. Invariati i gate Docker, GDPR, i privilegi e le regole di salvataggio.

## Verifiche e limiti

- Preflight RC134 e test storici di proiezione/domande: PASS locale.
- Chromium reale con fixture sintetica CSS: PASS a 1440 e 390 px, con controllo geometria, tipografia, stato disabilitato e tasti.
- Suite frontend Node: 209/209 PASS; parser TSX globale: 0 errori sintattici.
- Build npm/Vite completa **non verificata**: `npm ci --offline` si interrompe perché manca `yargs-parser` nella cache. Serve CI GitHub completa, incluso il collaudo autenticato con PostgreSQL e controllo visivo operativo.

**Completamento certificato invariato:** 85,25%, 43 gate accettati e 17 parziali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
