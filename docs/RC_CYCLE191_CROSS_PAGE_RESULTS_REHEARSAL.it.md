# Quorivio 0.1.0-dev — RC191: risultati live tra pagine e anteprime indipendenti

**Baseline pubblicata:** RC190, commit `bb80a3ce28cafa437da4903fef3fb84a4fc54b25`; campagna automatica GitHub Actions verde `42027634427`, pubblicazione multiarchitettura Docker Hub riuscita nella run `42032833536` (`sha-bb80a3ce28ca`, `latest`). Nessuna modifica alla versione `0.1.0-dev`.

## Anomalie corrette

1. **Widget Risultati con sorgente in un'altra pagina.** L'anteprima utilizzava `linkedStatisticSource(widget,widgets)` soltanto sulla pagina che contiene i risultati e non consultava `targetActivityId`. Per questo presentava un risultato vuoto o un invito a selezionare un widget locale anche con un collegamento valido. RC191 introduce `linkedStatisticContext()`, usato dalle viste di anteprima e dalla proiezione reale, che risolve all'interno della stessa sessione l'attività, il widget, le opzioni e la modalità grafico della pagina sorgente.
2. **Risultati live apparentemente bloccati durante votazioni rapide.** Il `PresenterLinkedResult` dipendeva da `liveRevision={snapshot}`: ogni snapshot WebSocket sostituiva l'oggetto e cancellava la richiesta HTTP autenticata in corso. RC191 non usa lo snapshot come dipendenza dell'effetto: consulta immediatamente la sorgente e la aggiorna ogni tre secondi. Un eventuale errore di accesso dati è segnalato, senza mascherarlo con un falso grafico a zero. Se non ci sono risposte il messaggio è distinto: «Nessuna risposta ancora registrata».
3. **Anteprime affiancate incoerenti con esclusioni e pagina del pubblico.** La prova usava un unico `activity=activities[page]` per entrambe le viste. Ora il percorso di navigazione include esclusivamente `presenterVisiblePages`. Ogni pagina visibile al presentatore individua la propria `audiencePageId` (eventualmente nascosta al presentatore): il pannello presentatore usa layout/widget/numero di pagina della prima, il pannello partecipante usa quelli della seconda; lo smartphone applica la geometria e lo sfondo propri della pagina del pubblico. Aprendo la prova da una pagina nascosta si parte dalla sua pagina presentatore collegata, se presente. Le scadenze del pubblico non si azzerano cambiando pagina del presentatore a pubblico invariato.

## Esempio funzionale

- Pagina **A**: domanda interattiva, esclusa dallo schermo del presentatore.
- Pagina **B**: una widget Risultati con `targetActivityId=A` e `targetWidgetId=<ID della domanda>`; proprietà `audiencePageId=A`.
- Anteprima «Affiancate»: **B** sullo schermo del presentatore, **A** su quello dei partecipanti. Se si invia una risposta simulata dalla pagina A, la statistica simulata della pagina B cambia. In produzione la pagina B legge gli aggregati autentici della domanda A attraverso endpoint riservati ai presentatori.
- Con «Successiva» si raggiunge soltanto la prossima pagina **visibile al presentatore**; non la A esclusa.

## Verifiche e limiti

- Node `apps/web/test/*.test.ts`: **326 test superati**. Node `apps/api/test/*.test.ts`: **599 test superati**.
- Suite Python di regressione storica aggiornata: **30 test superati**; nuovi test RC191 **6 superati**.
- Compilazione rigorosa dei moduli di routing e risultati: `tsc --noEmit --strict ...` superata. L'analisi sintattica di `main.tsx` non ha restituito errori di parsing; la compilazione completa React/Vite richiede le dipendenze npm e va certificata nella CI successiva.
- Aggiunti un test Node e un preflight Python anticipato in GitHub Actions, senza indebolire i gate storici, le API di autorizzazione o la protezione dei risultati dei partecipanti.
- La campagna CI GitHub successiva al commit RC191, la verifica PostgreSQL con due pagine e il confronto visivo browser reale **restano da eseguire**. Completamento certificato **85,25%**, 43 gate accettati / 17 parziali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o publish automatico da parte dell'assistente.
