# RC124 — Guide magnetiche e griglia assoluta nell’editor (2 novembre 2026)

**Macroarea:** precisione del canvas 16:9, sia pagine sia schemi. Le nuove guide mostrano temporaneamente l’allineamento ai bordi e al centro di altri widget, nonché al centro della diapositiva. Sono elementi puramente grafici (non vengono salvati), spariscono al rilascio/annullamento del gesto e non intercettano eventi del puntatore. Le collisioni rimangono rifiutate; forme e linee conservano le sovrapposizioni consentite.

**Correzione funzionale:** «Aggancia alla griglia (5%)» prima arrotondava il *delta* del trascinamento, non la posizione finale. Ora la griglia è visualizzata e lo spostamento singolo o multiplo usa la posizione assoluta del riquadro selezionato; le proporzioni e le distanze relative del gruppo rimangono invariate. La modalità griglia prevale sulle guide magnetiche, evitando spostamenti fuori griglia. Sono inclusi test ai limiti della pagina e con coordinate malformate.

**Evidenze locali:** 13 test Node di posizionamento/guide, 4 contratti Python e prova Chromium dei CSS di produzione a 1440 e 390 px. La build React integrata e la campagna GitHub restano obbligatorie; non dichiarare un test completo del trascinamento React basandosi sulla prova CSS isolata.

**Avanzamento:** certificato **85,25%**, 43 gate accettati e 17 parziali su 60; **85,75% progresso tecnico locale proposto**, cioè +0,50 punti subordinati all’accettazione del sotto-gate tecnico A1-SMART-GUIDES ricavato dal peso parziale di A1. Non è una certificazione né una promozione del ledger. I controlli indipendenti su touch fisico, accessibilità e confronto visivo restano aperti.

**Baseline:** RC122, commit `a97b80b8d09ebd1a6054111bf88326581e2cc80f`, tutti gli 11 gate automatici riusciti nella run `41350047731`, run complessiva `cancelled` per pubblicazione Docker rimasta in esecuzione. RC123 ancora non committata come esplicitamente indicato dal maintainer. RC124 cumulativa da RC123; nessun commit, push o pubblicazione effettuati dall’assistente.

**Commit suggerito RC123–RC124:** `Unify safe editor image uploads, bound Docker publication, and add PowerPoint-like alignment guides with absolute grid snapping [full-ci]`.
