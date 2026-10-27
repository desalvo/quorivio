# Quorivio — Ispettore widget, rinomina pagine e anteprima partecipante (27 ottobre 2026)

**Baseline committata:** `67a7be939a5930e2f9a49ce3932a4b7f29a682ac`, Full CI 40553571012 verde. Il cumulativo corrente è **non committato** e include anche recupero dell'autosalvataggio e geometria condivisa del ciclo avviato in precedenza.

## Sviluppi

- Tooltip dei widget in un livello flottante esterno alla sidebar: niente tagli e niente messaggio doppio su mobile.
- Unico pannello proprietà nell'editor integrato, con pulsante X accessibile, eliminando il pannello ridondante. Anche le impostazioni della pagina hanno una X.
- Configurazione completa delle scelte per domande e quiz temporizzati: didascalie «Opzione N», scelta singola/multipla, aggiunta/rimozione (fino a 12), risposta corretta, durata. Opzioni visualizzate nel canvas e nella proiezione, con checkbox/radio **a sinistra** del testo.
- Recupero dell'autosalvataggio dopo risposte di rete interrotte e geometria percentuale condivisa tra editor, proiezione e partecipante, con test.
- Endpoint dedicato `PATCH /api/sessions/:id/pages/:aid/title`: autorizzazione, validazione, blocco sessioni chiuse, revisione metadati e broadcast. Non modifica opzioni, voti, revisione del layout o allegati. Comando «Rinomina pagina» nel menu della miniatura e nel menu contestuale del canvas vuoto; preserva la bozza in memoria.
- Anteprima partecipante: rimossi titolo e numero duplicati e la linguetta/barra viola laterale. Navigazione simulata consentita **solo nel piè di pagina dell'anteprima**. La vista reale segue solo la pagina attiva del presentatore e non duplica il titolo quando i widget lo disegnano.
- Cinque regressioni e un test Chromium/PostgreSQL di rinomina dal menu con verifica del titolo, opzioni, revisione layout e coordinate.

## Evidenze e limiti

- Locali: **851/851 Python** e **447/447 Node** PASS; parsing TypeScript JSX/backend e sintassi test browser PASS.
- Nuova Full CI PostgreSQL/Chromium, build React/Vite, verifica su browser e dispositivo reale: **da eseguire**. Non dichiarare completata l'accettazione visiva e di accessibilità.
- Matrice RC **53,0% invariata**, `release_candidate_ready=false`. Avanzamenti futuri richiedono evidenze verificabili.
- Commit, push, tag e pubblicazione Docker non effettuati; publishing sempre opt-in.
