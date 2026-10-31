# RC69 — Riconciliazione dell'esportazione JSON e recupero autorevole del riordino

**Baseline committata:** `487c960f09b3c9adb996d489f44b52d059da12b2`, CI standard `41191213305`, campagna estesa `41191751069`. RC66–RC69 non sono ancora dichiarati committati. L'assistente non esegue commit, push o pubblicazioni.

## Credito con evidenza (+0,50 punti percentuali)

Il job qualità della CI verde `124509777927` ha eseguito `tools/ci_browser_editor.py` sulla **app React di produzione compilata in Chromium reale**. Dalla miniatura di una pagina il presentatore ha aperto il menu, scelto **Esporta layout JSON**, atteso un vero download del browser e verificato l'esistenza del file. L'esportazione della singola pagina non è il riordino di A2-ORDER né l'autosave/CAS di A3-AUTO. Non è una verifica di roundtrip JSON completo.

Il gate A2 parziale scende da peso 4 a 3, il nuovo gate accettato `A2-PAGE-JSON` pesa 1. Peso totale 100, punteggio **84,75%** (42 gate accettati, 17 parziali su 59). È una riconciliazione di prove **già superate in GitHub**, non un credito per i nuovi cambiamenti.

## Nuovo codice (non ancora certificato dalla CI)

- Il riordino rilegge sempre l'ordine autorevole dopo la PUT, anche in caso di errore di trasporto. Non ritenta una scrittura potenzialmente già committata e non dichiara che l'ordine precedente sia conservato.
- UI con esito distinto per scrittura confermata, scrittura recuperata, rifiuto e modifica concorrente. Se fallisce anche la GET, segnala che l'esito è incerto e chiede il ricaricamento.
- Nuovi test Node per errore dopo COMMIT, rifiuto, concorrenza, mancata lettura e variazioni dell'insieme delle pagine.
- Nuovo test Playwright sull'**app React compilata**, in Chromium, Firefox e WebKit alle larghezze 1440/390px: trascinamento nativo, errore dopo commit, rifiuto 409 e riordino accessibile con Alt+FrecciaSu. La rete è simulata in memoria e non coinvolge dati reali.

**La nuova prova browser è in attesa della prossima CI standard ed estesa.** Localmente npm non può scaricare le dipendenze per mancanza di risoluzione DNS: la build TypeScript/Vite non è considerata verificata. Nessuna attestazione di touchscreen fisico, lettori di schermo, fedeltà visiva indipendente o drag/drop nativo già accettato. Pubblicazione e RC strict disabilitate.
