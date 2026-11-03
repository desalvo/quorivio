# RC151 — Controlli negativi TypeScript robusti (3 novembre 2026)

La run GitHub Actions [41706075530](https://github.com/desalvo/quorivio/actions/runs/41706075530) si è fermata nel preflight storico RC115, `test_negative_mutations_reject_original_compiler_errors`, prima di installare le dipendenze. La mutazione di prova cercava una stringa letterale del vecchio `Pick` che terminava in `resultsOnly`. RC150 ha correttamente aggiunto `position` e `resultTopCount`, quindi la sostituzione non modificava il codice, provocando un falso errore.

Il controllo RC115 ora interpreta l'unione reale del `Pick`, rimuove ciascun campo necessario separatamente e verifica che la mutazione abbia effettivamente modificato la sorgente. I nuovi test RC151 controllano l'estensibilità, i campi obbligatori `showTitle` e `autoFit`, il dominio condiviso e la permanenza del controllo `tsc --noEmit && vite build`. Nessuna modifica funzionale a runtime, widget o editor. Inventario storico RC150 invariato; RC151 diventa l'inventario corrente riproducibile in checkout Git pulito.

**Completamento certificato invariato: 85,25% (43 accettati / 17 parziali)**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Le prove locali non sostituiscono la CI completa o le accettazioni browser; nessun commit, push o rilascio effettuato dall'assistente.
