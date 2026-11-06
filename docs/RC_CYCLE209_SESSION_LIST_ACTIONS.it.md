# RC209 — Gestione delle sessioni direttamente da «Apri sessione»

Versione prodotto invariata: `0.1.0-dev`.

## Funzionalità

Nella lista autenticata «Apri sessione», il proprietario primario può ora:

- riportare le sessioni **avviate, in pausa o terminate** a **non avviata**, senza aprire la dashboard;
- cancellare definitivamente una sessione, indipendentemente dallo stato.

Le due operazioni sono distinte: il reset cancella in modo irreversibile partecipanti, risposte, voti, statistiche e allegati privati degli utenti; conserva pagine, widget, materiali della presentazione e impostazioni. Rigenera URL/codice pubblico e ristabilisce una scadenza di almeno 24 ore, anche se la sessione era terminata. La cancellazione elimina tutta la sessione e i materiali collegati tramite il percorso di pulizia già esistente.

Solo i proprietari visualizzano i pulsanti: l'autorizzazione è **ricontrollata sul server**, non fidata dalla sola UI. Entrambe le operazioni richiedono un dialogo di conferma che nomina la sessione e descrive la perdita dei dati. Durante l'operazione i pulsanti nella lista vengono disabilitati contro doppio invio; dopo il successo l'elenco si aggiorna e, se necessario, torna alla pagina precedente. Se il browser conserva un riferimento alla sessione rimossa, viene eliminato **solo il riferimento di navigazione**, non i cookie di autenticazione. Gli errori preservano l'elenco e vengono mostrati all'utente.

## Validazione

- Suite Node API: **616/616**, frontend: **368/368**.
- Nuovi test Node RC209: **4/4**; Python preflight RC209: **4/4**; regressioni RC71/RC208/RC209: **18/18**.
- Il test di integrazione PostgreSQL `ci_rc71_lifecycle_postgres.py` è stato esteso per verificare anche il ripristino da `closed`, conservazione delle pagine, rigenerazione del codice e rifiuto del reset da `ready`. Il suo passaggio in GitHub CI è **da verificare**.
- Full build React/TypeScript e full CI della RC209 **non ancora certificati**. Ultima full CI interamente verde verificata: RC203, run `42110429701`.
- Completamento certificato invariato: **85,25%** (43 gate accettati, 17 parziali).

`rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag dell'assistente.
