# RC206 — Note di sviluppo e validazione

## Modifiche funzionali

- Ctrl/Cmd+clic per selezionare/deselezionare più miniature, clic normale per selezione singola. Scorciatoie D (duplica), R (rinomina), Backspace (elimina dopo conferma). Sono attive soltanto con focus sulle miniature/menu, non nei campi editabili o sui widget. Le duplicazioni sono inserite dopo ciascun originale e sono ordinate secondo il server.
- Il menu delle miniature viene collocato in `document.body` e limitato allo schermo, con scorrimento interno, per non perdere «Elimina pagina».
- Le pagine escluse dallo schermo del presentatore non consumano un numero nel footer; lo stesso numero del presentatore viene inviato anche alle pagine indipendenti del pubblico (HTTP/WebSocket). Sono preservati i riferimenti originali tra pagine.
- Etichette delle risposte singole, multiple e sottodomande fino a 255 caratteri, controllate nel client e dal validatore API. Nelle barre dei risultati, etichette multilinea, spaziatura verticale e conteggi più visibili.
- Gestione degli sfondi personali nella voce del menu contestuale canvas (anche editor schemi): rinomina, eliminazione protetta. La cancellazione verifica proprietà e utilizzi (anche copie legacy di checksum uguale), blocca le immagini utilizzate con `409 background_in_use`; gli asset restano privati per sessione.

## Sicurezza e compatibilità

Il server ricontrolla autenticazione, proprietà della libreria e riferimenti alle immagini prima di eliminare. I modelli dati sono aggiornati tramite ALTER TABLE idempotenti; l'API di accesso partecipante non divulga i metadati delle immagini, ma soltanto il numero corrente del presentatore. Il comportamento del menu è deliberatamente confinato all'editor, senza intercettare tasti mentre l'utente scrive.

## Verifiche e limiti

Preflight `tools.tests.test_rc206_page_selection_and_library`; test Node `apps/web/test/rc206-page-thumbnail-selection.test.ts` e `apps/api/test/independent-widget-answers.test.ts`; regressioni RC200/RC203/RC204/RC205; controlli sintattici TS globali. La build rigorosa React/TypeScript, il collaudo browser visivo e la full CI GitHub rimangono obbligatori. La coerenza tipografica generale editor/preview introdotta in RC205 va ancora validata nell'interfaccia reale.

Ultima full CI verificata RC203, run 42110429701. Progress 85,25% (43 accettati / 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag.
