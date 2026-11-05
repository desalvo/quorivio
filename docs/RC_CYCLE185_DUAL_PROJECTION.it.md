# RC185 — Pagine live indipendenti per presentatore e partecipanti, risultati tra pagine

## Baseline

La RC184 ha ottenuto CI verde in GitHub Actions [41993094578](https://github.com/desalvo/quorivio/actions/runs/41993094578), commit `45f76e57b4c9e7a2acd3687893040d2d6d6658e6`: 14 job superati e 3 job di pubblicazione volutamente saltati. Questa rimane la baseline verificata. Nessun commit, push, tag o rilascio da parte dell'assistente.

## Funzionalità implementate

- **Due pagine live distinte**: `current_activity_id` continua a indicare esclusivamente la pagina aperta al pubblico; il nuovo `presenter_activity_id` identifica la pagina proiettata sullo schermo del presentatore. La snapshot del pubblico contiene soltanto la pagina a lui destinata. Le vecchie sessioni mantengono il comportamento predefinito, con la stessa pagina su entrambi gli schermi.
- **Menu contestuale del canvas**: per ogni pagina si può selezionare quale pagina vedranno i partecipanti mentre il presentatore proietta quella corrente. Si può anche impostare «Salta sullo schermo presentatore»: la pagina sarà esclusa dalle frecce e dalla sequenza del presentatore, ma rimarrà utilizzabile dai partecipanti e come sorgente dei risultati. Gli stessi controlli sono in «Impostazioni pagina e risultati».
- **Navigazione atomica**: la route autenticata controlla le revisioni concorrenti e verifica le destinazioni all'interno della stessa sessione. Cambia i due puntatori in un'unica transazione PostgreSQL, mantenendo **una sola pagina aperta alle risposte**. Se la pagina del pubblico resta la stessa attraverso più slide dei risultati, non viene reimpostata inutilmente l'ora di apertura.
- **Widget Risultati tra pagine**: nelle proprietà si scelgono pagina sorgente, widget sorgente ed eventuale singola domanda. Lo schermo del presentatore usa gli endpoint autenticati e l'ID della pagina sorgente per statistiche e risposte in tempo reale: quiz, testo libero, gradimento, reazioni, domande sul tema e quiz a tempo.
- **Salvataggio**: le proprietà entrano nell'autosalvataggio, nelle bozze JSON, nel merge collaborativo e nelle verifiche server. La cancellazione di una pagina ancora referenziata da un'altra viene bloccata con errore esplicito.
- **Portabilità**: import/export .quorivio rimappano gli ID delle pagine e i riferimenti dei widget; non è possibile importare involontariamente riferimenti alla sessione originale.

## Caso d'uso

1. Pagina A: contiene il widget «Domanda» Q; selezionare «Salta sullo schermo presentatore».
2. Pagina B: contiene la widget «Risultati» che fa riferimento alla pagina A e al widget Q. Sul canvas B impostare «Pagina partecipanti = A».
3. Durante la proiezione, il presentatore vede B e le statistiche live; i partecipanti vedono A, rispondono e votano. Le frecce del presentatore saltano A, senza eliminarla dal percorso del pubblico.

## Sicurezza e verifiche

Il salvataggio dei riferimenti e la cancellazione delle pagine usano un lock di sessione ordinato per evitare collegamenti orfani in caso di modifiche concorrenti. Le risposte da pagine differenti sono consultabili solo dal presentatore autenticato. Gli accessi dei partecipanti continuano a essere vincolati alla pagina pubblica effettivamente attiva; gli ID di destinazione sono verificati sul server e non affidati al client. I nuovi test coprono compatibilità precedente, instradamento, risultati, import/export, concorrenza e privacy; sono inseriti fra i controlli iniziali della CI.

La build Vite, i test reali React/PostgreSQL di doppia proiezione e la nuova campagna GitHub richiedono ancora il commit e la CI: **non sono dichiarati superati**. Completamento certificato immutato: **85,25% (43 gate accettati, 17 parziali)**. Pubblicazione e strict gate restano disabilitati fino alle verifiche indipendenti.
