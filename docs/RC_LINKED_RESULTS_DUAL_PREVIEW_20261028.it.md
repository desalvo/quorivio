# Quorivio — risultati collegati e prove affiancate (28/10/2026)

## Batch RC 28/10/2026 — risultati collegati, anteprime interattive affiancate e palette

**Versione:** 0.1.0-dev invariata. Ultima Full CI GitHub verificata: 40595463258 sul commit e2dc3a97bd15d82a50c23a98b1fb83c2bd1841c9 (precedente al presente ciclo). **Questo ciclo: solo test locali, nuova Full CI da eseguire. Completamento globale RC 53,0% invariato, gate A1–A4 ancora parziali.**

Implementato:
- Ogni widget Risultati viene mostrato soltanto al presentatore ed è collegabile dal pannello proprietà a un widget statistico della stessa pagina (domanda, quiz a tempo, gradimento, reazioni) mediante `targetWidgetId`. Il backend rifiuta target inesistenti, autoreferenze, widget non statistici e riferimenti esterni alla pagina. I widget legacy privi di collegamento restano caricabili ma richiedono configurazione.
- Nella proiezione reale del presentatore i grafici interrogano gli endpoint autenticati e specifici della sorgente; nel preview si usano dati fittizi generati all'avvio, mai scritti nel database. Le statistiche delle domande sul tema non sono ancora collegate a un aggregato reale e rimangono aperte.
- Anteprime presentatore, partecipante e simultanee affiancate accessibili sia dalla dashboard sia dall'editor, con canvas 16:9, contenuto della bozza corrente (anche non salvata), schermo intero e stato di prova condiviso. I risultati sono assenti dalla vista partecipante; le reazioni funzionano nella prova, senza richieste di scrittura.
- Duplicando insieme domanda e risultati, i duplicati mantengono un collegamento tra loro; i collegamenti verso widget rimossi sono svuotati. Palette rettangolare ad angoli arrotondati con font face, font size, colore e formattazione del testo selezionato; corretto il focus quando si passa dall'editing alla palette.

**Test locali:** build TypeScript backend e frontend/Vite PASS; **455/455 Node backend, 44/44 Node frontend e 58/58 Python mirati PASS**; Chromium offline geometria 16:9 e puntatore delle reazioni su 1440 e 390 px PASS. Il browser con app autenticata su localhost è bloccato da `net::ERR_BLOCKED_BY_ADMINISTRATOR`; NON è un test end-to-end superato. Suite Python generale interrotta per timeout; NON superata. CI GitHub e PostgreSQL 18 sul nuovo batch NON ancora verificati. Inserita la nuova prova offline nella Full CI opt-in.

**Da chiudere:** prove browser end-to-end PostgreSQL su sessioni reali, confronto visivo di tutti i widget, Firefox/WebKit e dispositivi fisici, accessibilità assistiva, WYSIWYG durante digitazione, più domande indipendenti in un widget, risultati live per domande sul tema. Nessun commit/push/tag/release o pubblicazione Docker automatica.

Report: `docs/RC_LINKED_RESULTS_DUAL_PREVIEW_20261028.it.md`.
