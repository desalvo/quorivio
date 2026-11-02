# RC132 — Collisioni coerenti tra tastiera e puntatore e ridimensionamento accessibile delle risposte

2 novembre 2026. Baseline confermata: RC130 committata, CI GitHub `41420021082` verde. RC131 e RC132 sono modifiche **cumulative non ancora committate**; la CI GitHub per queste modifiche non è ancora stata eseguita.

## Implementato

1. **Geometria da tastiera:** lo spostamento di una singola widget e la traslazione di una selezione multipla utilizzano lo stesso algoritmo continuo di primo contatto del trascinamento RC131. Il movimento si ferma al primo ostacolo non grafico, senza attraversarlo o tornare all'origine. Si conservano distanze relative del gruppo, limiti del canvas e sovrapposizioni intenzionali di forme e linee. Rotazione e ridimensionamento della widget mantengono i controlli separati già esistenti.
2. **Risposta a testo libero:** la maniglia di altezza è ora uno slider verticale accessibile, con valori minimo/massimo/attuale (48–400 pixel logici), focus visibile e comandi FrecciaSu/Giù (8 px), Maiusc+Freccia (32 px), PagSu/PagGiù (32 px), Inizio/Fine. La stessa maniglia è ora disponibile tanto per le risposte a testo libero quanto per le domande aperte dei partecipanti (prima con anteprima fissa). Rimane il trascinamento touch/mouse. La maniglia non avvia lo spostamento della widget e ogni modifica da tastiera attraversa il normale salvataggio e lo storico Undo/Redo. Nessun cambiamento ai dati delle risposte.
3. **Regressioni:** dieci nuovi test Node verificano ostacoli sottili, selezioni rigide, forme, bordi, dati non validi, altezza tastiera e annullamento. Aggiunti controllo Python anticipato e passo CI dedicato. Non sono stati indeboliti gate di rilascio o autorizzazioni di pubblicazione.

## Verifiche e limite della certificazione

Suite Node frontend locale: 202/202 test superati. Test Python mirati: 27/27 superati; la suite generale non è terminata entro il limite locale durante la fase convertitore. Inventario sorgente verificato; integrità ZIP verificata separatamente. La compilazione TypeScript/Vite, la prova browser su applicazione reale e la CI GitHub richiedono un nuovo commit del manutentore.

**Completamento certificato invariato: 85,25%** (43 gate accettati, 17 parziali su 60). Restano collaudi mobili fisici e tecnologie assistive, provider esterni, CSI/DR indipendenti e approvazioni di sicurezza/GDPR. Il gate rigoroso non viene promosso. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
